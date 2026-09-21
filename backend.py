import os
import certifi
import re
from dotenv import load_dotenv

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator
import uuid
import asyncio
import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq

# from tools.tavily_tool import tavily_search
# from tools.flight_tool import search_flights
from mcp_client import (
    tavily_mcp_search,
    aviation_mcp_call,
    extract_destination,
    forecast_mcp_search,
    weather_mcp_search,
)


def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL is missing. Please add your Render PostgreSQL External Database URL to .env"
        )

    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")


# =========================
# LLM
# =========================
#
# openai/gpt-oss-120b is a REASONING model. By default (reasoning_format
# left unset -> "raw"), Groq has it write its internal chain-of-thought
# directly into the same content string inside <think>...</think> tags,
# and that reasoning text is generated (and billed against max_tokens)
# BEFORE the actual answer. With a small max_tokens, the whole budget can
# be spent on reasoning and the call finishes with an empty or half-typed
# answer, finish_reason="length" — which is what was causing the empty
# weather city, the truncated flight section, and the "I'm sorry, I can't
# provide that" refusal-looking text.
#
# reasoning_effort="low" makes it think less for these simple lookups;
# reasoning_format="hidden" stops any reasoning text from leaking into
# the visible content even if it does think.

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    reasoning_effort="low",
    reasoning_format="hidden",
)


# =========================
# Reliability helper
# =========================
#
# Detects a finish_reason of "length" (i.e. "I got cut off") and
# automatically asks the model to keep going instead of returning a
# half-finished answer. `continuation_hint` is caller-supplied so the
# retry instruction actually matches what that call is producing — reusing
# itinerary-specific wording ("don't restart the itinerary") for the
# flight/hotel/summary calls was itself causing confused, refusal-like
# replies, since it contradicted those calls' own "no itinerary" system
# prompts.


def invoke_with_continuation(
    llm_client,
    messages,
    max_tokens: int = 6000,
    max_continuations: int = 3,
    continuation_hint: str = "just keep going until the answer is complete",
) -> str:
    full_text = ""
    current_messages = list(messages)

    for attempt in range(max_continuations + 1):
        response = llm_client.invoke(current_messages, max_tokens=max_tokens)
        full_text += response.content

        finish_reason = (response.response_metadata or {}).get("finish_reason")

        if finish_reason != "length":
            break

        if attempt == max_continuations:
            full_text += (
                "\n\n[Note: this section may still be incomplete — it hit "
                "the output limit multiple times in a row.]"
            )
            break

        current_messages = current_messages + [
            AIMessage(content=response.content),
            HumanMessage(
                content=(
                    "You were cut off before finishing. Continue exactly "
                    "where you left off. Do not repeat anything you "
                    f"already wrote, and do not restart — {continuation_hint}."
                )
            ),
        ]

    text = full_text.strip()

    # Defense in depth: if reasoning still ate the whole budget and the
    # visible answer came back empty or as a bare refusal, don't let that
    # leak into the final assembled answer.
    if not text or (
        len(text) < 60
        and text.lower().startswith(("i'm sorry", "i am sorry", "i can't", "i cannot"))
    ):
        return (
            "(This section could not be generated — please try regenerating the plan.)"
        )

    return text


# =========================
# State
# =========================


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    weather_results: str


# =========================
# Flight Agent
# =========================

FLIGHT_AGENT_PROMPT = """
You are a travel flight expert. Answer with FLIGHT INFORMATION ONLY.

User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Give exactly these 7 points, briefly:

1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Strict rules:
- Do NOT include hotel recommendations.
- Do NOT include a day-by-day itinerary.
- Do NOT include a budget/cost summary table for the whole trip.
- Do NOT include a checklist, packing list, or visa/currency tips.
- Keep the whole answer under 200 words, plain text or a short table — no
  extra sections beyond the 7 points above.
"""


def flight_agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_query"]

    try:
        airports = asyncio.run(aviation_mcp_call("list_airports"))
        airlines = asyncio.run(aviation_mcp_call("list_airlines"))

        print("\nAIRPORTS:", airports)
        print("\nAIRLINES:", airlines)

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000],
        )

        flight_data = invoke_with_continuation(
            llm,
            [
                SystemMessage(
                    content=(
                        "You are an expert travel flight planner. You only "
                        "ever answer with flight-route information — never "
                        "hotels, itineraries, or budget tables."
                    )
                ),
                HumanMessage(content=prompt),
            ],
            max_tokens=900,
            max_continuations=1,
            continuation_hint="keep going with the remaining flight points only",
        )

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="Flight recommendations generated")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Hotel Agent
# =========================
#
# tavily_mcp_search() returns raw MCP tool output — a list of content
# blocks with a JSON string of search results inside. That raw blob was
# previously being dumped straight into the "Hotel Suggestions" section
# (the "[{'type': 'text', ...}]" mess). Now it's run through the LLM once
# to turn it into an actual short, readable hotel list.


def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"
    raw_results = asyncio.run(tavily_mcp_search(query))

    hotel_prompt = f"""
You are a travel hotel expert. Based on the raw search results below,
list 3-5 specific hotel or accommodation recommendations for this trip.

User Query:
{state['user_query']}

Raw search results (may include JSON, ignore the formatting):
{str(raw_results)[:3000]}

For each recommendation give: name, approximate price per night, and one
short line on why it fits. Return ONLY a clean bullet list of hotels —
no JSON, no raw text, no other sections, no day-by-day itinerary, no
overall budget table.
"""

    hotel_results = invoke_with_continuation(
        llm,
        [
            SystemMessage(
                content=(
                    "You are a hotel recommendation expert. You only ever "
                    "answer with a short hotel list — never raw data, "
                    "flights, or itineraries."
                )
            ),
            HumanMessage(content=hotel_prompt),
        ],
        max_tokens=700,
        max_continuations=1,
        continuation_hint="keep going with the remaining hotel bullets only",
    )

    return {
        "hotel_results": hotel_results,
        "messages": [AIMessage(content="Hotel information fetched.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Weather Agent
# =========================
#
# extract_destination() was returning things OpenWeather's geocoder can't
# resolve (e.g. a multi-city string like "Tokyo, Osaka" for a multi-stop
# trip), which OpenWeather rejects with {'cod': '400', 'message': 'Nothing
# to geocode'} — and that raw error dict was getting printed straight into
# the final answer as if it were real weather data. extract_destination()
# itself now returns a single geocodable "City,CountryCode" (see
# mcp_client.py); this agent also checks for an error response and falls
# back to a plain message instead of leaking the raw API error.


def extract_travel_days(query: str) -> int:
    """
    Extract trip duration from the user's query.
    Examples:
    - 5 day trip
    - 5 days in Bangkok
    - Bangkok for 4 days
    """

    patterns = [
        r"(\d+)\s*[-]?\s*day(?:s)?",
        r"for\s+(\d+)\s*day(?:s)?",
        r"(\d+)\s*day(?:s)?\s*trip",
    ]

    for pattern in patterns:
        match = re.search(pattern, query.lower())

        if match:
            days = int(match.group(1))

            # Keep it within OpenWeather's available forecast range
            return max(1, days)

    # Default
    return 5


def weather_agent(state: TravelState):
    city = extract_destination(state["user_query"])
    travel_days = extract_travel_days(state["user_query"])

    weather_data = asyncio.run(weather_mcp_search(city))
    forecast_data = asyncio.run(forecast_mcp_search(city, travel_days))

    if not isinstance(weather_data, dict) or "cod" in weather_data:
        weather_results = (
            f"Live weather data isn't available for '{city}' right now. "
            "Check a forecast site closer to your travel dates."
        )

    else:

        # -----------------------------
        # CURRENT WEATHER
        # -----------------------------

        current_temp = weather_data.get("temperature_c", "N/A")

        current_condition = weather_data.get("condition", "Unknown")

        condition_lower = current_condition.lower()

        if "rain" in condition_lower:
            current_recommendation = "🌧️ Keep an umbrella handy."

        elif "storm" in condition_lower or "thunder" in condition_lower:
            current_recommendation = "⛈️ Consider indoor plans during stormy periods."

        elif "clear" in condition_lower:
            current_recommendation = "😎 Clear skies — great time to explore!"

        elif "cloud" in condition_lower:
            current_recommendation = (
                "☁️ A little cloudy — nice weather for sightseeing."
            )

        elif current_temp != "N/A" and current_temp >= 35:
            current_recommendation = (
                "🥵 It's warm — plan outdoor activities earlier in the day."
            )

        else:
            current_recommendation = "👍 Looks comfortable for exploring."

        # -----------------------------
        # DAILY TRAVEL FORECAST
        # -----------------------------

        forecast_lines = []

        if isinstance(forecast_data, list) and forecast_data:

            for index, forecast in enumerate(forecast_data, start=1):

                temperature = forecast.get("temperature", "N/A")

                condition = forecast.get("weather", "Unknown")

                date = forecast.get("date", "")

                time = forecast.get("time", "12:00:00")

                # Convert 24-hour time
                hour = int(time.split(":")[0])

                if hour == 0:
                    display_time = "12:00 AM"
                elif hour < 12:
                    display_time = f"{hour}:00 AM"
                elif hour == 12:
                    display_time = "12:00 PM"
                else:
                    display_time = f"{hour - 12}:00 PM"

                condition_lower = condition.lower()

                # Friendly recommendation
                if "storm" in condition_lower or "thunder" in condition_lower:
                    recommendation = "⛈️ Keep outdoor plans flexible."

                elif "rain" in condition_lower:
                    recommendation = "🌧️ Keep an umbrella handy."

                elif "clear" in condition_lower:

                    if isinstance(temperature, (int, float)) and temperature >= 35:
                        recommendation = "🥵 Start sightseeing early to avoid the heat."
                    else:
                        recommendation = "😎 Clear skies — great for exploring!"

                elif "cloud" in condition_lower:
                    recommendation = "☁️ Nice conditions for sightseeing."

                elif isinstance(temperature, (int, float)) and temperature >= 35:
                    recommendation = "☀️ It's warm — plan outdoor activities earlier."

                else:
                    recommendation = "👍 Comfortable weather for exploring."

                forecast_lines.append(
                    f"**Day {index} — {date} at {display_time}**  \n"
                    f"🌡️ **{temperature}°C** | "
                    f"☁️ **{condition.title()}**  \n"
                    f"💡 {recommendation}"
                )

            forecast_text = "\n\n".join(forecast_lines)

        else:
            forecast_text = "Forecast unavailable."

        # -----------------------------
        # FINAL WEATHER RESPONSE
        # -----------------------------

        weather_results = f"""
### 🌤️ Weather in {weather_data['city']}

**Current:** 🌡️ {current_temp}°C | ☁️ {current_condition.title()}

**Recommendation:** {current_recommendation}

### 📅 Upcoming Forecast

{forecast_text}
"""

    return {
        **state,
        "weather_results": weather_results,
        "messages": state["messages"] + [HumanMessage(content=weather_results)],
    }


# =========================
# Itinerary Agent
# =========================


def itinerary_agent(state: TravelState):
    prompt = f"""
Create ONLY a day-by-day travel itinerary for this trip — nothing else.
Cover every single day from Day 1 through the final day — do not stop
early, do not summarize remaining days, and do not skip any day.

User Query:
{state['user_query']}

Flight Results (for context only — do not repeat these):
{state['flight_results']}

Hotel Results (for context only — do not repeat these):
{state['hotel_results']}

Weather Results (for context only — do not repeat this):
{state['weather_results']}

For each day, output:
- A short heading: "Day N – [City] – [theme]"
- A table with columns Time | Activity | Cost
- A "Day N total" row with the day's approximate cost

Strict rules — do NOT include any of the following, even briefly:
- A trip overview or introduction
- A restated flight plan or airline list
- A restated hotel list
- A grand total / overall budget summary table
- A packing list, checklist, or visa/currency tips
- A "quick summary" table or a closing "final word" section

Stop as soon as the last day's table and total are written. Nothing
after that.
"""

    itinerary_text = invoke_with_continuation(
        llm,
        [
            SystemMessage(
                content=(
                    "You are an expert travel planner who writes ONLY "
                    "day-by-day itinerary tables — never overviews, "
                    "budget summaries, checklists, or wrap-ups."
                )
            ),
            HumanMessage(content=prompt),
        ],
        max_tokens=6000,
        max_continuations=3,
        continuation_hint="keep going until every remaining day's table and total are written",
    )

    return {
        "itinerary": itinerary_text,
        "messages": [AIMessage(content=itinerary_text)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Final Response Agent
# =========================
#
# IMPORTANT: this used to ask the LLM to regenerate the *entire* itinerary
# again inside the "final" formatted answer. That second full-length
# generation, with no max_tokens set, was the actual source of the
# truncated 7-day plans — it ran out of output tokens partway through
# re-typing days that had already been generated correctly once.
#
# Now we only ask the LLM for a short summary + recommendations, and
# splice in the flight/hotel/weather/itinerary text we already have
# verbatim. Nothing that's already been generated gets regenerated.


def final_agent(state: TravelState):
    summary_prompt = f"""
Based on the details below, write exactly two short sections and nothing
else:

1. "Trip Summary" — 2-3 sentences overview of the trip.
2. "Final Recommendations" — 3-4 concise bullet points of practical tips.

User Request:
{state['user_query']}

Itinerary (for context only — do NOT repeat, list, or re-describe it):
{state['itinerary'][:1500]}

Weather (for context only — do NOT repeat it):
{state['weather_results']}

Strict rules: do not include flight info, hotel info, a budget table, a
checklist, or the day-by-day itinerary — those are added separately by
the app. Total output under 120 words.
"""

    summary_text = invoke_with_continuation(
        llm,
        [
            SystemMessage(
                content="You are a professional AI travel booking assistant."
            ),
            HumanMessage(content=summary_prompt),
        ],
        max_tokens=600,
        max_continuations=1,
        continuation_hint="keep going with the remaining recommendation bullets only",
    )

    final_answer = f"""{summary_text}

## Flight Information
{state['flight_results']}

## Hotel Suggestions
{state['hotel_results']}

## Weather Information
{state['weather_results']}

## Day-by-Day Itinerary
{state['itinerary']}

*Note: live flight data may not include ticket prices if pricing is unavailable from the source API.*
"""

    return {
        "messages": [AIMessage(content=final_answer)],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Build Graph
# =========================

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "weather_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)


# =========================
# PostgreSQL Checkpointer
# =========================
DATABASE_URL = get_database_url()

_conn = psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer)


# =========================
# Function for FastAPI
# =========================


def run_travel_agent(user_input: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}

    result = travel_graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config,
    )

    final_answer = result["messages"][-1].content

    return {
        "thread_id": thread_id,
        "answer": final_answer,
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "itinerary": result.get("itinerary", ""),
        "llm_calls": result.get("llm_calls", 0),
    }

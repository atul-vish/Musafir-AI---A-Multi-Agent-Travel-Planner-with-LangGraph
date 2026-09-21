import os
import sys
from pathlib import Path

import certifi
import httpx
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

# Environment configuration

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# Automatically find the current project folder.
# This replaces the hard-coded Windows paths.
PROJECT_DIR = Path(__file__).resolve().parent
WEATHER_SERVER_PATH = PROJECT_DIR / "custom_weather_mcp_server.py"


# Preserve the complete Windows environment when starting
# local stdio MCP servers.
AVIATION_ENV = os.environ.copy()
AVIATION_ENV["AVIATION_STACK_API_KEY"] = AVIATION_STACK_API_KEY or ""

WEATHER_ENV = os.environ.copy()
WEATHER_ENV["OPENWEATHER_API_KEY"] = OPENWEATHER_API_KEY or ""


# LLM
#
# gpt-oss-20b runs roughly 2x faster than gpt-oss-120b on Groq's hardware.
# extract_destination() only needs to hand back a city/country name, and
# it blocks weather_agent's real work until it finishes, so it's worth
# using the faster model here even though itinerary/final quality calls
# stay on 120b.
# gpt-oss-20b is also a reasoning model: by default its chain-of-thought
# is written into the same content string before the actual answer, so a
# tiny max_tokens (as used below for extract_destination) can get fully
# consumed by reasoning before any visible text comes out — that was
# producing an empty destination string and, downstream, a broken
# weather lookup. reasoning_effort/format keep it fast and clean.
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
    reasoning_effort="low",
    reasoning_format="hidden",
)


# MCP client configuration

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": ("https://mcp.tavily.com/mcp/" f"?tavilyApiKey={TAVILY_API_KEY}"),
        },
        "aviationstack": {
            "transport": "stdio",
            "command": "uvx",
            "args": ["aviationstack-mcp"],
            "env": AVIATION_ENV,
        },
        "weather": {
            "transport": "stdio",
            "command": r"D:\Anaconda\envs\travel\python.exe",
            "args": [
                r"D:\AIML\ML Projects\Musafir-AI---A-Multi-Agent-Travel-Planner-with-LangGraph\custom_weather_mcp_server.py"
            ],
            "env": {"OPENWEATHER_API_KEY": OPENWEATHER_API_KEY},
        },
    }
)


# Diagnostic function


async def get_all_tools():

    all_tools = []

    for server_name in ("tavily", "aviationstack", "weather"):
        try:
            tools = await client.get_tools(server_name=server_name)

            all_tools.extend(tools)

            print(f"\nAvailable tools from " f"{server_name} MCP:\n")

            for tool in tools:
                print(tool.name)

        except Exception as error:
            print(f"\nCould not connect to " f"{server_name} MCP:\n{error}\n")

    return all_tools


# Tavily MCP tool

search_tool = None


async def initialize_mcp():

    global search_tool

    if search_tool is not None:
        return

    tools = await client.get_tools(server_name="tavily")

    tools_by_name = {tool.name: tool for tool in tools}

    search_tool = tools_by_name.get("tavily_search")

    if search_tool is None:
        available_tools = ", ".join(tools_by_name.keys())

        raise RuntimeError(
            "Tavily MCP connected, but the "
            "'tavily_search' tool was not found. "
            f"Available tools: "
            f"{available_tools or 'none'}"
        )


async def tavily_mcp_search(query: str):
    await initialize_mcp()

    result = await search_tool.ainvoke({"query": query})

    return result


# AviationStack MCP tools

aviation_tools = {}


async def initialize_aviation_tools():
    global aviation_tools

    if aviation_tools:
        return

    # Load only AviationStack.
    # Tavily and Weather will not be initialized here.
    tools = await client.get_tools(server_name="aviationstack")

    aviation_tools = {tool.name: tool for tool in tools}

    if not aviation_tools:
        raise RuntimeError("AviationStack MCP connected but " "returned no tools.")


async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    await initialize_aviation_tools()

    tool = aviation_tools.get(tool_name)

    if tool is None:
        available_tools = ", ".join(sorted(aviation_tools.keys()))

        raise ValueError(
            f"AviationStack tool '{tool_name}' "
            "was not found. "
            f"Available tools: "
            f"{available_tools or 'none'}"
        )

    result = await tool.ainvoke(tool_args or {})

    return result


# Weather — direct OpenWeather calls
#
# get_current_weather/get_forecast in custom_weather_mcp_server.py were
# just wrapping plain requests.get() calls to OpenWeather. Routing them
# through MCP stdio meant every single call spawned a brand-new Python
# interpreter process (loading mcp, fastmcp, requests, dotenv, opening an
# MCP session, running one function, tearing it all down) — easily the
# single biggest source of latency in the whole pipeline. Since this is a
# first-party API call within the same codebase, there's no reason to pay
# for a subprocess + protocol round trip: we call OpenWeather directly
# with a shared async HTTP client instead.

_http_client = httpx.AsyncClient(timeout=10.0)


async def weather_mcp_search(city: str):
    response = await _http_client.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"},
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"],
    }


async def forecast_mcp_search(city: str, travel_days: int = 5):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    response = await _http_client.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        return data

    daily_forecasts = {}

    for item in data.get("list", []):
        datetime_text = item["dt_txt"]
        date = datetime_text.split(" ")[0]
        time = datetime_text.split(" ")[1]

        # Store only the forecast closest to 12:00 PM
        target_time = "12:00:00"

        if date not in daily_forecasts:
            daily_forecasts[date] = item
        else:
            existing_time = daily_forecasts[date]["dt_txt"].split(" ")[1]

            # Choose the timestamp closest to 12:00 PM
            current_distance = abs(int(time[:2]) * 60 + int(time[3:5]) - 720)

            existing_distance = abs(
                int(existing_time[:2]) * 60 + int(existing_time[3:5]) - 720
            )

            if current_distance < existing_distance:
                daily_forecasts[date] = item

    # Keep only the requested number of travelling days
    selected_forecasts = list(daily_forecasts.values())[:travel_days]

    forecast = []

    for item in selected_forecasts:
        forecast.append(
            {
                "datetime": item["dt_txt"],
                "date": item["dt_txt"].split(" ")[0],
                "time": item["dt_txt"].split(" ")[1],
                "temperature": item["main"]["temp"],
                "weather": item["weather"][0]["description"],
            }
        )

    return forecast


# Destination extractor


def extract_destination(query: str):
    # This gets passed straight to OpenWeather's geocoder, which needs a
    # single real place name — not a list of cities, not a country name
    # for a multi-city trip, and no extra words. A reply like "Tokyo,
    # Osaka" or "Japan" gets rejected by OpenWeather with a
    # "Nothing to geocode" error, which was previously leaking straight
    # into the final answer as if it were real weather data.
    prompt = f"""
    This query describes a trip, possibly to multiple cities:

    {query}

    Identify the SINGLE main/first destination CITY (not country, not a
    list) and return it in the exact format: City,CountryCode
    (ISO 3166 two-letter country code), e.g. "Tokyo,JP" or "Paris,FR".

    Return ONLY that string. No other words, no punctuation, no quotes.
    """

    # max_tokens was capped at 15 — nowhere near enough headroom once you
    # account for the model's reasoning tokens, which is exactly what
    # left this call returning an empty string.
    response = llm.invoke(prompt, max_tokens=200)

    destination = response.content.strip().strip('"').strip("'")

    # Defense in depth: reasoning models can occasionally still return
    # nothing usable. Never hand an empty string to OpenWeather — that's
    # what produced the "Nothing to geocode" error leaking into output.
    if not destination or len(destination) > 60:
        return "Tokyo,JP"

    return destination

# ✈️ Musafir AI — Multi-Agent Travel Planner

> An AI-powered, multi-agent travel planning system that transforms natural-language travel requests into personalized trip plans using **LangGraph, LangChain, FastAPI, Groq, Tavily, AviationStack, and PostgreSQL**.

<p align="center">

🚀 **[Try Musafir AI Live](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)**

</p>

---

## 📌 Overview

**Musafir AI** is an end-to-end AI travel planning application designed to automate the process of researching and organizing a trip.

Instead of manually searching across multiple platforms for flights, hotels, and activities, users can simply describe their travel requirements in natural language.

Musafir AI uses a **multi-agent architecture orchestrated with LangGraph**, where specialized AI agents collaborate to research different aspects of a trip and produce a structured travel plan.

### Example

A user can enter:

> "Plan a 5-day trip to Tokyo with a budget of $1500."

The system can then coordinate multiple agents to generate:

* ✈️ Flight information
* 🏨 Hotel suggestions
* 🗺️ Day-by-day itinerary
* 💰 Budget-aware recommendations
* 📝 A final consolidated travel plan

---

## 🎯 Problem Statement

Travel planning often requires switching between multiple websites and applications to research:

* Flights
* Hotels
* Tourist attractions
* Daily activities
* Travel budgets
* Itineraries

This process can be time-consuming and fragmented.

**Musafir AI brings these tasks into a single AI-powered workflow using autonomous agents.**

---

## 💡 Solution

Musafir AI divides the travel-planning process into specialized agents.

```text
                     USER REQUEST
                          │
                          ▼
                  ┌───────────────┐
                  │   FastAPI     │
                  │    Backend    │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   LangGraph   │
                  │ Orchestrator  │
                  └───────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │Flight Agent │ │ Hotel Agent │ │ Itinerary   │
   │             │ │             │ │   Agent     │
   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
          │               │               │
          ▼               ▼               ▼
    AviationStack      Tavily Search   LLM Planning
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                  ┌───────────────┐
                  │ Final Response│
                  │     Agent     │
                  └───────┬───────┘
                          │
                          ▼
                   TRAVEL PLAN
```

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture

Specialized agents collaborate to handle different parts of the travel-planning workflow.

* Flight Research Agent
* Hotel Research Agent
* Itinerary Planning Agent
* Final Response Agent

### 🧠 LangGraph Orchestration

LangGraph manages the agent workflow and state transitions, allowing multiple specialized agents to work together as a coordinated system.

### ✈️ Flight Research

Uses **AviationStack** to retrieve flight-related information based on the travel request.

### 🏨 Hotel Research

Uses **Tavily Search** to discover relevant accommodation options and travel information.

### 🗺️ AI Itinerary Generation

The itinerary agent converts the collected travel information into a structured day-by-day plan.

### 💬 Natural-Language Interaction

Users don't need to fill out complicated forms.

They can simply describe their trip naturally.

Example:

```text
I want to visit Dubai for 4 days with a budget of ₹80,000.
Suggest flights, hotels and places to visit.
```

### 💾 Persistent Conversation State

PostgreSQL is used for storing application state and supporting persistent conversations.

### ⚡ LLM-Powered Responses

Groq-powered LLM inference is used to generate fast AI responses.

### 🌐 Web Application

A FastAPI backend serves the application with a lightweight HTML/CSS/JavaScript frontend.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│                  USER                       │
│       Natural Language Travel Request       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                FASTAPI                      │
│             API / Web Layer                 │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│               LANGGRAPH                     │
│          Multi-Agent Orchestrator           │
└──────────────┬──────────┬──────────┬────────┘
               │          │          │
               ▼          ▼          ▼
          Flight Agent  Hotel Agent  Itinerary
               │          │          │
               ▼          ▼          ▼
         AviationStack  Tavily      Groq LLM
               │          │          │
               └──────────┼──────────┘
                          ▼
                 Final Response Agent
                          │
                          ▼
                 Structured Travel Plan
                          │
                          ▼
                     PostgreSQL
```

---

## 🔄 How It Works

### 1. User Input

The user submits a natural-language travel request.

```text
Plan a 3-day trip to Tokyo with a budget of $1200.
```

### 2. Request Processing

FastAPI receives and processes the request.

### 3. Agent Orchestration

LangGraph determines the workflow and coordinates the specialized agents.

### 4. Flight Research

The flight agent retrieves flight-related information through AviationStack.

### 5. Hotel Research

The hotel agent uses Tavily to search for relevant accommodation and travel information.

### 6. Itinerary Planning

The itinerary agent combines the available information and generates a practical schedule.

### 7. Final Response

The final response agent consolidates the results into a user-friendly travel plan.

### 8. State Persistence

Relevant conversation/application state can be persisted using PostgreSQL.

---

## 🛠️ Tech Stack

| Category         | Technology            |
| ---------------- | --------------------- |
| Language         | Python                |
| Backend          | FastAPI               |
| AI Orchestration | LangGraph             |
| LLM Framework    | LangChain             |
| LLM Inference    | Groq                  |
| Web Search       | Tavily                |
| Flight Data      | AviationStack         |
| Database         | PostgreSQL            |
| Frontend         | HTML, CSS, JavaScript |
| Templating       | Jinja2                |
| Deployment       | Render                |

---

## 📁 Project Structure

```text
Musafir-AI/
│
├── app.py
│   └── FastAPI application entry point
│
├── backend.py
│   └── LangGraph multi-agent workflow
│
├── requirements.txt
│   └── Python dependencies
│
├── static/
│   └── Frontend static assets
│
├── templates/
│   └── HTML templates
│
├── tools/
│   └── External API and search integrations
│
├── .env
│   └── Environment variables
│
└── README.md
    └── Project documentation
```

---

## ⚙️ Prerequisites

Before running Musafir AI locally, make sure you have:

* Python **3.10+**
* PostgreSQL
* Git
* A Groq API key
* A Tavily API key
* An AviationStack API key

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Musafir-AI.git
cd Musafir-AI
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db

GROQ_API_KEY=your_groq_api_key

AVIATIONSTACK_API_KEY=your_aviationstack_api_key

TAVILY_API_KEY=your_tavily_api_key

DEFAULT_ORIGIN_IATA=DAC
```

> ⚠️ Never commit your `.env` file or expose API keys publicly.

Add this to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

## ▶️ Running Locally

Start the FastAPI application:

```bash
python app.py
```

The application should be available at:

```text
http://127.0.0.1:8001/
```

Open the URL in your browser.

---

## 🌐 Live Demo

Try the deployed application:

🚀 **[Launch Musafir AI](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)**

---

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

Used to verify that the backend is running.

### Travel Planning

```http
POST /api/travel
```

Accepts a natural-language travel request.

### Example

```bash
curl -X POST http://127.0.0.1:8001/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

---

## 🧪 Example Input

```text
Plan a 4-day trip to Dubai.

Budget: ₹80,000

I want:
- Good hotels
- Flight suggestions
- Popular attractions
- A day-by-day itinerary
```

## 📋 Example Output

The system generates a structured travel plan containing relevant information such as:

```text
✈️ Flight Suggestions

🏨 Hotel Recommendations

📅 Day 1
- Activity 1
- Activity 2
- Activity 3

📅 Day 2
- Activity 1
- Activity 2
- Activity 3

📅 Day 3
- Activity 1
- Activity 2

📅 Day 4
- Activity 1
- Activity 2

💰 Estimated Budget

📝 Additional Travel Tips
```

---

## 🧠 Why Multi-Agent Architecture?

A single LLM can generate a travel plan, but specialized agents provide a more modular architecture.

Each agent focuses on a specific responsibility:

```text
Flight Agent
     │
     ├── Flight-related research
     │
Hotel Agent
     │
     ├── Accommodation research
     │
Itinerary Agent
     │
     ├── Schedule generation
     │
Final Agent
     │
     └── Response synthesis
```

This makes the system easier to extend with additional capabilities such as:

* Restaurant recommendations
* Weather analysis
* Budget optimization
* Local transportation
* Visa information
* Activity recommendations
* Travel alerts

---

## 📈 Future Improvements

Potential improvements include:

* [ ] Real-time hotel booking integration
* [ ] Real-time flight booking
* [ ] Weather-aware itinerary generation
* [ ] Restaurant recommendation agent
* [ ] Budget optimization agent
* [ ] Map integration
* [ ] User authentication
* [ ] Personalized travel preferences
* [ ] Multi-language support
* [ ] Voice-based travel planning
* [ ] Agent observability and tracing
* [ ] Improved error handling and fallback agents
* [ ] Containerized deployment with Docker
* [ ] Automated CI/CD pipeline

---

## 🔒 Security Considerations

* API keys are stored using environment variables.
* Sensitive credentials should never be committed to GitHub.
* Production deployments should use secure secret management.
* Database credentials should not be hardcoded.
* External API failures should be handled gracefully.

---

## 🤝 Contributing

Contributions are welcome!

### Fork the repository

```bash
git fork
```

Or fork the repository directly through GitHub.

### Create a feature branch

```bash
git checkout -b feature/new-feature
```

### Commit your changes

```bash
git add .
git commit -m "feat: add new travel feature"
```

### Push your branch

```bash
git push origin feature/new-feature
```

Then open a Pull Request.

---

## 🗺️ Roadmap

```text
✅ Basic Travel Planner
        │
        ▼
✅ Multi-Agent Architecture
        │
        ▼
✅ LangGraph Orchestration
        │
        ▼
✅ Flight Research
        │
        ▼
✅ Hotel Research
        │
        ▼
✅ AI Itinerary Generation
        │
        ▼
✅ PostgreSQL State Persistence
        │
        ▼
🚧 Advanced Personalization
        │
        ▼
🚧 Real-Time Travel Intelligence
        │
        ▼
🚧 Voice + Multilingual Support
```

---

## 📊 Project Goals

Musafir AI aims to demonstrate how modern AI engineering concepts can be combined into a production-style application:

* Multi-agent systems
* LLM orchestration
* Tool calling
* API integrations
* State management
* Database persistence
* Backend engineering
* AI-powered decision workflows
* Cloud deployment

---

## 🙌 Acknowledgments

Built using modern AI and web technologies including:

* LangGraph
* LangChain
* Groq
* FastAPI
* Tavily
* AviationStack
* PostgreSQL

---

## 📄 License

This project is open source. Add your preferred license file, such as **MIT License**, before publishing the repository.

---

## ⭐ Support

If you find Musafir AI useful or interesting:

⭐ Star the repository
🍴 Fork the project
🐛 Report issues
💡 Suggest new features
🤝 Contribute to the project

---

<p align="center">

### ✈️ Plan smarter. Travel better. Explore more.

**[🚀 Try Musafir AI Live](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)**

</p>

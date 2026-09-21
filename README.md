# ✈️ Musafir AI

### MCP-Enabled Multi-Agent AI Travel Planner

> **An AI-powered travel planning system built with Multi-Agent Architecture, LangGraph, MCP, LLMs, external tools, and real-time travel data integrations.**

[![Live Demo](https://img.shields.io/badge/Live-Demo-00C853?style=for-the-badge)](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square\&logo=fastapi\&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-1C3C3C?style=flat-square)](https://www.langchain.com/langgraph)
[![LangChain](https://img.shields.io/badge/LangChain-LLM_Framework-1C3C3C?style=flat-square)](https://www.langchain.com/)
[![MCP](https://img.shields.io/badge/MCP-Tool_Integration-8B5CF6?style=flat-square)](https://modelcontextprotocol.io/)
[![Groq](https://img.shields.io/badge/Groq-LLM_Inference-F55036?style=flat-square)](https://groq.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=flat-square\&logo=postgresql\&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square\&logo=docker\&logoColor=white)](https://www.docker.com/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=flat-square)](https://render.com/)

---

## 🌐 Live Application

### [🚀 Launch Musafir AI](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)

Musafir AI transforms natural-language travel requirements into structured travel plans by combining **LLM reasoning, multi-agent orchestration, MCP-based tool integration, external APIs, web search, and persistent application state**.

---

# 🧠 What is Musafir AI?

**Musafir AI** is an end-to-end **Multi-Agent AI Travel Planner** designed to automate complex travel research and planning workflows.

Instead of manually switching between flight websites, hotel platforms, search engines, travel guides, and itinerary planners, users can simply describe their requirements in natural language.

For example:

```text
Plan a 5-day trip to Tokyo with a budget of $1500.

I need:
- Flight suggestions
- Affordable hotels
- Popular attractions
- A day-by-day itinerary
- Budget-aware recommendations
```

Musafir AI processes the request through a coordinated AI workflow consisting of specialized agents and external tools.

---

# 🚀 What Makes This Project Different?

Musafir AI is not designed as a simple:

```text
User → LLM → Response
```

Instead, it follows an **agentic AI architecture**:

```text
User
 │
 ▼
FastAPI
 │
 ▼
LangGraph Orchestrator
 │
 ├───────────────┐
 ▼               ▼
Specialized     MCP
Agents           Tools
 │               │
 └───────┬───────┘
         ▼
External APIs / Search
         │
         ▼
Final Response Agent
         │
         ▼
Structured Travel Plan
```

The project demonstrates practical AI engineering concepts including:

* Multi-Agent Systems
* LLM orchestration
* LangGraph state management
* Model Context Protocol (MCP)
* Tool calling
* External API integration
* Web search
* PostgreSQL persistence
* FastAPI backend development
* Docker containerization
* Cloud deployment

---

# 🔌 MCP — Model Context Protocol

Musafir AI integrates **Model Context Protocol (MCP)** to provide a standardized architecture for connecting AI agents with external tools and capabilities.

Instead of tightly coupling every external capability directly to the agent, MCP provides a tool-oriented integration layer.

```text
                  ┌─────────────────────┐
                  │     AI Agent        │
                  │                     │
                  │    LangGraph        │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     MCP Client      │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │     MCP Server      │
                  │                     │
                  │      Tools          │
                  └──────────┬──────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        Flight Tools    Search Tools    Other Tools
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                       External Data
```

### Why MCP?

MCP makes the architecture more extensible by creating a clear separation between:

```text
AI Reasoning
     │
     ▼
Tool Interface
     │
     ▼
External Capability
```

This allows additional tools and integrations to be introduced without tightly coupling every capability to the core agent implementation.

---

# 🏗️ System Architecture

```text
                         ┌───────────────────┐
                         │       USER        │
                         │ Natural Language  │
                         │   Travel Request  │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │      FastAPI      │
                         │    API / Web      │
                         │      Layer        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │     LangGraph     │
                         │ Agent Orchestrator│
                         └─────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
       │ Flight Agent │     │ Hotel Agent  │     │ Itinerary    │
       │              │     │              │     │ Agent        │
       └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    MCP Client     │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    MCP Server     │
                         │      Tools        │
                         └─────────┬─────────┘
                                   │
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
             Flight API       Web Search       Other Tools
                  │                │                │
                  └────────────────┼────────────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │   Final Response  │
                         │      Agent        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │  Structured Trip  │
                         │       Plan        │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │    PostgreSQL     │
                         │ State / Persistence│
                         └───────────────────┘
```

---

# 🤖 Multi-Agent Architecture

Musafir AI separates travel planning into specialized responsibilities.

### ✈️ Flight Research Agent

Responsible for flight-related research and retrieval.

Primary integrations include:

* AviationStack
* MCP-based tool integration

---

### 🏨 Hotel Research Agent

Responsible for discovering accommodation options and relevant travel information.

Primary integration:

* Tavily Search

---

### 🗺️ Itinerary Agent

Transforms collected travel context into a structured itinerary.

Responsibilities include:

* Destination planning
* Activity organization
* Schedule generation
* Budget-aware reasoning
* Travel recommendations

---

### 🧠 Final Response Agent

Aggregates the outputs from the specialized agents and generates the final user-facing travel plan.

```text
Flight Research
       │
       ▼
Hotel Research
       │
       ▼
Itinerary Planning
       │
       ▼
Final Response Agent
       │
       ▼
Structured Travel Plan
```

---

# 🔄 End-to-End Workflow

### 01 — User Request

```text
Plan a 4-day trip to Dubai with a budget of ₹80,000.
Find flights, hotels and places to visit.
```

### 02 — API Layer

FastAPI receives the request.

### 03 — Agent Orchestration

LangGraph manages the execution flow and agent state.

### 04 — Tool Selection

Agents determine which external capabilities are required.

### 05 — MCP Integration

The MCP client communicates with the MCP server to access supported tools.

### 06 — External Data Retrieval

The system retrieves relevant information through external APIs and web search.

### 07 — Itinerary Generation

The itinerary agent converts the collected context into a structured schedule.

### 08 — Response Synthesis

The final response agent combines the outputs.

### 09 — Persistence

Relevant application state can be stored in PostgreSQL.

### 10 — User Response

The user receives a consolidated travel plan.

---

# ✨ Core Features

| Feature               | Description                                   |
| --------------------- | --------------------------------------------- |
| 🤖 Multi-Agent System | Specialized agents for different travel tasks |
| 🧠 LangGraph          | Agent workflow and state orchestration        |
| 🔌 MCP                | Standardized AI-to-tool integration           |
| 🛠️ Tool Calling      | Agents interact with external capabilities    |
| ✈️ Flight Research    | Flight-related information retrieval          |
| 🏨 Hotel Research     | Accommodation discovery                       |
| 🗺️ AI Itinerary      | Day-by-day itinerary generation               |
| 💬 Natural Language   | No complex travel forms                       |
| ⚡ Fast LLM Inference  | Groq-powered inference                        |
| 🔎 Web Research       | Tavily-powered search                         |
| 💾 Persistent State   | PostgreSQL-backed persistence                 |
| 🌐 REST API           | FastAPI backend                               |
| 🐳 Docker             | Containerized deployment                      |
| ☁️ Cloud Deployment   | Render                                        |

---

# 🛠️ Technology Stack

## AI / Agent Layer

* **Python**
* **LangGraph**
* **LangChain**
* **Groq**
* **Model Context Protocol (MCP)**

## Backend

* **FastAPI**
* **Uvicorn**
* **Jinja2**

## Tool & Data Integrations

* **MCP**
* **AviationStack**
* **Tavily**

## Database

* **PostgreSQL**

## Frontend

* **HTML**
* **CSS**
* **JavaScript**

## Infrastructure

* **Docker**
* **Render**

---

# 📂 Project Structure

```text
Musafir-AI/
│
├── app.py
│   └── FastAPI application entry point
│
├── backend.py
│   └── Multi-agent workflow
│
├── mcp_client.py
│   └── MCP client integration
│
├── mcp_server.py
│   └── MCP server / tool layer
│
├── requirements.txt
│   └── Python dependencies
│
├── Dockerfile
│   └── Container configuration
│
├── static/
│   └── CSS, JavaScript and static assets
│
├── templates/
│   └── HTML templates
│
├── tools/
│   └── External API and tool integrations
│
├── .env
│   └── Local environment variables
│
├── .gitignore
│
└── README.md
```

---

# ⚙️ Local Development

## Prerequisites

Make sure you have:

* Python 3.10+
* Git
* PostgreSQL
* Docker
* Required API credentials
* MCP dependencies required by the configured tools

---

## 1. Clone the Repository

```bash
git clone https://github.com/atul-vish/Musafir-AI---A-Multi-Agent-Travel-Planner-with-LangGraph.git

cd Musafir-AI---A-Multi-Agent-Travel-Planner-with-LangGraph
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a `.env` file:

```env
DATABASE_URL=your_postgresql_connection_string

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

AVIATIONSTACK_API_KEY=your_aviationstack_api_key

DEFAULT_ORIGIN_IATA=DAC
```

Additional variables may be required depending on the MCP tools and integrations enabled in the current deployment.

### Security

Never commit secrets to GitHub.

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# ▶️ Running Locally

Start the application:

```bash
python app.py
```

The application runs at:

```text
http://127.0.0.1:8001
```

---

# 🐳 Docker

Build:

```bash
docker build -t musafir-ai .
```

Run:

```bash
docker run --env-file .env -p 8001:8001 musafir-ai
```

Application:

```text
http://localhost:8001
```

---

# 🌐 Deployment

Musafir AI is deployed using **Docker + Render**.

```text
Developer
    │
    ▼
Git Commit
    │
    ▼
GitHub
    │
    ▼
Render
    │
    ▼
Docker Build
    │
    ├── Python Runtime
    ├── Application Dependencies
    ├── MCP Runtime
    └── Environment Configuration
    │
    ▼
FastAPI Application
    │
    ▼
Live Musafir AI
```

---

# 🔌 API

## Health Check

```http
GET /health
```

## Travel Planning

```http
POST /api/travel
```

Example:

```bash
curl -X POST http://127.0.0.1:8001/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

---

# 🧪 Example Request

```text
Plan a 5-day trip to Singapore.

Budget: ₹1,00,000

I need:
- Flight suggestions
- Affordable hotels
- Popular attractions
- Local transportation suggestions
- A day-by-day itinerary
- Budget-aware recommendations
```

---

# 🧩 AI Engineering Concepts Demonstrated

Musafir AI demonstrates practical AI engineering beyond basic LLM API usage.

### Agentic AI

Multiple specialized agents collaborate to complete a complex task.

### LLM Orchestration

LangGraph manages agent execution and state transitions.

### MCP

MCP provides a standardized tool integration layer between AI agents and external capabilities.

### Tool Calling

Agents interact with APIs, search systems, and external tools.

### State Management

PostgreSQL provides persistent application state.

### API Engineering

FastAPI exposes the AI system through a backend service.

### Containerization

Docker packages the application and runtime environment.

### Cloud Deployment

The application is deployed as a cloud-hosted service.

### Failure Handling

External APIs and tools can fail independently, requiring graceful handling and fallbacks.

---

# 📈 Extensibility

The MCP-oriented architecture makes it possible to introduce additional tools and agents.

Potential future capabilities:

```text
                    Musafir AI
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Flight Tools    Hotel Tools      Search Tools
        │               │                │
        └───────────────┼────────────────┘
                        │
                        ▼
                  MCP Tool Layer
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
   Weather          Restaurant       Transport
    Agent              Agent            Agent
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                Travel Intelligence
```

Potential additions include:

* Weather Agent
* Restaurant Agent
* Transportation Agent
* Budget Optimization Agent
* Visa Information Agent
* Activity Recommendation Agent
* Travel Alert Agent

---

# 🗺️ Roadmap

### Core Platform

* [x] Natural-language travel planning
* [x] FastAPI backend
* [x] LangGraph orchestration
* [x] Multi-agent architecture
* [x] LLM-powered itinerary generation

### Travel Intelligence

* [x] Flight research
* [x] Hotel research
* [x] Web search integration
* [x] PostgreSQL persistence

### MCP & Tooling

* [x] MCP integration
* [x] MCP client/server architecture
* [ ] Expand MCP tool ecosystem
* [ ] Tool-level observability
* [ ] Improved tool fallback handling

### Personalization

* [ ] User profiles
* [ ] Persistent travel preferences
* [ ] Personalized recommendations
* [ ] Budget optimization

### Advanced Travel Intelligence

* [ ] Weather-aware itinerary generation
* [ ] Real-time travel alerts
* [ ] Map integration
* [ ] Transportation optimization
* [ ] Real-time booking integrations

### AI Experience

* [ ] Voice-based travel planning
* [ ] Multilingual support
* [ ] Conversational trip modification
* [ ] Mobile application

### Production AI Engineering

* [ ] Agent observability
* [ ] Distributed tracing
* [ ] Evaluation pipelines
* [ ] Automated testing
* [ ] CI/CD
* [ ] LLM evaluation framework
* [ ] Cost and latency monitoring

---

# 🔒 Security & Reliability

Production AI applications require more than model integration.

Musafir AI follows these engineering principles:

* 🔐 Secrets are stored through environment variables.
* 🗄️ Database credentials are not hardcoded.
* 🌐 External API failures should be handled gracefully.
* 🧩 Agent responsibilities are separated.
* 🔌 Tool integrations are isolated through defined interfaces.
* 🐳 Runtime dependencies are containerized.
* 🚫 Sensitive credentials should never be committed to GitHub.
* 📊 Production deployments should use monitoring and logging.
* 🔄 External integrations should have fallback strategies.

---

# 📊 Observability & Evaluation

Future production improvements should evaluate both software and AI quality.

### System Metrics

* Request latency
* API response time
* Tool execution time
* Error rate
* Database latency
* LLM latency

### AI Metrics

* Response relevance
* Itinerary quality
* Tool-selection accuracy
* Hallucination rate
* Task completion rate
* User satisfaction

### Cost Metrics

* Token consumption
* LLM cost per request
* External API usage
* Average cost per itinerary

---

# 🤝 Contributing

### 1. Fork the repository

Fork the project through GitHub.

### 2. Create a feature branch

```bash
git checkout -b feature/new-travel-agent
```

### 3. Make your changes

```bash
git add .
```

### 4. Commit

```bash
git commit -m "feat: add new travel agent"
```

### 5. Push

```bash
git push origin feature/new-travel-agent
```

### 6. Open a Pull Request

Include:

* What changed
* Why it changed
* How it was tested
* New environment variables, if any
* Any architectural considerations

---

# 📝 Development Guidelines

Recommended commit convention:

```text
feat: add weather agent
fix: handle flight API timeout
refactor: simplify itinerary workflow
docs: update MCP documentation
test: add agent workflow tests
chore: update dependencies
```

---

# 🏆 Project Goals

Musafir AI demonstrates how modern AI engineering components can be combined into an extensible application:

```text
                    Musafir AI
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
      LLMs           Agents             Tools
       │                │                │
       ▼                ▼                ▼
    Groq          LangGraph            MCP
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                  FastAPI Backend
                        │
                        ▼
                   PostgreSQL
                        │
                        ▼
                     Docker
                        │
                        ▼
                     Render
```

The goal is to demonstrate an AI system that combines:

* Multi-Agent AI
* LLM orchestration
* MCP
* Tool calling
* External API integration
* State management
* Backend engineering
* Database persistence
* Containerization
* Cloud deployment

---

# 🙏 Acknowledgements

Built with:

* [LangGraph](https://www.langchain.com/langgraph)
* [LangChain](https://www.langchain.com/)
* [Model Context Protocol](https://modelcontextprotocol.io/)
* [Groq](https://groq.com/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Tavily](https://tavily.com/)
* [AviationStack](https://aviationstack.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [Docker](https://www.docker.com/)
* [Render](https://render.com/)

---

# 📄 License

This project is currently intended as an open-source project.

Add an appropriate `LICENSE` file before distributing the repository publicly.

---

# ⭐ Support the Project

If you find Musafir AI useful or interesting:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report issues
* 💡 Suggest features
* 🤝 Contribute

---

<div align="center">

# ✈️ Musafir AI

### From natural language to an intelligent travel plan.

**Multi-Agent AI • LangGraph • MCP • FastAPI • Groq • PostgreSQL • Docker**

[🚀 **Try Musafir AI Live**](https://musafir-ai-a-multi-agent-travel-planner.onrender.com)

</div>

# AI SDR — Autonomous AI Sales Development Representative

An autonomous sales pipeline powered by [CrewAI](https://github.com/crewAIInc/crewAI) agents. The system sources franchise leads, qualifies and scores them against your Ideal Customer Profile (ICP), routes them to the right sales rep, and sends personalized outreach — all without human intervention.

## Features

- **Multi-agent pipeline** — five specialized CrewAI agents orchestrated by a hierarchical manager
- **Franchise-aware intelligence** — built-in logic for franchise directories, FDD signals, land-and-expand opportunities, and unit-count growth analysis
- **Full CRM sync** — pushes qualified leads and activity to Salesforce
- **Automated outreach** — personalized emails via Resend with Cal.com booking links
- **Slack notifications** — rep alerts when new leads are routed or meetings are booked
- **REST API** — FastAPI service with versioned endpoints for ICP management, pipeline runs, and reporting
- **Background workers** — ARQ/Redis job queue for async pipeline execution
- **Streamlit dashboard** — real-time pipeline metrics and run history
- **One-command deploy** — Docker Compose for local dev, Railway for production

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  CrewAI Pipeline                │
│                                                 │
│  Lead Sourcer → Qualifier → Router → Setter     │
│                     ↑                           │
│              Pipeline Manager (hierarchical)    │
└─────────────────────────────────────────────────┘
        ↕                         ↕
  FastAPI (port 8000)     Streamlit (port 8501)
        ↕
  ARQ Worker ←→ Redis
        ↕
  PostgreSQL (persistence)
```

### Agents

| Agent | Role |
|---|---|
| **Lead Sourcer** | Discovers franchise companies and contacts via web scraping, DuckDuckGo, and franchise directories |
| **Lead Qualifier** | Scores leads 0–100 against ICP criteria; assigns Hot / Warm / Cold tiers |
| **Lead Router** | Applies configurable routing rules to assign leads to the right sales rep or team |
| **Appointment Setter** | Writes personalized outreach, checks calendar availability, sends email, and books meetings |
| **Pipeline Manager** | Hierarchical manager agent that oversees and coordinates all other agents |

### Integrations

| Category | Service |
|---|---|
| LLM | Anthropic Claude (via LiteLLM — swap to any provider) |
| CRM | Salesforce |
| Email | Resend |
| Calendar | Cal.com |
| Notifications | Slack |
| Web search | DuckDuckGo (no API key required) |
| Database | PostgreSQL + SQLAlchemy (async) |
| Job queue | Redis + ARQ |

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for local development)
- API keys for the integrations you want to use (see [Configuration](#configuration))

### Local Setup

1. **Clone and install dependencies**

   ```bash
   git clone https://github.com/mmccarthyhearst/AI-SDR.git
   cd AI-SDR
   pip install -e ".[dev]"
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Start infrastructure and run the API**

   ```bash
   make docker-up      # start Postgres + Redis
   make migrate        # run database migrations
   make dev            # start the FastAPI server on :8000
   ```

4. **Open the dashboard** (optional)

   ```bash
   pip install -e ".[ui]"
   make dashboard      # Streamlit UI on :8080
   ```

### Full Stack with Docker Compose

Starts the API, background worker, Streamlit dashboard, Postgres, and Redis in one command:

```bash
docker compose up -d
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Dashboard | http://localhost:8501 |

## Configuration

All settings are controlled via environment variables. Copy `.env.example` to `.env` and fill in your values.

| Variable | Description | Required |
|---|---|---|
| `API_KEY` | Authentication key for the REST API | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `LLM_PROVIDER` | LiteLLM provider (e.g. `anthropic`) | ✅ |
| `LLM_MODEL_FAST` | Fast model for sourcing (e.g. `claude-haiku-4-5-20251001`) | ✅ |
| `LLM_MODEL_MID` | Mid-tier model for qualifying & outreach | ✅ |
| `LLM_API_KEY` | API key for your LLM provider | ✅ |
| `RESEND_API_KEY` | Resend email API key | For email |
| `EMAIL_FROM_ADDRESS` | Sender email address | For email |
| `CALCOM_API_KEY` | Cal.com API key | For calendar |
| `SALESFORCE_USERNAME` | Salesforce username | For CRM sync |
| `SALESFORCE_PASSWORD` | Salesforce password | For CRM sync |
| `SALESFORCE_SECURITY_TOKEN` | Salesforce security token | For CRM sync |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL | For notifications |

## API Reference

The FastAPI service exposes a versioned REST API at `/api/v1`. Interactive docs are available at `/docs` when the server is running.

Key endpoint groups:

- `POST /api/v1/pipeline/run` — kick off a new SDR pipeline run
- `GET /api/v1/pipeline/runs` — list pipeline run history and metrics
- `GET /api/v1/leads` — list sourced and qualified leads
- `GET /api/v1/companies` — browse discovered companies
- `GET /api/v1/appointments` — view booked appointments
- `PUT /api/v1/icp` — update Ideal Customer Profile criteria
- `PUT /api/v1/routing-rules` — update lead routing rules

## Running the Pipeline Manually

Use the included script to trigger a pipeline run from the command line:

```bash
python scripts/run_pipeline.py
```

To seed initial ICP data:

```bash
python scripts/seed_icp.py
```

## Development

```bash
make test        # run tests
make test-cov    # run tests with HTML coverage report
make lint        # check code style (ruff)
make fix         # auto-fix code style issues
```

### Creating a Database Migration

```bash
make migrate-new msg="describe your change"
make migrate
```

## Deploying to Railway

The repo includes a `railway.toml` that deploys three services:

| Service | Start command |
|---|---|
| `api` | `alembic upgrade head && uvicorn ai_sdr.main:app` |
| `worker` | `python -m arq ai_sdr.workers.settings.WorkerSettings` |
| `dashboard` | `streamlit run src/ai_sdr/ui/app.py` |

Add your environment variables in the Railway dashboard and push — deployments are Dockerfile-based.

## Project Structure

```
src/ai_sdr/
├── agents/          # CrewAI agent definitions
│   ├── crew.py      # Pipeline orchestration
│   ├── lead_sourcer.py
│   ├── lead_qualifier.py
│   ├── lead_router.py
│   ├── appointment_setter.py
│   └── pipeline_manager.py
├── api/v1/          # FastAPI route handlers
├── db/              # Database engine, session, base models
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic layer
├── tools/           # CrewAI tool definitions (CRM, email, calendar, etc.)
├── ui/              # Streamlit dashboard
├── workers/         # ARQ background worker settings
├── config.py        # Pydantic settings
└── main.py          # FastAPI application factory
```

## License

MIT

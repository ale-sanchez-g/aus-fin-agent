# aus-fin-agent

An Australian open banking product discovery platform that uses the Consumer Data Right (CDR) and an AI agent to help users find the most suitable financial products.

---

## Overview

`aus-fin-agent` is a production-ready monorepo that combines a LangGraph-powered AI agent, a CDR/open banking data adapter, a background sync worker, and a React web interface. Users describe what they are looking for in natural language and the agent retrieves, filters, scores, and explains the best-matching financial products, generating a compliant recommendation report.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser (React SPA)                                            │
│  Discovery Wizard → Product Comparison → Report Viewer          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (Axios)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Backend  (port 8000)                                   │
│                                                                  │
│   POST /discovery/sessions  ──►  LangGraph Agent (7 nodes)     │
│   GET  /products                                                 │
│   GET  /reports                                                  │
│   GET  /providers                                                │
│                                                                  │
│   ┌─────────────┐   ┌─────────────────┐   ┌────────────────┐  │
│   │  SQLAlchemy │   │  AWS Bedrock    │   │  AWS S3        │  │
│   │  PostgreSQL │   │  (Claude 3.5)   │   │  (Reports)     │  │
│   └─────────────┘   └─────────────────┘   └────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  OpenBanking MCP Adapter  (port 4000)                           │
│  Express.js  –  Mock CDR data (dev) / Live CDR API (prod)       │
└─────────────────────────────────────────────────────────────────┘
                             ▲
                             │ Periodic sync
┌────────────────────────────┴────────────────────────────────────┐
│  Worker Service  (port 8001)                                    │
│  Syncs products & providers from adapter into PostgreSQL        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
aus-fin-agent/
├── apps/
│   ├── api/          # FastAPI backend + LangGraph agent
│   ├── web/          # React + TypeScript frontend
│   └── worker/       # Background sync service (Python)
├── packages/
│   ├── openbanking-mcp-adapter/   # Node.js CDR adapter (Express)
│   └── shared-schemas/            # Shared JS/TS schema definitions
└── infra/
    └── terraform/    # AWS networking & ECS infrastructure
```

---

## Services

### API (`apps/api`)

FastAPI service that exposes the REST API and orchestrates the AI agent.

**Key endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/discovery/sessions` | Start a product discovery workflow |
| `GET`  | `/api/v1/discovery/sessions/{id}/results` | Retrieve ranked recommendations |
| `GET`  | `/api/v1/products` | Paginated/filtered product listing |
| `GET`  | `/api/v1/products/compare` | Side-by-side comparison of up to 10 products |
| `GET`  | `/api/v1/reports/{id}` | Fetch a generated recommendation report |

**LangGraph agent pipeline** (triggered by `POST /discovery/sessions`):

```
Intake → Retrieval → Eligibility → Scoring → Reasoning → Compliance → Report
```

1. **Intake** – Parses the user's natural language intent; infers product category and a weight profile (`balanced`, `fee_conscious`, `rate_focused`, `feature_rich`); extracts hard constraints (e.g. maximum monthly fee).
2. **Retrieval** – Queries the database for all products matching the inferred category.
3. **Eligibility** – Filters products against the user's constraints (fee caps, rate ranges, residency, minimum age).
4. **Scoring** – Applies a weighted scoring engine across six dimensions: monthly fees, rate competitiveness, feature fit, eligibility fit, digital capability, and overall suitability.
5. **Reasoning** – Calls **AWS Bedrock (Claude 3.5 Sonnet)** to generate a human-readable narrative; falls back to a template if Bedrock is unavailable.
6. **Compliance** – Softens prescriptive language and appends required CDR disclaimers.
7. **Report** – Assembles the final report, persists it to **AWS S3**, and saves metadata to PostgreSQL.

**Tech stack:** Python 3.12, FastAPI 0.115, SQLAlchemy 2.0, Alembic, LangGraph ≥ 0.2.28, LangChain-Core ≥ 0.3.81, Pydantic 2.9, structlog, tenacity, AWS Bedrock / S3 / Cognito.

---

### Worker (`apps/worker`)

Runs on a configurable interval (hours) and keeps the database up to date with the latest CDR product data.

**Cycle:**
1. Fetch products from the adapter (`GET /api/products`).
2. Fetch providers/data holders (`GET /api/providers`).
3. Upsert records into PostgreSQL.
4. Every 4 cycles, clean up stale records.

Exposes a health-check HTTP endpoint on port 8001 and shuts down gracefully on `SIGTERM`/`SIGINT`.

---

### OpenBanking MCP Adapter (`packages/openbanking-mcp-adapter`)

Express.js service (port 4000) that abstracts the CDR API. In development/test it serves pre-populated mock data; in production it connects to the real open banking MCP library.

**Routes:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health + mock-mode flag |
| `GET` | `/api/providers` | All registered data holders |
| `GET` | `/api/providers/:id/products` | Products for a provider (optional category filter) |
| `GET` | `/api/products` | All products across all providers |
| `GET` | `/api/products/:id` | Single product detail |

Set `USE_MOCK_DATA=true` to use bundled mock data without a live CDR connection.

---

### Web (`apps/web`)

React 18 + TypeScript SPA served by Nginx.

**Routes:**

| Path | Page | Description |
|------|------|-------------|
| `/` | Dashboard | Overview and quick navigation |
| `/discover` | Discovery Wizard | Multi-step form: Category → Weight Profile → Preferences → Review |
| `/products` | Product Comparison | Side-by-side product table |
| `/reports/:sessionId` | Report Viewer | Narrative, scores, and compliance notes |
| `/sync-status` | Sync Status | Health of the last data sync cycle |

The Discovery Wizard submits to the API and polls until the agent finishes (2-minute timeout), then redirects to the Report Viewer.

**Tech stack:** React 18.3, React Router 6, Axios 1.7.7, TypeScript 5.5, Vite 5.4, Vitest, Playwright (E2E).

---

### Shared Schemas (`packages/shared-schemas`)

Single source of truth for data shapes (products, providers, discovery sessions, reports) shared between the Node adapter, frontend, and any other JS/TS consumers.

---

## Infrastructure

Deployed on **AWS ap-southeast-2** using Terraform:

- **ECS Fargate** – Runs all four container services (api, web, worker, node-adapter).
- **VPC** – Public/private subnets across 2 AZs, NAT Gateway.
- **ALB** – Routes traffic to the web and API containers.
- **RDS PostgreSQL** – Primary datastore.
- **S3** – Stores generated recommendation reports (`aus-fin-agent-reports-<env>`).
- **AWS Cognito** – User authentication and JWT issuance.
- **AWS Bedrock** – LLM inference (Claude 3.5 Sonnet) for narrative generation.

---

## CI/CD

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `ci.yml` | Push / PR | Lint (ruff, ESLint, tsc), unit tests (pytest, Vitest, Jest) |
| `cd.yml` | Push to `main` | Build Docker images, push to ECR, force-deploy ECS services |

---

## Local Development

### Prerequisites

- Docker + Docker Compose
- Python 3.12
- Node.js 20

### Environment variables

A `.env` file is included at the repo root with safe defaults for local development. The adapter uses bundled mock CDR data (`USE_MOCK_DATA=true`) so no live AWS credentials are required to start. If you want real Bedrock narrative generation or S3 report storage, fill in the AWS fields.

```bash
# optional: review / override values before first run
vim .env
```

### Run with Docker Compose

```bash
docker-compose up -d --build
```

This starts all five services (PostgreSQL, node-adapter, backend API, worker, web). 

| Service | URL |
|---------|-----|
| Web app | http://localhost:80 |
| API | http://localhost:8000 |
| OpenBanking adapter | http://localhost:4000 |
| Worker health | http://localhost:8001 |
| PostgreSQL | localhost:5432 |

### Run services individually

**API:**
```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Adapter:**
```bash
cd packages/openbanking-mcp-adapter
npm install
USE_MOCK_DATA=true node src/server.js
```

**Worker:**
```bash
cd apps/worker
pip install -r requirements.txt
python -m app.main
```

**Web:**
```bash
cd apps/web
npm install
npm run dev
```

### Run tests

```bash
# API + worker (Python)
cd apps/api && pytest
cd apps/worker && pytest

# Web (Vitest unit tests)
cd apps/web && npm test

# Adapter (Jest)
cd packages/openbanking-mcp-adapter && npm test

# E2E (Playwright)
cd apps/web && npx playwright test
```

---

## License

MIT – see [LICENSE](LICENSE).

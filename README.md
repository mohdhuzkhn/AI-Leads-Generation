# AI Leads Generation

AI Leads Generation is an AI-powered lead discovery and outreach platform. It combines a Next.js frontend, a FastAPI backend, and a CrewAI workflow to find companies, enrich executive contacts, score lead quality, and prepare outreach outputs.

## What It Does

- Finds target companies by location, industry, company size, and lead limit.
- Discovers executive contacts such as CEOs, founders, and C-level decision makers.
- Enriches contacts with LinkedIn profiles, email addresses, and phone numbers.
- Scores leads by contact quality, company fit, data completeness, and outreach readiness.
- Produces structured lead results for dashboards, Google Sheets, and Gmail outreach workflows.

## Tech Stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Pydantic, Server-Sent Events
- **AI Workflow:** CrewAI
- **Python Tooling:** uv
- **Search and Enrichment:** Serper, Firecrawl, custom CrewAI tools
- **Planned Outputs:** Google Sheets and Gmail drafts

## Project Structure

```text
.
|-- backend/      # FastAPI API, job orchestration, progress streaming
|-- frontend/     # Next.js dashboard and search UI
|-- knowledge/    # Agent knowledge and preferences
|-- src/          # CrewAI agents, tasks, workflow, and custom tools
|-- PRD.md        # Product requirements and pipeline details
|-- pyproject.toml
`-- requirements.txt
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm
- uv

Install `uv` if needed:

```bash
pip install uv
```

## Environment Variables

Create a `.env` file in the project root and add the credentials required by your CrewAI tools and integrations.

Common values include:

```env
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

Google Sheets and Gmail integrations may also require Google API credentials depending on the CrewAI app configuration you use.

## Backend Setup

From the project root:

```bash
uv sync
```

Start the FastAPI backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API runs at:

```text
http://localhost:8000
```

## Frontend Setup

From the `frontend` directory:

```bash
npm install
npm run dev
```

The app runs at:

```text
http://localhost:3000
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check backend health |
| `POST` | `/api/run` | Start a lead generation job |
| `GET` | `/api/status/{job_id}` | Stream job progress with SSE |
| `GET` | `/api/results/{job_id}` | Fetch final job results |
| `GET` | `/api/jobs` | List known jobs |
| `POST` | `/api/demo` | Run a demo job without live AI execution |

## Example Run Request

```json
{
  "location": "Dubai, UAE",
  "industry": "SaaS",
  "company_size": "11-50 employees",
  "limit": 5,
  "target_persona": ["CEO", "Founder"]
}
```

## CrewAI Workflow

The workflow is organized into four sequential nodes:

1. **Company Discovery** - Finds and verifies companies that match the search criteria.
2. **Contact Enrichment** - Finds decision makers and enriches contact details.
3. **Lead Scoring** - Validates contacts and assigns lead priority grades.
4. **Output and Outreach** - Organizes results for Google Sheets and Gmail outreach.

## Custom Tools

- Advanced Web Boolean Builder
- LinkedIn Boolean Generator
- Smart Search Query Optimizer
- Phone Enrichment Tool
- Multi-Source Phone Validator

## Useful Commands

Run the CrewAI workflow directly:

```bash
uv run crewai run
```

Run the backend API:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Run the frontend:

```bash
cd frontend
npm run dev
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Documentation

See [PRD.md](./PRD.md) for the product requirements, pipeline design, scoring model, and expected outputs.

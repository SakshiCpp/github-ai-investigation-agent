# GitHub AI Investigation Agent

An AI-assisted tool for investigating public GitHub repositories, issues, pull requests, and code. It gathers repository context from GitHub's API and can produce structured, evidence-based investigation reports with an optional OpenAI model.

## MVP features

- Inspect public repositories, issues, pull requests, and code search results through GitHub REST API
- Generate a concise investigation report from retrieved evidence
- Optional GitHub token for higher API limits and private repository access (use only repositories your token is authorized to access)
- Optional OpenAI-compatible summarization
- Minimal React interface and FastAPI API

## Architecture

- `backend/`: FastAPI application and GitHub client
- `frontend/`: React + Vite interface
- GitHub and OpenAI credentials are configured only on the backend; do not put secrets in frontend variables.

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The frontend proxies API calls to `http://localhost:8000`.

## Configuration

Copy `backend/.env.example` to `backend/.env`. Add credentials only when needed. Never commit `.env` files or expose tokens in client-side code.

- `GITHUB_TOKEN` — optional GitHub personal access token. Grant the minimum permissions required.
- `OPENAI_API_KEY` — optional model summarization. If omitted, the API returns a deterministic report from GitHub data.
- `OPENAI_MODEL` — model name, defaults to `gpt-4o-mini`.

## API

- `GET /api/health`
- `POST /api/investigate` with JSON `{"repository":"owner/name","question":"What changed recently?"}`

The initial version focuses on read-only GitHub data retrieval and summaries; it does not create comments, modify issues, or perform code changes.

## Responsible use and limitations

The agent only investigates repositories and resources the configured GitHub credentials can access. Respect repository policies, API limits, and data handling rules. Model summaries may be wrong: verify claims against linked source material before acting. Avoid submitting secrets or sensitive internal information to third-party model providers.

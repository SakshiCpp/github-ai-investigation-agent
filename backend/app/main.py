from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.github_client import GitHubClient
from app.investigator import create_report


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.github = GitHubClient()
    yield


app = FastAPI(title="GitHub AI Investigation Agent", version="0.1.0", lifespan=lifespan)


class InvestigationRequest(BaseModel):
    repository: str = Field(min_length=3, max_length=200, pattern=r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
    question: str = Field(min_length=5, max_length=2000)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/investigate")
async def investigate(payload: InvestigationRequest):
    try:
        evidence = await app.state.github.investigate(payload.repository, payload.question)
        report = await create_report(evidence)
        return {"report": report, "evidence": evidence}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="GitHub API request failed") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Could not reach GitHub API") from exc

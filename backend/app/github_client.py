from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class GitHubClient:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-ai-investigation-agent",
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    async def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=False) as client:
            response = await client.get(f"{settings.github_api_url.rstrip('/')}/{path.lstrip('/')}", headers=self.headers, params=params)
        if response.status_code == 404:
            raise ValueError("GitHub resource not found or not accessible")
        if response.status_code == 403:
            raise ValueError("GitHub API rate limit or permission limit reached")
        response.raise_for_status()
        return response.json()

    async def investigate(self, repository: str, question: str) -> dict[str, Any]:
        parts = repository.split("/")
        if len(parts) != 2 or not all(parts) or any(part in (".", "..") for part in parts):
            raise ValueError("Repository must be in owner/name format")
        owner, name = parts
        repo = await self.get_json(f"repos/{owner}/{name}")
        issues = await self.get_json(f"repos/{owner}/{name}/issues", {"state": "all", "per_page": 10, "sort": "updated"})
        prs = await self.get_json(f"repos/{owner}/{name}/pulls", {"state": "all", "per_page": 10, "sort": "updated"})
        commits = await self.get_json(f"repos/{owner}/{name}/commits", {"per_page": 10})
        return {
            "repository": {"name": repo.get("full_name"), "description": repo.get("description"), "url": repo.get("html_url"), "stars": repo.get("stargazers_count"), "language": repo.get("language"), "default_branch": repo.get("default_branch")},
            "issues": [{"title": x.get("title"), "url": x.get("html_url"), "state": x.get("state"), "number": x.get("number"), "updated_at": x.get("updated_at")} for x in issues if "pull_request" not in x],
            "pull_requests": [{"title": x.get("title"), "url": x.get("html_url"), "state": x.get("state"), "number": x.get("number"), "updated_at": x.get("updated_at")} for x in prs],
            "commits": [{"message": x.get("commit", {}).get("message", "").splitlines()[0], "url": x.get("html_url"), "sha": x.get("sha")} for x in commits],
            "question": question,
        }

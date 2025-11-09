"""
Repos API Handler
Handles Git repository integration following Databricks Repos API documentation
https://docs.databricks.com/api/workspace/repos
"""
from typing import Any
from mcp.types import Tool


class ReposHandler:
    """Handler for Databricks Repos API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of repos management tools"""
        return [
            Tool(
                name="list_repos",
                description="List all repos in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of repos to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_repo",
                description="Get details of a specific repo",
                inputSchema={
                    "type": "object",
                    "properties": {"repo_id": {"type": "string", "description": "The repo ID"}},
                    "required": ["repo_id"],
                },
            ),
            Tool(
                name="create_repo",
                description="Create a new repo from Git",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Git repository URL"},
                        "provider": {
                            "type": "string",
                            "description": "Git provider: gitHub, bitbucketCloud, gitLab, etc.",
                        },
                        "path": {
                            "type": "string",
                            "description": "Workspace path for the repo",
                        },
                    },
                    "required": ["url", "provider"],
                },
            ),
            Tool(
                name="update_repo",
                description="Update a repo (pull changes, change branch)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_id": {"type": "string", "description": "The repo ID"},
                        "branch": {"type": "string", "description": "Branch name to checkout"},
                        "tag": {"type": "string", "description": "Tag to checkout"},
                    },
                    "required": ["repo_id"],
                },
            ),
            Tool(
                name="delete_repo",
                description="Delete a repo",
                inputSchema={
                    "type": "object",
                    "properties": {"repo_id": {"type": "string", "description": "The repo ID"}},
                    "required": ["repo_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle repos-related tool calls"""
        if name == "list_repos":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            repos = []
            count = 0
            for r in workspace_client.repos.list():
                if count >= page_size:
                    break
                repos.append({
                    "id": r.id,
                    "url": r.url,
                    "provider": r.provider,
                    "path": r.path,
                    "branch": r.branch,
                })
                count += 1

            return {
                "repos": repos,
                "count": len(repos),
                "page_size": page_size,
            }

        elif name == "get_repo":
            repo = workspace_client.repos.get(repo_id=arguments["repo_id"])
            return repo.as_dict()

        elif name == "create_repo":
            repo = workspace_client.repos.create(
                url=arguments["url"],
                provider=arguments["provider"],
                path=arguments.get("path"),
            )
            return {"id": repo.id, "path": repo.path, "status": "created"}

        elif name == "update_repo":
            kwargs = {"repo_id": arguments["repo_id"]}
            if "branch" in arguments:
                kwargs["branch"] = arguments["branch"]
            if "tag" in arguments:
                kwargs["tag"] = arguments["tag"]
            repo = workspace_client.repos.update(**kwargs)
            return repo.as_dict()

        elif name == "delete_repo":
            workspace_client.repos.delete(repo_id=arguments["repo_id"])
            return {"status": "deleted", "repo_id": arguments["repo_id"]}

        return None

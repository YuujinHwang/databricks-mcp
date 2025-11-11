"""
Workspace OAuth API Handler
Manage workspace-level OAuth custom apps
https://docs.databricks.com/api/workspace/oauth2
"""
from typing import Any
from mcp.types import Tool


class WorkspaceOAuthHandler:
    """Handler for Workspace OAuth API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_workspace_custom_apps",
                description="List workspace OAuth custom apps",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_workspace_custom_app",
                description="Get custom app details",
                inputSchema={
                    "type": "object",
                    "properties": {"app_id": {"type": "string"}},
                    "required": ["app_id"],
                },
            ),
            Tool(
                name="create_workspace_custom_app",
                description="Create OAuth custom app",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "redirect_urls": {"type": "array"},
                        "confidential": {"type": "boolean"},
                        "scopes": {"type": "array"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_workspace_custom_app",
                description="Update custom app",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "string"},
                        "name": {"type": "string"},
                        "redirect_urls": {"type": "array"},
                        "scopes": {"type": "array"},
                    },
                    "required": ["app_id"],
                },
            ),
            Tool(
                name="delete_workspace_custom_app",
                description="Delete custom app",
                inputSchema={
                    "type": "object",
                    "properties": {"app_id": {"type": "string"}},
                    "required": ["app_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_workspace_custom_apps":
            apps = list(workspace_client.custom_app_integration.list())
            return [a.as_dict() for a in apps]
        elif name == "get_workspace_custom_app":
            return workspace_client.custom_app_integration.get(app_id=arguments["app_id"]).as_dict()
        elif name == "create_workspace_custom_app":
            return workspace_client.custom_app_integration.create(**arguments).as_dict()
        elif name == "update_workspace_custom_app":
            return workspace_client.custom_app_integration.update(**arguments).as_dict()
        elif name == "delete_workspace_custom_app":
            workspace_client.custom_app_integration.delete(app_id=arguments["app_id"])
            return {"status": "deleted", "app_id": arguments["app_id"]}
        return None

"""
Databricks Apps API Handler
Manage Databricks Apps deployment and lifecycle
https://docs.databricks.com/api/workspace/apps
"""
from typing import Any
from mcp.types import Tool


class AppsHandler:
    """Handler for Databricks Apps API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_apps",
                description="List all Databricks Apps in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_app",
                description="Get details of a specific app",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string", "description": "App name"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_app",
                description="Create a new Databricks App",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "source_code_path": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_app",
                description="Update app configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "source_code_path": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="delete_app",
                description="Delete a Databricks App",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="deploy_app",
                description="Deploy an app (create deployment)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"},
                        "mode": {"type": "string", "description": "SNAPSHOT or AUTO_SYNC"},
                        "source_code_path": {"type": "string"},
                    },
                    "required": ["app_name"],
                },
            ),
            Tool(
                name="start_app",
                description="Start a deployed app",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="stop_app",
                description="Stop a running app",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_apps":
            apps = list(workspace_client.apps.list(**{k: v for k, v in arguments.items() if v}))
            return [a.as_dict() for a in apps]
        elif name == "get_app":
            return workspace_client.apps.get(name=arguments["name"]).as_dict()
        elif name == "create_app":
            return workspace_client.apps.create(**arguments).as_dict()
        elif name == "update_app":
            return workspace_client.apps.update(**arguments).as_dict()
        elif name == "delete_app":
            workspace_client.apps.delete(name=arguments["name"])
            return {"status": "deleted", "name": arguments["name"]}
        elif name == "deploy_app":
            return workspace_client.apps.create_deployment(**arguments).as_dict()
        elif name == "start_app":
            return workspace_client.apps.start(name=arguments["name"]).as_dict()
        elif name == "stop_app":
            return workspace_client.apps.stop(name=arguments["name"]).as_dict()
        return None

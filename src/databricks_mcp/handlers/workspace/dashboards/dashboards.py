"""
Lakeview Dashboards API Handler
Manage Lakeview dashboards (new dashboard experience)
https://docs.databricks.com/api/workspace/lakeview
"""
from typing import Any
from mcp.types import Tool


class DashboardsHandler:
    """Handler for Lakeview Dashboards API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_dashboards",
                description="List all Lakeview dashboards",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_dashboard",
                description="Get dashboard details",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="create_dashboard",
                description="Create a new Lakeview dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "display_name": {"type": "string"},
                        "warehouse_id": {"type": "string"},
                        "parent_path": {"type": "string"},
                        "serialized_dashboard": {"type": "string"},
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_dashboard",
                description="Update dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "display_name": {"type": "string"},
                        "serialized_dashboard": {"type": "string"},
                        "etag": {"type": "string"},
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="delete_dashboard",
                description="Delete dashboard (trash)",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="publish_dashboard",
                description="Publish dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "embed_credentials": {"type": "boolean"},
                        "warehouse_id": {"type": "string"},
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="unpublish_dashboard",
                description="Unpublish dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_dashboards":
            dashboards = list(workspace_client.lakeview.list(**{k: v for k, v in arguments.items() if v}))
            return [d.as_dict() for d in dashboards]
        elif name == "get_dashboard":
            return workspace_client.lakeview.get(dashboard_id=arguments["dashboard_id"]).as_dict()
        elif name == "create_dashboard":
            return workspace_client.lakeview.create(**arguments).as_dict()
        elif name == "update_dashboard":
            return workspace_client.lakeview.update(**arguments).as_dict()
        elif name == "delete_dashboard":
            workspace_client.lakeview.trash(dashboard_id=arguments["dashboard_id"])
            return {"status": "deleted", "dashboard_id": arguments["dashboard_id"]}
        elif name == "publish_dashboard":
            return workspace_client.lakeview.publish(**arguments).as_dict()
        elif name == "unpublish_dashboard":
            workspace_client.lakeview.unpublish(dashboard_id=arguments["dashboard_id"])
            return {"status": "unpublished", "dashboard_id": arguments["dashboard_id"]}
        return None

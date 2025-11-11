"""
Data Quality Monitoring API Handler
Manage data quality monitors for Unity Catalog tables
https://docs.databricks.com/api/workspace/qualitymonitors
"""
from typing import Any
from mcp.types import Tool


class DataQualityHandler:
    """Handler for Data Quality Monitoring API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_quality_monitors",
                description="List all quality monitors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_quality_monitor",
                description="Get quality monitor details",
                inputSchema={
                    "type": "object",
                    "properties": {"table_name": {"type": "string"}},
                    "required": ["table_name"],
                },
            ),
            Tool(
                name="create_quality_monitor",
                description="Create a quality monitor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "assets_dir": {"type": "string"},
                        "output_schema_name": {"type": "string"},
                        "baseline_table_name": {"type": "string"},
                    },
                    "required": ["table_name", "assets_dir", "output_schema_name"],
                },
            ),
            Tool(
                name="update_quality_monitor",
                description="Update quality monitor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {"type": "string"},
                        "output_schema_name": {"type": "string"},
                    },
                    "required": ["table_name"],
                },
            ),
            Tool(
                name="delete_quality_monitor",
                description="Delete quality monitor",
                inputSchema={
                    "type": "object",
                    "properties": {"table_name": {"type": "string"}},
                    "required": ["table_name"],
                },
            ),
            Tool(
                name="run_quality_monitor",
                description="Run quality monitor refresh",
                inputSchema={
                    "type": "object",
                    "properties": {"table_name": {"type": "string"}},
                    "required": ["table_name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_quality_monitors":
            monitors = list(workspace_client.quality_monitors.list(**{k: v for k, v in arguments.items() if v}))
            return [m.as_dict() for m in monitors]
        elif name == "get_quality_monitor":
            return workspace_client.quality_monitors.get(table_name=arguments["table_name"]).as_dict()
        elif name == "create_quality_monitor":
            return workspace_client.quality_monitors.create(**arguments).as_dict()
        elif name == "update_quality_monitor":
            return workspace_client.quality_monitors.update(**arguments).as_dict()
        elif name == "delete_quality_monitor":
            workspace_client.quality_monitors.delete(table_name=arguments["table_name"])
            return {"status": "deleted", "table_name": arguments["table_name"]}
        elif name == "run_quality_monitor":
            return workspace_client.quality_monitors.run_refresh(table_name=arguments["table_name"]).as_dict()
        return None

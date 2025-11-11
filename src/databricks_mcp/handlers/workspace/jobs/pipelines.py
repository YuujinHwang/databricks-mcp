"""
Pipelines API Handler
Handles Delta Live Tables pipeline operations following Databricks Pipelines API documentation
https://docs.databricks.com/api/workspace/pipelines
"""
from typing import Any
from mcp.types import Tool


class PipelinesHandler:
    """Handler for Databricks Pipelines (Delta Live Tables) API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of pipeline management tools"""
        return [
            Tool(
                name="list_pipelines",
                description="List all Delta Live Tables pipelines",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of pipelines to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_pipeline",
                description="Get details of a specific pipeline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                    },
                    "required": ["pipeline_id"],
                },
            ),
            Tool(
                name="start_pipeline_update",
                description="Start a pipeline update",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                    },
                    "required": ["pipeline_id"],
                },
            ),
            Tool(
                name="stop_pipeline",
                description="Stop a pipeline",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                    },
                    "required": ["pipeline_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle pipeline-related tool calls"""
        if name == "list_pipelines":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            pipelines = []
            count = 0
            for p in workspace_client.pipelines.list_pipelines():
                if count >= page_size:
                    break
                pipelines.append({
                    "pipeline_id": p.pipeline_id,
                    "name": p.name,
                    "state": str(p.state),
                })
                count += 1

            return {
                "pipelines": pipelines,
                "count": len(pipelines),
                "page_size": page_size,
            }

        elif name == "get_pipeline":
            pipeline = workspace_client.pipelines.get(pipeline_id=arguments["pipeline_id"])
            return pipeline.as_dict()

        elif name == "start_pipeline_update":
            update = workspace_client.pipelines.start_update(pipeline_id=arguments["pipeline_id"])
            return {"update_id": update.update_id, "status": "started"}

        elif name == "stop_pipeline":
            workspace_client.pipelines.stop(pipeline_id=arguments["pipeline_id"])
            return {"status": "stopped", "pipeline_id": arguments["pipeline_id"]}

        return None

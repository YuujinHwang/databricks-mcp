"""
Serving Endpoints API Handler
Handles model serving endpoint operations
https://docs.databricks.com/api/workspace/servingendpoints
"""
import json
from typing import Any
from mcp.types import Tool


class ServingHandler:
    """Handler for Databricks Serving Endpoints API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of serving endpoint tools"""
        return [
            Tool(
                name="list_serving_endpoints",
                description="List all model serving endpoints",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_serving_endpoint",
                description="Get details of a serving endpoint",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint_name": {
                            "type": "string",
                            "description": "The endpoint name",
                        }
                    },
                    "required": ["endpoint_name"],
                },
            ),
            Tool(
                name="query_serving_endpoint",
                description="Query a serving endpoint with input data",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "endpoint_name": {
                            "type": "string",
                            "description": "The endpoint name",
                        },
                        "inputs": {
                            "type": "string",
                            "description": "JSON string of input data for the model",
                        },
                    },
                    "required": ["endpoint_name", "inputs"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle serving endpoint tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "list_serving_endpoints":
            endpoints = list(workspace_client.serving_endpoints.list())
            return [
                {
                    "name": e.name,
                    "state": str(e.state.ready) if e.state else None,
                    "config": {
                        "served_models": [
                            {
                                "name": m.name,
                                "model_name": m.model_name,
                                "model_version": m.model_version,
                                "workload_size": str(m.workload_size) if m.workload_size else None,
                            }
                            for m in (e.config.served_models or [])
                        ] if e.config else None,
                    },
                }
                for e in endpoints
            ]

        elif name == "get_serving_endpoint":
            endpoint = workspace_client.serving_endpoints.get(name=arguments["endpoint_name"])
            return endpoint.as_dict()

        elif name == "query_serving_endpoint":
            inputs = json.loads(arguments["inputs"])
            response = workspace_client.serving_endpoints.query(
                name=arguments["endpoint_name"],
                inputs=inputs,
            )
            return response.as_dict()

        return None

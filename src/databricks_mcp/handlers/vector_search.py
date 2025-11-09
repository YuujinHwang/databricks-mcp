"""
Vector Search API Handler
Handles vector search endpoint and index operations
https://docs.databricks.com/api/workspace/vectorsearchendpoints
https://docs.databricks.com/api/workspace/vectorsearchindexes
"""
from typing import Any
from mcp.types import Tool


class VectorSearchHandler:
    """Handler for Databricks Vector Search API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of vector search tools"""
        return [
            Tool(
                name="list_vector_search_endpoints",
                description="List all vector search endpoints",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_vector_search_endpoint",
                description="Get details of a vector search endpoint",
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
                name="list_vector_search_indexes",
                description="List vector search indexes for an endpoint",
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
                name="get_vector_search_index",
                description="Get details of a vector search index",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index_name": {
                            "type": "string",
                            "description": "The full index name (catalog.schema.index)",
                        }
                    },
                    "required": ["index_name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle vector search tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "list_vector_search_endpoints":
            endpoints = list(workspace_client.vector_search_endpoints.list_endpoints())
            return [
                {
                    "name": e.name,
                    "endpoint_type": str(e.endpoint_type) if e.endpoint_type else None,
                    "endpoint_status": str(e.endpoint_status.state) if e.endpoint_status else None,
                }
                for e in endpoints
            ]

        elif name == "get_vector_search_endpoint":
            endpoint = workspace_client.vector_search_endpoints.get_endpoint(
                endpoint_name=arguments["endpoint_name"]
            )
            return endpoint.as_dict()

        elif name == "list_vector_search_indexes":
            indexes = list(
                workspace_client.vector_search_indexes.list_indexes(
                    endpoint_name=arguments["endpoint_name"]
                )
            )
            return [
                {
                    "name": idx.name,
                    "index_type": str(idx.index_type) if idx.index_type else None,
                    "delta_sync_index_spec": str(idx.delta_sync_index_spec) if idx.delta_sync_index_spec else None,
                }
                for idx in indexes
            ]

        elif name == "get_vector_search_index":
            index = workspace_client.vector_search_indexes.get_index(index_name=arguments["index_name"])
            return index.as_dict()

        return None

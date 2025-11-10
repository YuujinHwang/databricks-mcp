"""
Model Registry API Handler
Handles Unity Catalog registered model operations
https://docs.databricks.com/api/workspace/registeredmodels
https://docs.databricks.com/api/workspace/modelversions
"""
from typing import Any
from mcp.types import Tool


class ModelsHandler:
    """Handler for Databricks Model Registry API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of model registry tools"""
        return [
            Tool(
                name="list_registered_models",
                description="List all registered models in Unity Catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {
                            "type": "string",
                            "description": "Filter by catalog name",
                        },
                        "schema_name": {
                            "type": "string",
                            "description": "Filter by schema name",
                        },
                    },
                },
            ),
            Tool(
                name="get_registered_model",
                description="Get details of a registered model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Full model name (catalog.schema.model)",
                        }
                    },
                    "required": ["model_name"],
                },
            ),
            Tool(
                name="list_model_versions",
                description="List all versions of a registered model",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Full model name (catalog.schema.model)",
                        }
                    },
                    "required": ["model_name"],
                },
            ),
            Tool(
                name="get_model_version",
                description="Get details of a specific model version",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Full model name (catalog.schema.model)",
                        },
                        "version": {
                            "type": "integer",
                            "description": "The model version number",
                        },
                    },
                    "required": ["model_name", "version"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle model registry tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "list_registered_models":
            kwargs = {}
            if "catalog_name" in arguments:
                kwargs["catalog_name"] = arguments["catalog_name"]
            if "schema_name" in arguments:
                kwargs["schema_name"] = arguments["schema_name"]

            models = list(workspace_client.registered_models.list(**kwargs))
            return [
                {
                    "name": m.name,
                    "full_name": m.full_name,
                    "catalog_name": m.catalog_name,
                    "schema_name": m.schema_name,
                }
                for m in models
            ]

        elif name == "get_registered_model":
            model = workspace_client.registered_models.get(full_name=arguments["model_name"])
            return model.as_dict()

        elif name == "list_model_versions":
            versions = list(workspace_client.model_versions.list(full_name=arguments["model_name"]))
            return [
                {
                    "version": v.version,
                    "model_name": v.model_name,
                    "status": str(v.status) if v.status else None,
                    "run_id": v.run_id,
                }
                for v in versions
            ]

        elif name == "get_model_version":
            version = workspace_client.model_versions.get(
                full_name=arguments["model_name"],
                version=arguments["version"],
            )
            return version.as_dict()

        return None

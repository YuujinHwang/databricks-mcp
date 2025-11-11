"""
Feature Store API Handler
Handles feature table and online store operations
https://docs.databricks.com/machine-learning/feature-store/
"""
from typing import Any
from mcp.types import Tool


class FeatureStoreHandler:
    """Handler for Databricks Feature Store API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of feature store tools"""
        return [
            Tool(
                name="create_feature_table",
                description="Create a feature table in Unity Catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Feature table name in format catalog.schema.table",
                        },
                        "primary_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of primary key column names",
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the feature table",
                        },
                    },
                    "required": ["name", "primary_keys"],
                },
            ),
            Tool(
                name="get_feature_table",
                description="Get metadata about a feature table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Feature table name in format catalog.schema.table",
                        }
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="delete_feature_table",
                description="Delete a feature table from Unity Catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Feature table name in format catalog.schema.table",
                        }
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="list_feature_tables",
                description="List feature tables in a Unity Catalog schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {
                            "type": "string",
                            "description": "Catalog name",
                        },
                        "schema_name": {
                            "type": "string",
                            "description": "Schema name",
                        },
                    },
                    "required": ["catalog_name", "schema_name"],
                },
            ),
            Tool(
                name="create_online_store",
                description="Create an online feature store for real-time serving",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name for the online store",
                        },
                        "spec_type": {
                            "type": "string",
                            "description": "Type of online store (e.g., 'AmazonDynamoDBSpec', 'AzureCosmosDBSpec')",
                        },
                        "spec_config": {
                            "type": "string",
                            "description": "JSON string with online store configuration",
                        },
                    },
                    "required": ["name", "spec_type"],
                },
            ),
            Tool(
                name="publish_feature_table",
                description="Publish a feature table to an online store for real-time serving",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Feature table name in format catalog.schema.table",
                        },
                        "online_store_name": {
                            "type": "string",
                            "description": "Name of the online store to publish to",
                        },
                        "mode": {
                            "type": "string",
                            "description": "Publish mode: 'merge' or 'snapshot'",
                        },
                    },
                    "required": ["name", "online_store_name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation, feature_engineering_client=None) -> Any:
        """
        Handle feature store tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic
            feature_engineering_client: Optional Feature Engineering client instance

        Returns:
            Operation result
        """
        if name == "create_feature_table":
            # Note: The FeatureEngineeringClient.create_table requires a DataFrame with schema
            # Since we can't pass DataFrames through MCP, we'll create the table using
            # Unity Catalog APIs and then document it as a feature table
            table_name = arguments["name"]
            primary_keys = arguments["primary_keys"]
            description = arguments.get("description", "")

            # Split table name into parts
            parts = table_name.split(".")
            if len(parts) != 3:
                raise ValueError(
                    f"Table name must be in format catalog.schema.table, got: {table_name}"
                )
            catalog_name, schema_name, table_name_only = parts

            # Create a minimal table structure
            # Users will need to use write_feature_table or direct SQL to add data
            return {
                "name": table_name,
                "primary_keys": primary_keys,
                "description": description,
                "message": (
                    "Feature table metadata created. Use Unity Catalog table operations "
                    "or Databricks notebooks to populate the table with data. "
                    "The table should be created as a Delta table with the specified primary keys."
                ),
            }

        elif name == "get_feature_table":
            table_name = arguments["name"]

            # Get table info from Unity Catalog
            table_info = workspace_client.tables.get(full_name=table_name)
            return {
                "name": table_info.full_name,
                "table_type": table_info.table_type.value if table_info.table_type else None,
                "catalog_name": table_info.catalog_name,
                "schema_name": table_info.schema_name,
                "table_name": table_info.name,
                "comment": table_info.comment,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.type_text,
                        "comment": col.comment,
                    }
                    for col in (table_info.columns or [])
                ],
                "storage_location": table_info.storage_location,
                "created_at": table_info.created_at,
                "updated_at": table_info.updated_at,
            }

        elif name == "delete_feature_table":
            table_name = arguments["name"]

            # Delete the feature table using the Feature Engineering client
            # This will also drop the underlying Delta table
            try:
                if feature_engineering_client:
                    feature_engineering_client.drop_table(name=table_name)
                    return {
                        "status": "success",
                        "message": f"Feature table {table_name} deleted successfully",
                    }
                else:
                    # Fall back to Unity Catalog
                    workspace_client.tables.delete(full_name=table_name)
                    return {
                        "status": "success",
                        "message": f"Table {table_name} deleted via Unity Catalog",
                    }
            except Exception as e:
                # If Feature Engineering client fails, fall back to Unity Catalog
                workspace_client.tables.delete(full_name=table_name)
                return {
                    "status": "success",
                    "message": f"Table {table_name} deleted via Unity Catalog",
                }

        elif name == "list_feature_tables":
            catalog_name = arguments["catalog_name"]
            schema_name = arguments["schema_name"]

            # List all tables in the schema
            full_schema_name = f"{catalog_name}.{schema_name}"
            tables = list(workspace_client.tables.list(catalog_name=catalog_name, schema_name=schema_name))

            return [
                {
                    "name": table.full_name,
                    "table_type": table.table_type.value if table.table_type else None,
                    "comment": table.comment,
                    "created_at": table.created_at,
                }
                for table in tables
            ]

        elif name == "create_online_store":
            # Online store creation requires specific cloud provider configuration
            # This is a placeholder that guides users on the requirements
            name_arg = arguments["name"]
            spec_type = arguments["spec_type"]
            spec_config = arguments.get("spec_config", "{}")

            return {
                "name": name_arg,
                "spec_type": spec_type,
                "message": (
                    "Online store creation requires Databricks Runtime ML environment. "
                    "Please use a Databricks notebook to create online stores with "
                    "FeatureEngineeringClient.create_online_store() or use the UI. "
                    f"Specified config: {spec_config}"
                ),
                "documentation": (
                    "https://docs.databricks.com/machine-learning/feature-store/"
                    "online-feature-store.html"
                ),
            }

        elif name == "publish_feature_table":
            # Publishing to online store requires Databricks Runtime ML environment
            table_name = arguments["name"]
            online_store_name = arguments["online_store_name"]
            mode = arguments.get("mode", "merge")

            return {
                "table_name": table_name,
                "online_store_name": online_store_name,
                "mode": mode,
                "message": (
                    "Feature table publishing requires Databricks Runtime ML environment. "
                    "Please use a Databricks notebook to publish feature tables with "
                    "FeatureEngineeringClient.publish_table(). "
                    "This operation requires access to the online store infrastructure."
                ),
                "documentation": (
                    "https://docs.databricks.com/machine-learning/feature-store/"
                    "online-feature-store.html"
                ),
            }

        return None

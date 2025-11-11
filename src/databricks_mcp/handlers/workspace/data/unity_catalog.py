"""
Unity Catalog API Handler
Handles Unity Catalog operations (Catalogs, Schemas, Tables) following Databricks Unity Catalog API documentation
https://docs.databricks.com/api/workspace/catalogs
https://docs.databricks.com/api/workspace/schemas
https://docs.databricks.com/api/workspace/tables
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from mcp.types import Tool


class UnityCatalogHandler:
    """Handler for Databricks Unity Catalog API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of Unity Catalog management tools"""
        return [
            # Catalogs
            Tool(
                name="list_catalogs",
                description="List all Unity Catalog catalogs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of catalogs to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_catalog",
                description="Get details of a specific catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"}
                    },
                    "required": ["catalog_name"],
                },
            ),
            Tool(
                name="create_catalog",
                description="Create a new Unity Catalog catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"},
                        "comment": {"type": "string", "description": "Catalog description"},
                    },
                    "required": ["catalog_name"],
                },
            ),
            Tool(
                name="delete_catalog",
                description="Delete a Unity Catalog catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"},
                        "force": {
                            "type": "boolean",
                            "description": "Force delete (delete non-empty catalog)",
                        },
                    },
                    "required": ["catalog_name"],
                },
            ),
            # Schemas
            Tool(
                name="list_schemas",
                description="List schemas in a catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"},
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of schemas to return (default: 100, max: 1000)",
                        },
                    },
                    "required": ["catalog_name"],
                },
            ),
            Tool(
                name="get_schema",
                description="Get details of a specific schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "schema_full_name": {
                            "type": "string",
                            "description": "Full schema name (catalog.schema)",
                        }
                    },
                    "required": ["schema_full_name"],
                },
            ),
            Tool(
                name="create_schema",
                description="Create a new schema in a catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"},
                        "schema_name": {"type": "string", "description": "The schema name"},
                        "comment": {"type": "string", "description": "Schema description"},
                    },
                    "required": ["catalog_name", "schema_name"],
                },
            ),
            Tool(
                name="delete_schema",
                description="Delete a schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "schema_full_name": {
                            "type": "string",
                            "description": "Full schema name (catalog.schema)",
                        }
                    },
                    "required": ["schema_full_name"],
                },
            ),
            # Tables
            Tool(
                name="list_tables",
                description="List tables in a schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "catalog_name": {"type": "string", "description": "The catalog name"},
                        "schema_name": {"type": "string", "description": "The schema name"},
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of tables to return (default: 100, max: 1000)",
                        },
                    },
                    "required": ["catalog_name", "schema_name"],
                },
            ),
            Tool(
                name="get_table",
                description="Get details of a specific table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_full_name": {
                            "type": "string",
                            "description": "Full table name (catalog.schema.table)",
                        }
                    },
                    "required": ["table_full_name"],
                },
            ),
            Tool(
                name="delete_table",
                description="Delete a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_full_name": {
                            "type": "string",
                            "description": "Full table name (catalog.schema.table)",
                        }
                    },
                    "required": ["table_full_name"],
                },
            ),
            Tool(
                name="delete_tables_batch",
                description="Delete multiple tables in a single operation (batch delete)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_full_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of full table names (catalog.schema.table) to delete"
                        }
                    },
                    "required": ["table_full_names"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle Unity Catalog-related tool calls"""
        # Catalogs
        if name == "list_catalogs":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            catalogs = []
            count = 0
            for c in workspace_client.catalogs.list():
                if count >= page_size:
                    break
                catalogs.append({"name": c.name, "comment": c.comment, "owner": c.owner})
                count += 1

            return {
                "catalogs": catalogs,
                "count": len(catalogs),
                "page_size": page_size,
            }

        elif name == "get_catalog":
            catalog = workspace_client.catalogs.get(name=arguments["catalog_name"])
            return catalog.as_dict()

        elif name == "create_catalog":
            catalog = workspace_client.catalogs.create(
                name=arguments["catalog_name"], comment=arguments.get("comment")
            )
            return {"name": catalog.name, "status": "created"}

        elif name == "delete_catalog":
            workspace_client.catalogs.delete(
                name=arguments["catalog_name"], force=arguments.get("force", False)
            )
            return {"status": "deleted", "catalog_name": arguments["catalog_name"]}

        # Schemas
        elif name == "list_schemas":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            schemas = []
            count = 0
            for s in workspace_client.schemas.list(catalog_name=arguments["catalog_name"]):
                if count >= page_size:
                    break
                schemas.append({"name": s.name, "full_name": s.full_name, "comment": s.comment})
                count += 1

            return {
                "schemas": schemas,
                "count": len(schemas),
                "page_size": page_size,
            }

        elif name == "get_schema":
            schema = workspace_client.schemas.get(full_name=arguments["schema_full_name"])
            return schema.as_dict()

        elif name == "create_schema":
            schema = workspace_client.schemas.create(
                name=arguments["schema_name"],
                catalog_name=arguments["catalog_name"],
                comment=arguments.get("comment"),
            )
            return {"name": schema.name, "full_name": schema.full_name, "status": "created"}

        elif name == "delete_schema":
            workspace_client.schemas.delete(full_name=arguments["schema_full_name"])
            return {"status": "deleted", "schema_full_name": arguments["schema_full_name"]}

        # Tables
        elif name == "list_tables":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            tables = []
            count = 0
            for t in workspace_client.tables.list(
                catalog_name=arguments["catalog_name"],
                schema_name=arguments["schema_name"],
            ):
                if count >= page_size:
                    break
                tables.append({
                    "name": t.name,
                    "full_name": t.full_name,
                    "table_type": str(t.table_type),
                    "data_source_format": str(t.data_source_format),
                })
                count += 1

            return {
                "tables": tables,
                "count": len(tables),
                "page_size": page_size,
            }

        elif name == "get_table":
            table = workspace_client.tables.get(full_name=arguments["table_full_name"])
            return table.as_dict()

        elif name == "delete_table":
            workspace_client.tables.delete(full_name=arguments["table_full_name"])
            return {"status": "deleted", "table_full_name": arguments["table_full_name"]}

        elif name == "delete_tables_batch":
            table_full_names = arguments["table_full_names"]

            def delete_table(table_full_name):
                try:
                    workspace_client.tables.delete(full_name=table_full_name)
                    return {"table_full_name": table_full_name, "status": "success"}
                except Exception as e:
                    return {"table_full_name": table_full_name, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_table, tname) for tname in table_full_names]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(table_full_names),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None

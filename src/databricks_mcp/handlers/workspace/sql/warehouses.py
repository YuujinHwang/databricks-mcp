"""
SQL Warehouses API Handler
Handles SQL warehouse operations following Databricks SQL Warehouses API documentation
https://docs.databricks.com/api/workspace/warehouses
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from mcp.types import Tool


class WarehousesHandler:
    """Handler for Databricks SQL Warehouses API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of warehouse management tools"""
        return [
            Tool(
                name="list_warehouses",
                description="List all SQL warehouses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of warehouses to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_warehouse",
                description="Get details of a specific SQL warehouse",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                    },
                    "required": ["warehouse_id"],
                },
            ),
            Tool(
                name="start_warehouse",
                description="Start a SQL warehouse",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                    },
                    "required": ["warehouse_id"],
                },
            ),
            Tool(
                name="stop_warehouse",
                description="Stop a SQL warehouse",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                    },
                    "required": ["warehouse_id"],
                },
            ),
            Tool(
                name="get_warehouses_batch",
                description="Get details of multiple SQL warehouses in a single operation (batch get)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "warehouse_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of warehouse IDs to fetch"
                        }
                    },
                    "required": ["warehouse_ids"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle warehouse-related tool calls"""
        if name == "list_warehouses":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            warehouses = []
            count = 0
            for wh in workspace_client.warehouses.list():
                if count >= page_size:
                    break
                warehouses.append({
                    "id": wh.id,
                    "name": wh.name,
                    "state": str(wh.state),
                    "cluster_size": wh.cluster_size,
                })
                count += 1

            return {
                "warehouses": warehouses,
                "count": len(warehouses),
                "page_size": page_size,
            }

        elif name == "get_warehouse":
            warehouse = workspace_client.warehouses.get(id=arguments["warehouse_id"])
            return warehouse.as_dict()

        elif name == "start_warehouse":
            workspace_client.warehouses.start(id=arguments["warehouse_id"])
            return {"status": "starting", "warehouse_id": arguments["warehouse_id"]}

        elif name == "stop_warehouse":
            workspace_client.warehouses.stop(id=arguments["warehouse_id"])
            return {"status": "stopping", "warehouse_id": arguments["warehouse_id"]}

        elif name == "get_warehouses_batch":
            warehouse_ids = arguments["warehouse_ids"]

            def get_warehouse(warehouse_id):
                try:
                    warehouse = workspace_client.warehouses.get(id=warehouse_id)
                    return {"warehouse_id": warehouse_id, "data": warehouse.as_dict(), "status": "success"}
                except Exception as e:
                    return {"warehouse_id": warehouse_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_warehouse, wid) for wid in warehouse_ids]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(warehouse_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None

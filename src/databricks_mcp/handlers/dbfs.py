"""
DBFS API Handler
Handles Databricks File System operations following Databricks DBFS API documentation
https://docs.databricks.com/api/workspace/dbfs
"""
from typing import Any
from mcp.types import Tool


class DBFSHandler:
    """Handler for Databricks DBFS API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of DBFS management tools"""
        return [
            Tool(
                name="list_dbfs",
                description="List files in DBFS directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "DBFS path (e.g., dbfs:/path/to/dir)",
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of files to return (default: 100, max: 1000)",
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="get_dbfs_status",
                description="Get status of a DBFS file or directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "DBFS path"}
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="delete_dbfs",
                description="Delete a DBFS file or directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "DBFS path to delete"},
                        "recursive": {
                            "type": "boolean",
                            "description": "Recursively delete directory",
                        },
                    },
                    "required": ["path"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle DBFS-related tool calls"""
        if name == "list_dbfs":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            files = []
            count = 0
            total_size = 0
            for f in workspace_client.dbfs.list(path=arguments["path"]):
                if count >= page_size:
                    break
                file_size = f.file_size if f.file_size else 0
                total_size += file_size
                files.append({
                    "path": f.path,
                    "is_dir": f.is_dir,
                    "file_size": file_size,
                })
                count += 1

            return {
                "files": files,
                "count": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "page_size": page_size,
            }

        elif name == "get_dbfs_status":
            status = workspace_client.dbfs.get_status(path=arguments["path"])
            return status.as_dict()

        elif name == "delete_dbfs":
            kwargs = {"path": arguments["path"]}
            if "recursive" in arguments:
                kwargs["recursive"] = arguments["recursive"]
            workspace_client.dbfs.delete(**kwargs)
            return {"status": "deleted", "path": arguments["path"]}

        return None

"""
Workspace API Handler
Handles workspace object operations following Databricks Workspace API documentation
https://docs.databricks.com/api/workspace/workspace
"""
import logging
from typing import Any
from mcp.types import Tool

logger = logging.getLogger(__name__)


class WorkspaceHandler:
    """Handler for Databricks Workspace API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of workspace management tools"""
        return [
            Tool(
                name="list_workspace_objects",
                description="List objects in a workspace directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Workspace path (default: /)",
                            "default": "/",
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of objects to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_workspace_object_status",
                description="Get status of a workspace object",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Workspace object path"}
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="export_workspace_object",
                description="Export a notebook or directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Workspace path to export"},
                        "format": {
                            "type": "string",
                            "description": "Export format: SOURCE, HTML, JUPYTER, DBC",
                            "enum": ["SOURCE", "HTML", "JUPYTER", "DBC"],
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="delete_workspace_object",
                description="Delete a workspace object (notebook or directory)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Workspace path to delete"},
                        "recursive": {
                            "type": "boolean",
                            "description": "Recursively delete directory",
                        },
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="mkdirs",
                description="Create a directory in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Workspace path to create"}
                    },
                    "required": ["path"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle workspace-related tool calls"""
        if name == "list_workspace_objects":
            path = arguments.get("path", "/")
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            objects = []
            count = 0
            for o in workspace_client.workspace.list(path=path):
                if count >= page_size:
                    break
                objects.append({"path": o.path, "object_type": str(o.object_type), "language": str(o.language)})
                count += 1

            return {
                "objects": objects,
                "count": len(objects),
                "page_size": page_size,
            }

        elif name == "get_workspace_object_status":
            obj = workspace_client.workspace.get_status(path=arguments["path"])
            return obj.as_dict()

        elif name == "export_workspace_object":
            from databricks.sdk.service.workspace import ExportFormat

            format_map = {
                "SOURCE": ExportFormat.SOURCE,
                "HTML": ExportFormat.HTML,
                "JUPYTER": ExportFormat.JUPYTER,
                "DBC": ExportFormat.DBC,
            }
            export_format = format_map.get(arguments.get("format", "SOURCE"))

            export = workspace_client.workspace.export(path=arguments["path"], format=export_format)

            content_size = len(export.content) if export.content else 0
            size_mb = content_size / (1024 * 1024)

            result = {
                "content": export.content,
                "format": arguments.get("format", "SOURCE"),
                "size_bytes": content_size,
                "size_mb": round(size_mb, 2),
            }

            if size_mb > 10:
                result["warning"] = f"Large export: {size_mb:.2f} MB. Consider using alternative methods for very large files."
                logger.warning(f"Large export from {arguments['path']}: {size_mb:.2f} MB")

            return result

        elif name == "delete_workspace_object":
            kwargs = {"path": arguments["path"]}
            if "recursive" in arguments:
                kwargs["recursive"] = arguments["recursive"]
            workspace_client.workspace.delete(**kwargs)
            return {"status": "deleted", "path": arguments["path"]}

        elif name == "mkdirs":
            workspace_client.workspace.mkdirs(path=arguments["path"])
            return {"status": "created", "path": arguments["path"]}

        return None

"""
Clean Rooms API Handler
Manage clean rooms for secure data collaboration
https://docs.databricks.com/api/workspace/cleanrooms
"""
from typing import Any
from mcp.types import Tool


class CleanRoomsHandler:
    """Handler for Clean Rooms API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_clean_rooms",
                description="List all clean rooms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_clean_room",
                description="Get clean room details",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_clean_room",
                description="Create a new clean room",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "comment": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_clean_room",
                description="Update clean room",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "comment": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="delete_clean_room",
                description="Delete clean room",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_clean_rooms":
            rooms = list(workspace_client.clean_rooms.list(**{k: v for k, v in arguments.items() if v}))
            return [r.as_dict() for r in rooms]
        elif name == "get_clean_room":
            return workspace_client.clean_rooms.get(name=arguments["name"]).as_dict()
        elif name == "create_clean_room":
            return workspace_client.clean_rooms.create(**arguments).as_dict()
        elif name == "update_clean_room":
            return workspace_client.clean_rooms.update(**arguments).as_dict()
        elif name == "delete_clean_room":
            workspace_client.clean_rooms.delete(name=arguments["name"])
            return {"status": "deleted", "name": arguments["name"]}
        return None

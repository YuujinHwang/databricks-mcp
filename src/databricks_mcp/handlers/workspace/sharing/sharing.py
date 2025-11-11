"""
Delta Sharing API Handler
Manage Delta Sharing recipients and shares
https://docs.databricks.com/api/workspace/recipients
https://docs.databricks.com/api/workspace/shares
"""
from typing import Any
from mcp.types import Tool


class DeltaSharingHandler:
    """Handler for Delta Sharing API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            # Recipients
            Tool(
                name="list_recipients",
                description="List all Delta Sharing recipients",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_recipient",
                description="Get recipient details",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_recipient",
                description="Create a new recipient",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "comment": {"type": "string"},
                        "sharing_code": {"type": "string"},
                        "authentication_type": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_recipient",
                description="Update recipient",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "comment": {"type": "string"},
                        "new_name": {"type": "string"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="delete_recipient",
                description="Delete recipient",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
            Tool(
                name="rotate_recipient_token",
                description="Rotate recipient token",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "existing_token_expire_in_seconds": {"type": "integer"},
                    },
                    "required": ["name"],
                },
            ),
            # Shares
            Tool(
                name="list_shares",
                description="List all Delta shares",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_share",
                description="Get share details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "include_shared_data": {"type": "boolean"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="create_share",
                description="Create a new share",
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
                name="update_share",
                description="Update share",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "comment": {"type": "string"},
                        "new_name": {"type": "string"},
                        "updates": {"type": "array"},
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="delete_share",
                description="Delete share",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        # Recipients
        if name == "list_recipients":
            recipients = list(workspace_client.recipients.list(**{k: v for k, v in arguments.items() if v}))
            return [r.as_dict() for r in recipients]
        elif name == "get_recipient":
            return workspace_client.recipients.get(name=arguments["name"]).as_dict()
        elif name == "create_recipient":
            return workspace_client.recipients.create(**arguments).as_dict()
        elif name == "update_recipient":
            return workspace_client.recipients.update(**arguments).as_dict()
        elif name == "delete_recipient":
            workspace_client.recipients.delete(name=arguments["name"])
            return {"status": "deleted", "name": arguments["name"]}
        elif name == "rotate_recipient_token":
            return workspace_client.recipients.rotate_token(**arguments).as_dict()
        # Shares
        elif name == "list_shares":
            shares = list(workspace_client.shares.list(**{k: v for k, v in arguments.items() if v}))
            return [s.as_dict() for s in shares]
        elif name == "get_share":
            return workspace_client.shares.get(**arguments).as_dict()
        elif name == "create_share":
            return workspace_client.shares.create(**arguments).as_dict()
        elif name == "update_share":
            return workspace_client.shares.update(**arguments).as_dict()
        elif name == "delete_share":
            workspace_client.shares.delete(name=arguments["name"])
            return {"status": "deleted", "name": arguments["name"]}
        return None

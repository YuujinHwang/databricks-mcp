"""
Settings API Handler
Handles account-level settings and IP access list operations
https://docs.databricks.com/api/account/ip-access-lists
https://docs.databricks.com/api/account/settings
"""
from typing import Any
from mcp.types import Tool


class SettingsHandler:
    """Handler for Databricks Settings API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of settings management tools"""
        return [
            # IP Access Lists
            Tool(
                name="list_ip_access_lists",
                description="List all IP access lists for the account console",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_ip_access_list",
                description="Get details of a specific IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"}
                    },
                    "required": ["ip_access_list_id"],
                },
            ),
            Tool(
                name="create_ip_access_list",
                description="Create an IP access list to allow/block IP addresses",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "description": "Label for the IP access list"},
                        "list_type": {
                            "type": "string",
                            "description": "Type of list (ALLOW or BLOCK)",
                            "enum": ["ALLOW", "BLOCK"],
                        },
                        "ip_addresses": {
                            "type": "array",
                            "description": "List of IP addresses/CIDR blocks (e.g., ['1.2.3.4/32'])",
                        },
                        "enabled": {
                            "type": "boolean",
                            "description": "Whether list is enabled (default: true)",
                        },
                    },
                    "required": ["label", "list_type", "ip_addresses"],
                },
            ),
            Tool(
                name="replace_ip_access_list",
                description="Replace/update an IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"},
                        "label": {"type": "string", "description": "Label for the IP access list"},
                        "list_type": {
                            "type": "string",
                            "description": "Type of list (ALLOW or BLOCK)",
                            "enum": ["ALLOW", "BLOCK"],
                        },
                        "ip_addresses": {
                            "type": "array",
                            "description": "List of IP addresses/CIDR blocks",
                        },
                        "enabled": {"type": "boolean", "description": "Whether list is enabled"},
                    },
                    "required": ["ip_access_list_id", "label", "list_type", "enabled", "ip_addresses"],
                },
            ),
            Tool(
                name="delete_ip_access_list",
                description="Delete an IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"}
                    },
                    "required": ["ip_access_list_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle settings-related tool calls"""

        # ============ IP Access Lists ============
        if name == "list_ip_access_lists":
            lists = list(account_client.ip_access_lists.list())
            return [l.as_dict() for l in lists]

        elif name == "get_ip_access_list":
            access_list = account_client.ip_access_lists.get(
                ip_access_list_id=arguments["ip_access_list_id"]
            )
            return access_list.as_dict()

        elif name == "create_ip_access_list":
            from databricks.sdk.service.settings import ListType

            list_type_map = {"ALLOW": ListType.ALLOW, "BLOCK": ListType.BLOCK}

            access_list = account_client.ip_access_lists.create(
                label=arguments["label"],
                list_type=list_type_map.get(arguments["list_type"]),
                ip_addresses=arguments["ip_addresses"],
                enabled=arguments.get("enabled", True),
            )
            return access_list.as_dict()

        elif name == "replace_ip_access_list":
            from databricks.sdk.service.settings import ListType

            list_type_map = {"ALLOW": ListType.ALLOW, "BLOCK": ListType.BLOCK}

            access_list = account_client.ip_access_lists.replace(
                ip_access_list_id=arguments["ip_access_list_id"],
                label=arguments["label"],
                list_type=list_type_map.get(arguments["list_type"]),
                enabled=arguments["enabled"],
                ip_addresses=arguments["ip_addresses"],
            )
            return access_list.as_dict()

        elif name == "delete_ip_access_list":
            account_client.ip_access_lists.delete(
                ip_access_list_id=arguments["ip_access_list_id"]
            )
            return {"status": "deleted", "ip_access_list_id": arguments["ip_access_list_id"]}

        return None

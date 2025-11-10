"""
Account API Handler
Handles account-level operations following Databricks Account API documentation
https://docs.databricks.com/api/account
"""
from typing import Any
from mcp.types import Tool


class AccountHandler:
    """Handler for Databricks Account API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of account management tools"""
        return [
            Tool(
                name="list_account_workspaces",
                description="List all workspaces in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of workspaces to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_account_workspace",
                description="Get details of a specific workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"}
                    },
                    "required": ["workspace_id"],
                },
            ),
            Tool(
                name="list_account_users",
                description="List all users in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of users to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_account_user",
                description="Get details of a specific user",
                inputSchema={
                    "type": "object",
                    "properties": {"user_id": {"type": "string", "description": "The user ID"}},
                    "required": ["user_id"],
                },
            ),
            Tool(
                name="list_account_groups",
                description="List all groups in the account",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_account_group",
                description="Get details of a specific group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_id": {"type": "string", "description": "The group ID"}
                    },
                    "required": ["group_id"],
                },
            ),
            Tool(
                name="list_account_service_principals",
                description="List all service principals in the account",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="list_account_metastores",
                description="List all Unity Catalog metastores in the account",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_account_metastore",
                description="Get details of a specific metastore",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"}
                    },
                    "required": ["metastore_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle account-related tool calls"""
        if name == "list_account_workspaces":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            workspaces = []
            count = 0
            for ws in account_client.workspaces.list():
                if count >= page_size:
                    break
                workspaces.append({
                    "workspace_id": ws.workspace_id,
                    "workspace_name": ws.workspace_name,
                    "workspace_status": str(ws.workspace_status),
                    "deployment_name": ws.deployment_name,
                })
                count += 1

            return {
                "workspaces": workspaces,
                "count": len(workspaces),
                "page_size": page_size,
            }

        elif name == "get_account_workspace":
            workspace = account_client.workspaces.get(workspace_id=arguments["workspace_id"])
            return workspace.as_dict()

        elif name == "list_account_users":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            users = []
            count = 0
            for u in account_client.users.list():
                if count >= page_size:
                    break
                users.append({
                    "id": u.id,
                    "user_name": u.user_name,
                    "display_name": u.display_name,
                    "active": u.active,
                })
                count += 1

            return {
                "users": users,
                "count": len(users),
                "page_size": page_size,
            }

        elif name == "get_account_user":
            user = account_client.users.get(id=arguments["user_id"])
            return user.as_dict()

        elif name == "list_account_groups":
            groups = list(account_client.groups.list())
            return [{"id": g.id, "display_name": g.display_name} for g in groups]

        elif name == "get_account_group":
            group = account_client.groups.get(id=arguments["group_id"])
            return group.as_dict()

        elif name == "list_account_service_principals":
            sps = list(account_client.service_principals.list())
            return [
                {
                    "id": sp.id,
                    "application_id": sp.application_id,
                    "display_name": sp.display_name,
                    "active": sp.active,
                }
                for sp in sps
            ]

        elif name == "list_account_metastores":
            metastores = list(account_client.metastores.list())
            return [
                {
                    "metastore_id": m.metastore_id,
                    "name": m.name,
                    "region": m.region,
                }
                for m in metastores
            ]

        elif name == "get_account_metastore":
            metastore = account_client.metastores.get(id=arguments["metastore_id"])
            return metastore.as_dict()

        return None

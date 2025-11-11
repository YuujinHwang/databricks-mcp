"""
Account IAM Handler
Identity and Access Management for Databricks Account
https://docs.databricks.com/api/account/users
https://docs.databricks.com/api/account/groups
https://docs.databricks.com/api/account/service-principals
https://docs.databricks.com/api/account/workspace-assignment
"""
from typing import Any
from mcp.types import Tool


class AccountIAMHandler:
    """Handler for Account-level Identity and Access Management"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of account IAM tools"""
        return [
            # ============ Users ============
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
                        "filter": {"type": "string", "description": "SCIM filter (e.g., 'userName eq john@example.com')"},
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
                name="create_account_user",
                description="Create a new user in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_name": {"type": "string", "description": "Email address of the user"},
                        "display_name": {"type": "string", "description": "Display name"},
                        "active": {"type": "boolean", "description": "Whether user is active (default: true)"},
                    },
                    "required": ["user_name"],
                },
            ),
            Tool(
                name="update_account_user",
                description="Update user details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "The user ID"},
                        "user_name": {"type": "string", "description": "Email address"},
                        "display_name": {"type": "string", "description": "Display name"},
                        "active": {"type": "boolean", "description": "Active status"},
                    },
                    "required": ["user_id"],
                },
            ),
            Tool(
                name="delete_account_user",
                description="Delete a user from the account",
                inputSchema={
                    "type": "object",
                    "properties": {"user_id": {"type": "string", "description": "The user ID"}},
                    "required": ["user_id"],
                },
            ),
            # ============ Groups ============
            Tool(
                name="list_account_groups",
                description="List all groups in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "SCIM filter"},
                    },
                },
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
                name="create_account_group",
                description="Create a new group in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "display_name": {"type": "string", "description": "Group name"},
                        "members": {"type": "array", "description": "Array of member user IDs"},
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_account_group",
                description="Update group details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_id": {"type": "string", "description": "The group ID"},
                        "display_name": {"type": "string", "description": "Group name"},
                        "members": {"type": "array", "description": "Array of member user IDs"},
                    },
                    "required": ["group_id"],
                },
            ),
            Tool(
                name="delete_account_group",
                description="Delete a group from the account",
                inputSchema={
                    "type": "object",
                    "properties": {"group_id": {"type": "string", "description": "The group ID"}},
                    "required": ["group_id"],
                },
            ),
            # ============ Service Principals ============
            Tool(
                name="list_account_service_principals",
                description="List all service principals in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "SCIM filter"},
                    },
                },
            ),
            Tool(
                name="get_account_service_principal",
                description="Get details of a specific service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"}
                    },
                    "required": ["service_principal_id"],
                },
            ),
            Tool(
                name="create_account_service_principal",
                description="Create a new service principal in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "application_id": {"type": "string", "description": "Application ID (optional)"},
                        "display_name": {"type": "string", "description": "Display name"},
                        "active": {"type": "boolean", "description": "Active status (default: true)"},
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_account_service_principal",
                description="Update service principal details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"},
                        "display_name": {"type": "string", "description": "Display name"},
                        "active": {"type": "boolean", "description": "Active status"},
                    },
                    "required": ["service_principal_id"],
                },
            ),
            Tool(
                name="delete_account_service_principal",
                description="Delete a service principal from the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"}
                    },
                    "required": ["service_principal_id"],
                },
            ),
            # ============ Workspace Assignment ============
            Tool(
                name="list_workspace_assignments",
                description="List workspace permission assignments for a specific workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"}
                    },
                    "required": ["workspace_id"],
                },
            ),
            Tool(
                name="get_workspace_assignment",
                description="Get workspace assignment for a principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "principal_id": {"type": "integer", "description": "The principal (user/group/SP) ID"},
                    },
                    "required": ["workspace_id", "principal_id"],
                },
            ),
            Tool(
                name="update_workspace_assignment",
                description="Create or update workspace permissions for a principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "principal_id": {"type": "integer", "description": "The principal ID"},
                        "permissions": {"type": "array", "description": "Array of permissions (e.g., ['USER'])"},
                    },
                    "required": ["workspace_id", "principal_id", "permissions"],
                },
            ),
            Tool(
                name="delete_workspace_assignment",
                description="Remove workspace assignment for a principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "principal_id": {"type": "integer", "description": "The principal ID"},
                    },
                    "required": ["workspace_id", "principal_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle account IAM tool calls"""

        # ============ Users ============
        if name == "list_account_users":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]

            users = []
            count = 0
            for u in account_client.users.list(**kwargs):
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

        elif name == "create_account_user":
            user = account_client.users.create(
                user_name=arguments["user_name"],
                display_name=arguments.get("display_name"),
                active=arguments.get("active", True),
            )
            return user.as_dict()

        elif name == "update_account_user":
            user = account_client.users.update(
                id=arguments["user_id"],
                user_name=arguments.get("user_name"),
                display_name=arguments.get("display_name"),
                active=arguments.get("active"),
            )
            return user.as_dict()

        elif name == "delete_account_user":
            account_client.users.delete(id=arguments["user_id"])
            return {"status": "deleted", "user_id": arguments["user_id"]}

        # ============ Groups ============
        elif name == "list_account_groups":
            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]

            groups = list(account_client.groups.list(**kwargs))
            return [{"id": g.id, "display_name": g.display_name} for g in groups]

        elif name == "get_account_group":
            group = account_client.groups.get(id=arguments["group_id"])
            return group.as_dict()

        elif name == "create_account_group":
            group = account_client.groups.create(
                display_name=arguments["display_name"],
                members=arguments.get("members"),
            )
            return group.as_dict()

        elif name == "update_account_group":
            group = account_client.groups.update(
                id=arguments["group_id"],
                display_name=arguments.get("display_name"),
                members=arguments.get("members"),
            )
            return group.as_dict()

        elif name == "delete_account_group":
            account_client.groups.delete(id=arguments["group_id"])
            return {"status": "deleted", "group_id": arguments["group_id"]}

        # ============ Service Principals ============
        elif name == "list_account_service_principals":
            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]

            sps = list(account_client.service_principals.list(**kwargs))
            return [
                {
                    "id": sp.id,
                    "application_id": sp.application_id,
                    "display_name": sp.display_name,
                    "active": sp.active,
                }
                for sp in sps
            ]

        elif name == "get_account_service_principal":
            sp = account_client.service_principals.get(id=arguments["service_principal_id"])
            return sp.as_dict()

        elif name == "create_account_service_principal":
            sp = account_client.service_principals.create(
                application_id=arguments.get("application_id"),
                display_name=arguments["display_name"],
                active=arguments.get("active", True),
            )
            return sp.as_dict()

        elif name == "update_account_service_principal":
            sp = account_client.service_principals.update(
                id=arguments["service_principal_id"],
                display_name=arguments.get("display_name"),
                active=arguments.get("active"),
            )
            return sp.as_dict()

        elif name == "delete_account_service_principal":
            account_client.service_principals.delete(id=arguments["service_principal_id"])
            return {"status": "deleted", "service_principal_id": arguments["service_principal_id"]}

        # ============ Workspace Assignment ============
        elif name == "list_workspace_assignments":
            assignments = list(account_client.workspace_assignment.list(
                workspace_id=arguments["workspace_id"]
            ))
            return [a.as_dict() for a in assignments]

        elif name == "get_workspace_assignment":
            assignment = account_client.workspace_assignment.get(
                workspace_id=arguments["workspace_id"],
                principal_id=arguments["principal_id"],
            )
            return assignment.as_dict()

        elif name == "update_workspace_assignment":
            from databricks.sdk.service.iam import WorkspacePermissions

            perms = WorkspacePermissions(permissions=arguments["permissions"])

            result = account_client.workspace_assignment.update(
                workspace_id=arguments["workspace_id"],
                principal_id=arguments["principal_id"],
                permissions=perms,
            )
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "updated"}

        elif name == "delete_workspace_assignment":
            account_client.workspace_assignment.delete(
                workspace_id=arguments["workspace_id"],
                principal_id=arguments["principal_id"],
            )
            return {
                "status": "deleted",
                "workspace_id": arguments["workspace_id"],
                "principal_id": arguments["principal_id"],
            }

        return None

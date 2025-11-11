"""
Workspace IAM API Handler
Manage workspace-level identity, access, and permissions
https://docs.databricks.com/api/workspace/permissions
https://docs.databricks.com/api/workspace/groups
https://docs.databricks.com/api/workspace/users
https://docs.databricks.com/api/workspace/servicePrincipals
"""
from typing import Any
from mcp.types import Tool


class WorkspaceIAMHandler:
    """Handler for Workspace-level IAM operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of workspace IAM tools"""
        return [
            # ============ Current User ============
            Tool(
                name="get_current_user",
                description="Get information about the currently authenticated user or service principal",
                inputSchema={"type": "object", "properties": {}},
            ),
            # ============ Permissions ============
            Tool(
                name="get_permissions",
                description="Get permissions for a workspace object (cluster, job, notebook, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_object_type": {
                            "type": "string",
                            "description": "Object type (clusters, jobs, notebooks, directories, etc.)",
                        },
                        "request_object_id": {
                            "type": "string",
                            "description": "Object ID or path",
                        },
                    },
                    "required": ["request_object_type", "request_object_id"],
                },
            ),
            Tool(
                name="set_permissions",
                description="Set permissions for a workspace object (replaces all existing permissions)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_object_type": {"type": "string", "description": "Object type"},
                        "request_object_id": {"type": "string", "description": "Object ID or path"},
                        "access_control_list": {
                            "type": "array",
                            "description": "List of ACL entries with user_name/group_name and permission_level",
                        },
                    },
                    "required": ["request_object_type", "request_object_id"],
                },
            ),
            Tool(
                name="update_permissions",
                description="Update permissions for a workspace object (adds/modifies specific grants)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_object_type": {"type": "string", "description": "Object type"},
                        "request_object_id": {"type": "string", "description": "Object ID or path"},
                        "access_control_list": {
                            "type": "array",
                            "description": "ACL entries to add/modify",
                        },
                    },
                    "required": ["request_object_type", "request_object_id", "access_control_list"],
                },
            ),
            Tool(
                name="get_permission_levels",
                description="Get available permission levels for a specific object type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request_object_type": {"type": "string", "description": "Object type"},
                        "request_object_id": {"type": "string", "description": "Object ID or path"},
                    },
                    "required": ["request_object_type", "request_object_id"],
                },
            ),
            # ============ Workspace Groups ============
            Tool(
                name="list_workspace_groups",
                description="List all groups in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "SCIM filter (e.g., \"displayName eq 'admins'\")"},
                        "attributes": {"type": "string", "description": "Attributes to return"},
                        "start_index": {"type": "integer", "description": "Start index for pagination"},
                        "count": {"type": "integer", "description": "Number of results per page"},
                    },
                },
            ),
            Tool(
                name="get_workspace_group",
                description="Get details of a specific workspace group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The group ID"}
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="create_workspace_group",
                description="Create a new workspace group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "display_name": {"type": "string", "description": "Group display name"},
                        "members": {
                            "type": "array",
                            "description": "Initial group members (user/service principal IDs)",
                        },
                        "entitlements": {
                            "type": "array",
                            "description": "Entitlements (e.g., allow-cluster-create)",
                        },
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_workspace_group",
                description="Update a workspace group (name, members, entitlements)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The group ID"},
                        "display_name": {"type": "string", "description": "New display name"},
                        "members": {"type": "array", "description": "New members list"},
                        "entitlements": {"type": "array", "description": "New entitlements"},
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="delete_workspace_group",
                description="Delete a workspace group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The group ID"}
                    },
                    "required": ["id"],
                },
            ),
            # ============ Workspace Users ============
            Tool(
                name="list_workspace_users",
                description="List all users in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "SCIM filter"},
                        "attributes": {"type": "string", "description": "Attributes to return"},
                        "start_index": {"type": "integer", "description": "Start index"},
                        "count": {"type": "integer", "description": "Results per page"},
                    },
                },
            ),
            Tool(
                name="get_workspace_user",
                description="Get details of a specific workspace user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="create_workspace_user",
                description="Create a new workspace user (requires admin)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_name": {"type": "string", "description": "User email/username"},
                        "display_name": {"type": "string", "description": "Display name"},
                        "active": {"type": "boolean", "description": "User active status (default: true)"},
                        "entitlements": {
                            "type": "array",
                            "description": "Entitlements (e.g., allow-cluster-create)",
                        },
                    },
                    "required": ["user_name"],
                },
            ),
            Tool(
                name="update_workspace_user",
                description="Update workspace user properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The user ID"},
                        "user_name": {"type": "string", "description": "New username"},
                        "active": {"type": "boolean", "description": "Active status"},
                        "entitlements": {"type": "array", "description": "New entitlements"},
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="delete_workspace_user",
                description="Delete a workspace user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The user ID"}
                    },
                    "required": ["id"],
                },
            ),
            # ============ Workspace Service Principals ============
            Tool(
                name="list_workspace_service_principals",
                description="List all service principals in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "SCIM filter"},
                        "attributes": {"type": "string", "description": "Attributes to return"},
                        "start_index": {"type": "integer", "description": "Start index"},
                        "count": {"type": "integer", "description": "Results per page"},
                    },
                },
            ),
            Tool(
                name="get_workspace_service_principal",
                description="Get details of a specific workspace service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The service principal ID"}
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="create_workspace_service_principal",
                description="Create a new workspace service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "display_name": {"type": "string", "description": "Service principal display name"},
                        "application_id": {"type": "string", "description": "Application (client) ID"},
                        "active": {"type": "boolean", "description": "Active status (default: true)"},
                        "entitlements": {"type": "array", "description": "Entitlements"},
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_workspace_service_principal",
                description="Update workspace service principal properties",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The service principal ID"},
                        "display_name": {"type": "string", "description": "New display name"},
                        "active": {"type": "boolean", "description": "Active status"},
                        "entitlements": {"type": "array", "description": "New entitlements"},
                    },
                    "required": ["id"],
                },
            ),
            Tool(
                name="delete_workspace_service_principal",
                description="Delete a workspace service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "The service principal ID"}
                    },
                    "required": ["id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle workspace IAM tool calls"""

        # ============ Current User ============
        if name == "get_current_user":
            user = workspace_client.current_user.me()
            return user.as_dict()

        # ============ Permissions ============
        elif name == "get_permissions":
            perms = workspace_client.permissions.get(
                request_object_type=arguments["request_object_type"],
                request_object_id=arguments["request_object_id"],
            )
            return perms.as_dict()

        elif name == "set_permissions":
            perms = workspace_client.permissions.set(
                request_object_type=arguments["request_object_type"],
                request_object_id=arguments["request_object_id"],
                access_control_list=arguments.get("access_control_list", []),
            )
            return perms.as_dict()

        elif name == "update_permissions":
            perms = workspace_client.permissions.update(
                request_object_type=arguments["request_object_type"],
                request_object_id=arguments["request_object_id"],
                access_control_list=arguments["access_control_list"],
            )
            return perms.as_dict()

        elif name == "get_permission_levels":
            levels = workspace_client.permissions.get_permission_levels(
                request_object_type=arguments["request_object_type"],
                request_object_id=arguments["request_object_id"],
            )
            return levels.as_dict()

        # ============ Workspace Groups ============
        elif name == "list_workspace_groups":
            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]
            if "attributes" in arguments:
                kwargs["attributes"] = arguments["attributes"]
            if "start_index" in arguments:
                kwargs["start_index"] = arguments["start_index"]
            if "count" in arguments:
                kwargs["count"] = arguments["count"]

            groups = list(workspace_client.groups.list(**kwargs))
            return [g.as_dict() for g in groups]

        elif name == "get_workspace_group":
            group = workspace_client.groups.get(id=arguments["id"])
            return group.as_dict()

        elif name == "create_workspace_group":
            group = workspace_client.groups.create(
                display_name=arguments["display_name"],
                members=arguments.get("members"),
                entitlements=arguments.get("entitlements"),
            )
            return group.as_dict()

        elif name == "update_workspace_group":
            kwargs = {"id": arguments["id"]}
            if "display_name" in arguments:
                kwargs["display_name"] = arguments["display_name"]
            if "members" in arguments:
                kwargs["members"] = arguments["members"]
            if "entitlements" in arguments:
                kwargs["entitlements"] = arguments["entitlements"]

            workspace_client.groups.patch(**kwargs)
            return {"status": "updated", "id": arguments["id"]}

        elif name == "delete_workspace_group":
            workspace_client.groups.delete(id=arguments["id"])
            return {"status": "deleted", "id": arguments["id"]}

        # ============ Workspace Users ============
        elif name == "list_workspace_users":
            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]
            if "attributes" in arguments:
                kwargs["attributes"] = arguments["attributes"]
            if "start_index" in arguments:
                kwargs["start_index"] = arguments["start_index"]
            if "count" in arguments:
                kwargs["count"] = arguments["count"]

            users = list(workspace_client.users.list(**kwargs))
            return [u.as_dict() for u in users]

        elif name == "get_workspace_user":
            user = workspace_client.users.get(id=arguments["id"])
            return user.as_dict()

        elif name == "create_workspace_user":
            user = workspace_client.users.create(
                user_name=arguments["user_name"],
                display_name=arguments.get("display_name"),
                active=arguments.get("active", True),
                entitlements=arguments.get("entitlements"),
            )
            return user.as_dict()

        elif name == "update_workspace_user":
            kwargs = {"id": arguments["id"]}
            if "user_name" in arguments:
                kwargs["user_name"] = arguments["user_name"]
            if "active" in arguments:
                kwargs["active"] = arguments["active"]
            if "entitlements" in arguments:
                kwargs["entitlements"] = arguments["entitlements"]

            workspace_client.users.patch(**kwargs)
            return {"status": "updated", "id": arguments["id"]}

        elif name == "delete_workspace_user":
            workspace_client.users.delete(id=arguments["id"])
            return {"status": "deleted", "id": arguments["id"]}

        # ============ Workspace Service Principals ============
        elif name == "list_workspace_service_principals":
            kwargs = {}
            if "filter" in arguments:
                kwargs["filter"] = arguments["filter"]
            if "attributes" in arguments:
                kwargs["attributes"] = arguments["attributes"]
            if "start_index" in arguments:
                kwargs["start_index"] = arguments["start_index"]
            if "count" in arguments:
                kwargs["count"] = arguments["count"]

            sps = list(workspace_client.service_principals.list(**kwargs))
            return [sp.as_dict() for sp in sps]

        elif name == "get_workspace_service_principal":
            sp = workspace_client.service_principals.get(id=arguments["id"])
            return sp.as_dict()

        elif name == "create_workspace_service_principal":
            sp = workspace_client.service_principals.create(
                display_name=arguments["display_name"],
                application_id=arguments.get("application_id"),
                active=arguments.get("active", True),
                entitlements=arguments.get("entitlements"),
            )
            return sp.as_dict()

        elif name == "update_workspace_service_principal":
            kwargs = {"id": arguments["id"]}
            if "display_name" in arguments:
                kwargs["display_name"] = arguments["display_name"]
            if "active" in arguments:
                kwargs["active"] = arguments["active"]
            if "entitlements" in arguments:
                kwargs["entitlements"] = arguments["entitlements"]

            workspace_client.service_principals.patch(**kwargs)
            return {"status": "updated", "id": arguments["id"]}

        elif name == "delete_workspace_service_principal":
            workspace_client.service_principals.delete(id=arguments["id"])
            return {"status": "deleted", "id": arguments["id"]}

        return None

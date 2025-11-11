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
            # ============ Workspaces ============
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
                name="create_account_workspace",
                description="Create a new workspace in the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_name": {"type": "string", "description": "Name of the workspace"},
                        "deployment_name": {"type": "string", "description": "Deployment name (subdomain)"},
                        "aws_region": {"type": "string", "description": "AWS region (e.g., us-west-2)"},
                        "credentials_id": {"type": "string", "description": "Credentials configuration ID"},
                        "storage_configuration_id": {"type": "string", "description": "Storage configuration ID"},
                        "network_id": {"type": "string", "description": "Network configuration ID (optional)"},
                        "pricing_tier": {"type": "string", "description": "Pricing tier (STANDARD, PREMIUM, ENTERPRISE)"},
                    },
                    "required": ["workspace_name", "deployment_name"],
                },
            ),
            Tool(
                name="update_account_workspace",
                description="Update workspace configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "credentials_id": {"type": "string", "description": "New credentials ID"},
                        "storage_configuration_id": {"type": "string", "description": "New storage config ID"},
                        "network_id": {"type": "string", "description": "New network config ID"},
                        "managed_services_customer_managed_key_id": {"type": "string", "description": "Managed services CMK ID"},
                        "storage_customer_managed_key_id": {"type": "string", "description": "Storage CMK ID"},
                    },
                    "required": ["workspace_id"],
                },
            ),
            Tool(
                name="delete_account_workspace",
                description="Delete a workspace from the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"}
                    },
                    "required": ["workspace_id"],
                },
            ),
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
            # ============ Metastores ============
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
            Tool(
                name="create_account_metastore",
                description="Create a new Unity Catalog metastore",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Metastore name"},
                        "storage_root": {"type": "string", "description": "Root storage location"},
                        "region": {"type": "string", "description": "Cloud region"},
                    },
                    "required": ["name", "storage_root"],
                },
            ),
            Tool(
                name="update_account_metastore",
                description="Update metastore configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "name": {"type": "string", "description": "New metastore name"},
                        "storage_root": {"type": "string", "description": "New storage root"},
                        "delta_sharing_scope": {"type": "string", "description": "Delta sharing scope"},
                    },
                    "required": ["metastore_id"],
                },
            ),
            Tool(
                name="delete_account_metastore",
                description="Delete a Unity Catalog metastore",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "force": {"type": "boolean", "description": "Force deletion (default: false)"},
                    },
                    "required": ["metastore_id"],
                },
            ),
            # ============ Metastore Assignments ============
            Tool(
                name="list_metastore_assignments",
                description="List workspace assignments for a metastore",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"}
                    },
                    "required": ["metastore_id"],
                },
            ),
            Tool(
                name="get_metastore_assignment",
                description="Get metastore assignment for a workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"}
                    },
                    "required": ["workspace_id"],
                },
            ),
            Tool(
                name="create_metastore_assignment",
                description="Assign a metastore to a workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "default_catalog_name": {"type": "string", "description": "Default catalog name"},
                    },
                    "required": ["workspace_id", "metastore_id"],
                },
            ),
            Tool(
                name="update_metastore_assignment",
                description="Update metastore assignment for a workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "default_catalog_name": {"type": "string", "description": "Default catalog name"},
                    },
                    "required": ["workspace_id", "metastore_id"],
                },
            ),
            Tool(
                name="delete_metastore_assignment",
                description="Remove metastore assignment from a workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace_id": {"type": "integer", "description": "The workspace ID"},
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                    },
                    "required": ["workspace_id", "metastore_id"],
                },
            ),
            # ============ Storage Credentials ============
            Tool(
                name="list_storage_credentials",
                description="List storage credentials for a metastore",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"}
                    },
                    "required": ["metastore_id"],
                },
            ),
            Tool(
                name="get_storage_credential",
                description="Get details of a storage credential",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "credential_name": {"type": "string", "description": "Storage credential name"},
                    },
                    "required": ["metastore_id", "credential_name"],
                },
            ),
            Tool(
                name="create_storage_credential",
                description="Create a storage credential for Unity Catalog",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "credential_name": {"type": "string", "description": "Credential name"},
                        "aws_iam_role": {"type": "object", "description": "AWS IAM role ARN"},
                        "azure_managed_identity": {"type": "object", "description": "Azure managed identity"},
                        "comment": {"type": "string", "description": "Comment/description"},
                    },
                    "required": ["metastore_id", "credential_name"],
                },
            ),
            Tool(
                name="update_storage_credential",
                description="Update a storage credential",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "metastore_id": {"type": "string", "description": "The metastore ID"},
                        "credential_name": {"type": "string", "description": "Storage credential name"},
                        "aws_iam_role": {"type": "object", "description": "AWS IAM role ARN"},
                        "azure_managed_identity": {"type": "object", "description": "Azure managed identity"},
                        "comment": {"type": "string", "description": "Comment/description"},
                    },
                    "required": ["metastore_id", "credential_name"],
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
        """Handle account-related tool calls"""

        # ============ Workspaces ============
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

        elif name == "create_account_workspace":
            workspace = account_client.workspaces.create(
                workspace_name=arguments["workspace_name"],
                deployment_name=arguments["deployment_name"],
                aws_region=arguments.get("aws_region"),
                credentials_id=arguments.get("credentials_id"),
                storage_configuration_id=arguments.get("storage_configuration_id"),
                network_id=arguments.get("network_id"),
                pricing_tier=arguments.get("pricing_tier"),
            )
            return workspace.as_dict()

        elif name == "update_account_workspace":
            workspace = account_client.workspaces.update(
                workspace_id=arguments["workspace_id"],
                credentials_id=arguments.get("credentials_id"),
                storage_configuration_id=arguments.get("storage_configuration_id"),
                network_id=arguments.get("network_id"),
                managed_services_customer_managed_key_id=arguments.get("managed_services_customer_managed_key_id"),
                storage_customer_managed_key_id=arguments.get("storage_customer_managed_key_id"),
            )
            return workspace.as_dict()

        elif name == "delete_account_workspace":
            account_client.workspaces.delete(workspace_id=arguments["workspace_id"])
            return {"status": "deleted", "workspace_id": arguments["workspace_id"]}

        # ============ Users ============
        elif name == "list_account_users":
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

        # ============ Metastores ============
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

        elif name == "create_account_metastore":
            metastore = account_client.metastores.create(
                name=arguments["name"],
                storage_root=arguments["storage_root"],
                region=arguments.get("region"),
            )
            return metastore.as_dict()

        elif name == "update_account_metastore":
            metastore = account_client.metastores.update(
                metastore_id=arguments["metastore_id"],
                name=arguments.get("name"),
                storage_root=arguments.get("storage_root"),
                delta_sharing_scope=arguments.get("delta_sharing_scope"),
            )
            return metastore.as_dict()

        elif name == "delete_account_metastore":
            force = arguments.get("force", False)
            account_client.metastores.delete(
                id=arguments["metastore_id"],
                force=force
            )
            return {"status": "deleted", "metastore_id": arguments["metastore_id"]}

        # ============ Metastore Assignments ============
        elif name == "list_metastore_assignments":
            workspace_ids = list(account_client.metastore_assignments.list(
                metastore_id=arguments["metastore_id"]
            ))
            return {"workspace_ids": workspace_ids, "count": len(workspace_ids)}

        elif name == "get_metastore_assignment":
            assignment = account_client.metastore_assignments.get(
                workspace_id=arguments["workspace_id"]
            )
            return assignment.as_dict()

        elif name == "create_metastore_assignment":
            account_client.metastore_assignments.create(
                workspace_id=arguments["workspace_id"],
                metastore_id=arguments["metastore_id"],
                default_catalog_name=arguments.get("default_catalog_name"),
            )
            return {
                "status": "assigned",
                "workspace_id": arguments["workspace_id"],
                "metastore_id": arguments["metastore_id"],
            }

        elif name == "update_metastore_assignment":
            account_client.metastore_assignments.update(
                workspace_id=arguments["workspace_id"],
                metastore_id=arguments["metastore_id"],
                default_catalog_name=arguments.get("default_catalog_name"),
            )
            return {
                "status": "updated",
                "workspace_id": arguments["workspace_id"],
                "metastore_id": arguments["metastore_id"],
            }

        elif name == "delete_metastore_assignment":
            account_client.metastore_assignments.delete(
                workspace_id=arguments["workspace_id"],
                metastore_id=arguments["metastore_id"],
            )
            return {
                "status": "unassigned",
                "workspace_id": arguments["workspace_id"],
                "metastore_id": arguments["metastore_id"],
            }

        # ============ Storage Credentials ============
        elif name == "list_storage_credentials":
            creds = list(account_client.storage_credentials.list(
                metastore_id=arguments["metastore_id"]
            ))
            return [c.as_dict() for c in creds]

        elif name == "get_storage_credential":
            cred = account_client.storage_credentials.get(
                metastore_id=arguments["metastore_id"],
                storage_credential_name=arguments["credential_name"],
            )
            return cred.as_dict()

        elif name == "create_storage_credential":
            from databricks.sdk.service.catalog import StorageCredentialInfo

            cred_info = StorageCredentialInfo(
                name=arguments["credential_name"],
                aws_iam_role=arguments.get("aws_iam_role"),
                azure_managed_identity=arguments.get("azure_managed_identity"),
                comment=arguments.get("comment"),
            )

            cred = account_client.storage_credentials.create(
                metastore_id=arguments["metastore_id"],
                credential_info=cred_info,
            )
            return cred.as_dict()

        elif name == "update_storage_credential":
            from databricks.sdk.service.catalog import StorageCredentialInfo

            cred_info = StorageCredentialInfo(
                name=arguments["credential_name"],
                aws_iam_role=arguments.get("aws_iam_role"),
                azure_managed_identity=arguments.get("azure_managed_identity"),
                comment=arguments.get("comment"),
            )

            cred = account_client.storage_credentials.update(
                metastore_id=arguments["metastore_id"],
                storage_credential_name=arguments["credential_name"],
                credential_info=cred_info,
            )
            return cred.as_dict()

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

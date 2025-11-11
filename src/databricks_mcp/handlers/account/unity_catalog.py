"""
Account Unity Catalog Handler
Unity Catalog management at account level
https://docs.databricks.com/api/account/metastores
https://docs.databricks.com/api/account/metastore-assignments
https://docs.databricks.com/api/account/storage-credentials
"""
from typing import Any
from mcp.types import Tool


class AccountUnityCatalogHandler:
    """Handler for Account-level Unity Catalog operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of account Unity Catalog tools"""
        return [
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
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle account Unity Catalog tool calls"""

        # ============ Metastores ============
        if name == "list_account_metastores":
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

        return None

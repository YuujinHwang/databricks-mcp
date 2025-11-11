"""
Provisioning API Handler
Handles account-level provisioning operations for workspaces
https://docs.databricks.com/api/account/credentials
https://docs.databricks.com/api/account/storage
https://docs.databricks.com/api/account/networks
"""
from typing import Any
from mcp.types import Tool


class ProvisioningHandler:
    """Handler for Databricks Provisioning API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of provisioning management tools"""
        return [
            # Credentials
            Tool(
                name="list_credentials",
                description="List all credential configurations for cross-account IAM roles",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_credential",
                description="Get details of a specific credential configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "credentials_id": {"type": "string", "description": "The credentials ID"}
                    },
                    "required": ["credentials_id"],
                },
            ),
            Tool(
                name="create_credential",
                description="Create a credential configuration for AWS cross-account IAM role",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "credentials_name": {"type": "string", "description": "Name of the credential"},
                        "aws_credentials": {
                            "type": "object",
                            "description": "AWS credentials with sts_role.role_arn",
                            "properties": {
                                "sts_role": {
                                    "type": "object",
                                    "properties": {
                                        "role_arn": {"type": "string", "description": "AWS IAM role ARN"}
                                    },
                                }
                            },
                        },
                    },
                    "required": ["credentials_name", "aws_credentials"],
                },
            ),
            Tool(
                name="delete_credential",
                description="Delete a credential configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "credentials_id": {"type": "string", "description": "The credentials ID"}
                    },
                    "required": ["credentials_id"],
                },
            ),
            # Storage Configurations
            Tool(
                name="list_storage_configurations",
                description="List all storage configurations for workspaces",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_storage_configuration",
                description="Get details of a specific storage configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "storage_configuration_id": {"type": "string", "description": "The storage config ID"}
                    },
                    "required": ["storage_configuration_id"],
                },
            ),
            Tool(
                name="create_storage_configuration",
                description="Create a storage configuration for workspace root storage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "storage_configuration_name": {"type": "string", "description": "Config name"},
                        "root_bucket_info": {
                            "type": "object",
                            "description": "Root bucket information",
                            "properties": {
                                "bucket_name": {"type": "string", "description": "S3 bucket name"}
                            },
                        },
                    },
                    "required": ["storage_configuration_name", "root_bucket_info"],
                },
            ),
            Tool(
                name="delete_storage_configuration",
                description="Delete a storage configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "storage_configuration_id": {"type": "string", "description": "The storage config ID"}
                    },
                    "required": ["storage_configuration_id"],
                },
            ),
            # Networks
            Tool(
                name="list_networks",
                description="List all network configurations for customer-managed VPCs",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_network",
                description="Get details of a specific network configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "network_id": {"type": "string", "description": "The network configuration ID"}
                    },
                    "required": ["network_id"],
                },
            ),
            Tool(
                name="create_network",
                description="Create a network configuration for customer-managed VPC",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "network_name": {"type": "string", "description": "Network configuration name"},
                        "vpc_id": {"type": "string", "description": "AWS VPC ID"},
                        "subnet_ids": {
                            "type": "array",
                            "description": "List of subnet IDs (at least 2 required)",
                        },
                        "security_group_ids": {
                            "type": "array",
                            "description": "List of security group IDs",
                        },
                    },
                    "required": ["network_name", "vpc_id", "subnet_ids", "security_group_ids"],
                },
            ),
            Tool(
                name="delete_network",
                description="Delete a network configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "network_id": {"type": "string", "description": "The network configuration ID"}
                    },
                    "required": ["network_id"],
                },
            ),
            # VPC Endpoints
            Tool(
                name="list_vpc_endpoints",
                description="List all VPC endpoint configurations for AWS PrivateLink",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_vpc_endpoint",
                description="Get details of a specific VPC endpoint configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vpc_endpoint_id": {"type": "string", "description": "The VPC endpoint ID"}
                    },
                    "required": ["vpc_endpoint_id"],
                },
            ),
            Tool(
                name="create_vpc_endpoint",
                description="Create a VPC endpoint configuration for AWS PrivateLink",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vpc_endpoint_name": {"type": "string", "description": "VPC endpoint name"},
                        "aws_vpc_endpoint_id": {"type": "string", "description": "AWS VPC endpoint ID"},
                        "region": {"type": "string", "description": "AWS region (e.g., us-west-2)"},
                    },
                    "required": ["vpc_endpoint_name", "aws_vpc_endpoint_id", "region"],
                },
            ),
            Tool(
                name="delete_vpc_endpoint",
                description="Delete a VPC endpoint configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "vpc_endpoint_id": {"type": "string", "description": "The VPC endpoint ID"}
                    },
                    "required": ["vpc_endpoint_id"],
                },
            ),
            # Private Access Settings
            Tool(
                name="list_private_access_settings",
                description="List all private access settings for AWS PrivateLink",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_private_access_settings",
                description="Get details of specific private access settings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "private_access_settings_id": {"type": "string", "description": "The private access settings ID"}
                    },
                    "required": ["private_access_settings_id"],
                },
            ),
            Tool(
                name="create_private_access_settings",
                description="Create private access settings for AWS PrivateLink",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "private_access_settings_name": {"type": "string", "description": "Settings name"},
                        "region": {"type": "string", "description": "AWS region"},
                        "public_access_enabled": {
                            "type": "boolean",
                            "description": "Whether public access is enabled (default: true)",
                        },
                        "private_access_level": {
                            "type": "string",
                            "description": "Private access level (ACCOUNT or ENDPOINT)",
                        },
                    },
                    "required": ["private_access_settings_name", "region"],
                },
            ),
            Tool(
                name="replace_private_access_settings",
                description="Replace/update private access settings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "private_access_settings_id": {"type": "string", "description": "The private access settings ID"},
                        "private_access_settings_name": {"type": "string", "description": "Settings name"},
                        "region": {"type": "string", "description": "AWS region"},
                        "public_access_enabled": {"type": "boolean", "description": "Public access enabled"},
                        "private_access_level": {"type": "string", "description": "Private access level"},
                    },
                    "required": ["private_access_settings_id"],
                },
            ),
            Tool(
                name="delete_private_access_settings",
                description="Delete private access settings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "private_access_settings_id": {"type": "string", "description": "The private access settings ID"}
                    },
                    "required": ["private_access_settings_id"],
                },
            ),
            # Encryption Keys
            Tool(
                name="list_encryption_keys",
                description="List all customer-managed encryption key configurations",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_encryption_key",
                description="Get details of a specific encryption key configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_managed_key_id": {"type": "string", "description": "The CMK ID"}
                    },
                    "required": ["customer_managed_key_id"],
                },
            ),
            Tool(
                name="create_encryption_key",
                description="Create a customer-managed encryption key configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "use_cases": {
                            "type": "array",
                            "description": "Use cases (MANAGED_SERVICES, STORAGE)",
                        },
                        "aws_key_info": {
                            "type": "object",
                            "description": "AWS KMS key information",
                            "properties": {
                                "key_arn": {"type": "string", "description": "AWS KMS key ARN"},
                                "key_alias": {"type": "string", "description": "AWS KMS key alias"},
                            },
                        },
                        "gcp_key_info": {
                            "type": "object",
                            "description": "GCP KMS key information",
                        },
                    },
                    "required": ["use_cases"],
                },
            ),
            Tool(
                name="delete_encryption_key",
                description="Delete an encryption key configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_managed_key_id": {"type": "string", "description": "The CMK ID"}
                    },
                    "required": ["customer_managed_key_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle provisioning-related tool calls"""

        # ============ Credentials ============
        if name == "list_credentials":
            creds = list(account_client.credentials.list())
            return [c.as_dict() for c in creds]

        elif name == "get_credential":
            cred = account_client.credentials.get(credentials_id=arguments["credentials_id"])
            return cred.as_dict()

        elif name == "create_credential":
            from databricks.sdk.service.provisioning import CreateCredentialAwsCredentials

            aws_creds = CreateCredentialAwsCredentials(
                sts_role=arguments["aws_credentials"].get("sts_role")
            )

            cred = account_client.credentials.create(
                credentials_name=arguments["credentials_name"],
                aws_credentials=aws_creds,
            )
            return cred.as_dict()

        elif name == "delete_credential":
            account_client.credentials.delete(credentials_id=arguments["credentials_id"])
            return {"status": "deleted", "credentials_id": arguments["credentials_id"]}

        # ============ Storage Configurations ============
        elif name == "list_storage_configurations":
            configs = list(account_client.storage.list())
            return [c.as_dict() for c in configs]

        elif name == "get_storage_configuration":
            config = account_client.storage.get(
                storage_configuration_id=arguments["storage_configuration_id"]
            )
            return config.as_dict()

        elif name == "create_storage_configuration":
            from databricks.sdk.service.provisioning import RootBucketInfo

            bucket_info = RootBucketInfo(bucket_name=arguments["root_bucket_info"]["bucket_name"])

            config = account_client.storage.create(
                storage_configuration_name=arguments["storage_configuration_name"],
                root_bucket_info=bucket_info,
            )
            return config.as_dict()

        elif name == "delete_storage_configuration":
            account_client.storage.delete(
                storage_configuration_id=arguments["storage_configuration_id"]
            )
            return {"status": "deleted", "storage_configuration_id": arguments["storage_configuration_id"]}

        # ============ Networks ============
        elif name == "list_networks":
            networks = list(account_client.networks.list())
            return [n.as_dict() for n in networks]

        elif name == "get_network":
            network = account_client.networks.get(network_id=arguments["network_id"])
            return network.as_dict()

        elif name == "create_network":
            network = account_client.networks.create(
                network_name=arguments["network_name"],
                vpc_id=arguments["vpc_id"],
                subnet_ids=arguments["subnet_ids"],
                security_group_ids=arguments["security_group_ids"],
            )
            return network.as_dict()

        elif name == "delete_network":
            account_client.networks.delete(network_id=arguments["network_id"])
            return {"status": "deleted", "network_id": arguments["network_id"]}

        # ============ VPC Endpoints ============
        elif name == "list_vpc_endpoints":
            endpoints = list(account_client.vpc_endpoints.list())
            return [e.as_dict() for e in endpoints]

        elif name == "get_vpc_endpoint":
            endpoint = account_client.vpc_endpoints.get(vpc_endpoint_id=arguments["vpc_endpoint_id"])
            return endpoint.as_dict()

        elif name == "create_vpc_endpoint":
            endpoint = account_client.vpc_endpoints.create(
                vpc_endpoint_name=arguments["vpc_endpoint_name"],
                aws_vpc_endpoint_id=arguments["aws_vpc_endpoint_id"],
                region=arguments["region"],
            )
            return endpoint.as_dict()

        elif name == "delete_vpc_endpoint":
            account_client.vpc_endpoints.delete(vpc_endpoint_id=arguments["vpc_endpoint_id"])
            return {"status": "deleted", "vpc_endpoint_id": arguments["vpc_endpoint_id"]}

        # ============ Private Access Settings ============
        elif name == "list_private_access_settings":
            settings_list = list(account_client.private_access.list())
            return [s.as_dict() for s in settings_list]

        elif name == "get_private_access_settings":
            settings = account_client.private_access.get(
                private_access_settings_id=arguments["private_access_settings_id"]
            )
            return settings.as_dict()

        elif name == "create_private_access_settings":
            settings = account_client.private_access.create(
                private_access_settings_name=arguments["private_access_settings_name"],
                region=arguments["region"],
                public_access_enabled=arguments.get("public_access_enabled", True),
                private_access_level=arguments.get("private_access_level"),
            )
            return settings.as_dict()

        elif name == "replace_private_access_settings":
            settings = account_client.private_access.replace(
                private_access_settings_id=arguments["private_access_settings_id"],
                private_access_settings_name=arguments.get("private_access_settings_name"),
                region=arguments.get("region"),
                public_access_enabled=arguments.get("public_access_enabled"),
                private_access_level=arguments.get("private_access_level"),
            )
            return settings.as_dict()

        elif name == "delete_private_access_settings":
            account_client.private_access.delete(
                private_access_settings_id=arguments["private_access_settings_id"]
            )
            return {"status": "deleted", "private_access_settings_id": arguments["private_access_settings_id"]}

        # ============ Encryption Keys ============
        elif name == "list_encryption_keys":
            keys = list(account_client.encryption_keys.list())
            return [k.as_dict() for k in keys]

        elif name == "get_encryption_key":
            key = account_client.encryption_keys.get(
                customer_managed_key_id=arguments["customer_managed_key_id"]
            )
            return key.as_dict()

        elif name == "create_encryption_key":
            key = account_client.encryption_keys.create(
                use_cases=arguments["use_cases"],
                aws_key_info=arguments.get("aws_key_info"),
                gcp_key_info=arguments.get("gcp_key_info"),
            )
            return key.as_dict()

        elif name == "delete_encryption_key":
            account_client.encryption_keys.delete(
                customer_managed_key_id=arguments["customer_managed_key_id"]
            )
            return {"status": "deleted", "customer_managed_key_id": arguments["customer_managed_key_id"]}

        return None

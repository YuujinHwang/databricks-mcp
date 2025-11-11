"""
OAuth API Handler
Handles OAuth and service principal secret operations
https://docs.databricks.com/api/account/custom-app-integration
https://docs.databricks.com/api/account/service-principal-secrets
"""
from typing import Any
from mcp.types import Tool


class OAuthHandler:
    """Handler for Databricks OAuth API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of OAuth management tools"""
        return [
            # Custom App Integration
            Tool(
                name="list_custom_app_integrations",
                description="List all custom OAuth app integrations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_creator_username": {
                            "type": "boolean",
                            "description": "Include creator username in response",
                        },
                    },
                },
            ),
            Tool(
                name="get_custom_app_integration",
                description="Get details of a specific custom OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"}
                    },
                    "required": ["integration_id"],
                },
            ),
            Tool(
                name="create_custom_app_integration",
                description="Create a custom OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Integration name"},
                        "redirect_urls": {
                            "type": "array",
                            "description": "List of redirect URLs for OAuth flow",
                        },
                        "confidential": {
                            "type": "boolean",
                            "description": "Whether app is confidential (default: true)",
                        },
                        "scopes": {
                            "type": "array",
                            "description": "OAuth scopes",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_custom_app_integration",
                description="Update a custom OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"},
                        "redirect_urls": {"type": "array", "description": "Redirect URLs"},
                        "scopes": {"type": "array", "description": "OAuth scopes"},
                    },
                    "required": ["integration_id"],
                },
            ),
            Tool(
                name="delete_custom_app_integration",
                description="Delete a custom OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"}
                    },
                    "required": ["integration_id"],
                },
            ),
            # Published App Integration
            Tool(
                name="list_published_app_integrations",
                description="List all published OAuth app integrations",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_published_app_integration",
                description="Get details of a published OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"}
                    },
                    "required": ["integration_id"],
                },
            ),
            Tool(
                name="create_published_app_integration",
                description="Create a published OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "string", "description": "Published app ID"},
                        "token_access_policy": {
                            "type": "object",
                            "description": "Token access policy",
                        },
                    },
                    "required": ["app_id"],
                },
            ),
            Tool(
                name="update_published_app_integration",
                description="Update a published OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"},
                        "token_access_policy": {
                            "type": "object",
                            "description": "Token access policy",
                        },
                    },
                    "required": ["integration_id"],
                },
            ),
            Tool(
                name="delete_published_app_integration",
                description="Delete a published OAuth app integration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "integration_id": {"type": "string", "description": "The integration ID"}
                    },
                    "required": ["integration_id"],
                },
            ),
            # Service Principal Secrets
            Tool(
                name="list_service_principal_secrets",
                description="List all secrets for a service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"}
                    },
                    "required": ["service_principal_id"],
                },
            ),
            Tool(
                name="create_service_principal_secret",
                description="Create a secret for a service principal",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"},
                        "lifetime": {
                            "type": "string",
                            "description": "Secret lifetime (optional, format: number + unit like '30d' or '1y')",
                        },
                    },
                    "required": ["service_principal_id"],
                },
            ),
            Tool(
                name="delete_service_principal_secret",
                description="Delete a service principal secret",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_principal_id": {"type": "string", "description": "The service principal ID"},
                        "secret_id": {"type": "string", "description": "The secret ID"},
                    },
                    "required": ["service_principal_id", "secret_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle OAuth-related tool calls"""

        # ============ Custom App Integration ============
        if name == "list_custom_app_integrations":
            kwargs = {}
            if "include_creator_username" in arguments:
                kwargs["include_creator_username"] = arguments["include_creator_username"]

            integrations = list(account_client.custom_app_integration.list(**kwargs))
            return [i.as_dict() for i in integrations]

        elif name == "get_custom_app_integration":
            integration = account_client.custom_app_integration.get(
                integration_id=arguments["integration_id"]
            )
            return integration.as_dict()

        elif name == "create_custom_app_integration":
            integration = account_client.custom_app_integration.create(
                name=arguments["name"],
                redirect_urls=arguments.get("redirect_urls"),
                confidential=arguments.get("confidential", True),
                scopes=arguments.get("scopes"),
            )
            return integration.as_dict()

        elif name == "update_custom_app_integration":
            integration = account_client.custom_app_integration.update(
                integration_id=arguments["integration_id"],
                redirect_urls=arguments.get("redirect_urls"),
                scopes=arguments.get("scopes"),
            )
            return integration.as_dict() if hasattr(integration, "as_dict") else {"status": "updated"}

        elif name == "delete_custom_app_integration":
            account_client.custom_app_integration.delete(integration_id=arguments["integration_id"])
            return {"status": "deleted", "integration_id": arguments["integration_id"]}

        # ============ Published App Integration ============
        elif name == "list_published_app_integrations":
            integrations = list(account_client.published_app_integration.list())
            return [i.as_dict() for i in integrations]

        elif name == "get_published_app_integration":
            integration = account_client.published_app_integration.get(
                integration_id=arguments["integration_id"]
            )
            return integration.as_dict()

        elif name == "create_published_app_integration":
            integration = account_client.published_app_integration.create(
                app_id=arguments["app_id"],
                token_access_policy=arguments.get("token_access_policy"),
            )
            return integration.as_dict()

        elif name == "update_published_app_integration":
            integration = account_client.published_app_integration.update(
                integration_id=arguments["integration_id"],
                token_access_policy=arguments.get("token_access_policy"),
            )
            return integration.as_dict() if hasattr(integration, "as_dict") else {"status": "updated"}

        elif name == "delete_published_app_integration":
            account_client.published_app_integration.delete(integration_id=arguments["integration_id"])
            return {"status": "deleted", "integration_id": arguments["integration_id"]}

        # ============ Service Principal Secrets ============
        elif name == "list_service_principal_secrets":
            secrets = list(
                account_client.service_principal_secrets.list(
                    service_principal_id=arguments["service_principal_id"]
                )
            )
            return [s.as_dict() for s in secrets]

        elif name == "create_service_principal_secret":
            kwargs = {"service_principal_id": arguments["service_principal_id"]}
            if "lifetime" in arguments:
                kwargs["lifetime"] = arguments["lifetime"]

            secret = account_client.service_principal_secrets.create(**kwargs)
            return secret.as_dict()

        elif name == "delete_service_principal_secret":
            account_client.service_principal_secrets.delete(
                service_principal_id=arguments["service_principal_id"],
                secret_id=arguments["secret_id"],
            )
            return {
                "status": "deleted",
                "service_principal_id": arguments["service_principal_id"],
                "secret_id": arguments["secret_id"],
            }

        return None

"""
Secrets API Handler
Handles secret management operations following Databricks Secrets API documentation
https://docs.databricks.com/api/workspace/secrets
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from mcp.types import Tool


class SecretsHandler:
    """Handler for Databricks Secrets API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of secrets management tools"""
        return [
            Tool(
                name="list_secret_scopes",
                description="List all secret scopes",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="create_secret_scope",
                description="Create a new secret scope",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"}
                    },
                    "required": ["scope"],
                },
            ),
            Tool(
                name="delete_secret_scope",
                description="Delete a secret scope",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"}
                    },
                    "required": ["scope"],
                },
            ),
            Tool(
                name="list_secrets",
                description="List secrets in a scope",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"}
                    },
                    "required": ["scope"],
                },
            ),
            Tool(
                name="put_secret",
                description="Create or update a secret",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"},
                        "key": {"type": "string", "description": "The secret key"},
                        "string_value": {"type": "string", "description": "The secret value"},
                    },
                    "required": ["scope", "key", "string_value"],
                },
            ),
            Tool(
                name="delete_secret",
                description="Delete a secret",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"},
                        "key": {"type": "string", "description": "The secret key"},
                    },
                    "required": ["scope", "key"],
                },
            ),
            Tool(
                name="put_secrets_batch",
                description="Create or update multiple secrets in a single operation (batch put)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"},
                        "secrets": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "key": {"type": "string", "description": "The secret key"},
                                    "string_value": {"type": "string", "description": "The secret value"}
                                },
                                "required": ["key", "string_value"]
                            },
                            "description": "Array of secrets to create/update"
                        }
                    },
                    "required": ["scope", "secrets"],
                },
            ),
            Tool(
                name="delete_secrets_batch",
                description="Delete multiple secrets in a single operation (batch delete)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string", "description": "The scope name"},
                        "keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of secret keys to delete"
                        }
                    },
                    "required": ["scope", "keys"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle secrets-related tool calls"""
        if name == "list_secret_scopes":
            scopes = list(workspace_client.secrets.list_scopes())
            return [{"name": s.name} for s in scopes]

        elif name == "create_secret_scope":
            workspace_client.secrets.create_scope(scope=arguments["scope"])
            return {"status": "created", "scope": arguments["scope"]}

        elif name == "delete_secret_scope":
            workspace_client.secrets.delete_scope(scope=arguments["scope"])
            return {"status": "deleted", "scope": arguments["scope"]}

        elif name == "list_secrets":
            secrets = list(workspace_client.secrets.list_secrets(scope=arguments["scope"]))
            return [{"key": s.key} for s in secrets]

        elif name == "put_secret":
            workspace_client.secrets.put_secret(
                scope=arguments["scope"],
                key=arguments["key"],
                string_value=arguments["string_value"],
            )
            return {
                "status": "created",
                "scope": arguments["scope"],
                "key": arguments["key"],
            }

        elif name == "delete_secret":
            workspace_client.secrets.delete_secret(scope=arguments["scope"], key=arguments["key"])
            return {
                "status": "deleted",
                "scope": arguments["scope"],
                "key": arguments["key"],
            }

        elif name == "put_secrets_batch":
            scope = arguments["scope"]
            secrets = arguments["secrets"]

            def put_secret(secret_item):
                try:
                    workspace_client.secrets.put_secret(
                        scope=scope,
                        key=secret_item["key"],
                        string_value=secret_item["string_value"]
                    )
                    return {"key": secret_item["key"], "status": "success"}
                except Exception as e:
                    return {"key": secret_item["key"], "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(put_secret, secret) for secret in secrets]
                results = [future.result() for future in as_completed(futures)]

            return {
                "scope": scope,
                "total": len(secrets),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_secrets_batch":
            scope = arguments["scope"]
            keys = arguments["keys"]

            def delete_secret(key):
                try:
                    workspace_client.secrets.delete_secret(scope=scope, key=key)
                    return {"key": key, "status": "success"}
                except Exception as e:
                    return {"key": key, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_secret, key) for key in keys]
                results = [future.result() for future in as_completed(futures)]

            return {
                "scope": scope,
                "total": len(keys),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None

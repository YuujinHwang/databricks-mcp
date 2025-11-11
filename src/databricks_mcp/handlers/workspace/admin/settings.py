"""
Workspace Settings API Handler
Manage workspace configuration, tokens, IP access lists
https://docs.databricks.com/api/workspace/tokens
https://docs.databricks.com/api/workspace/ipaccesslists
https://docs.databricks.com/api/workspace/workspaceconf
"""
from typing import Any
from mcp.types import Tool


class WorkspaceSettingsHandler:
    """Handler for Workspace Settings API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of workspace settings tools"""
        return [
            # ============ Tokens (Personal Access Tokens) ============
            Tool(
                name="list_workspace_tokens",
                description="List all personal access tokens for the workspace",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="create_workspace_token",
                description="Create a new personal access token (PAT)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "lifetime_seconds": {
                            "type": "integer",
                            "description": "Token lifetime in seconds (max: 7776000 = 90 days)",
                        },
                        "comment": {"type": "string", "description": "Comment/description for the token"},
                    },
                },
            ),
            Tool(
                name="revoke_workspace_token",
                description="Revoke (delete) a personal access token",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "token_id": {"type": "string", "description": "The token ID to revoke"}
                    },
                    "required": ["token_id"],
                },
            ),
            # ============ IP Access Lists (Workspace-level) ============
            Tool(
                name="list_workspace_ip_access_lists",
                description="List all workspace-level IP access lists",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_workspace_ip_access_list",
                description="Get details of a specific workspace IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"}
                    },
                    "required": ["ip_access_list_id"],
                },
            ),
            Tool(
                name="create_workspace_ip_access_list",
                description="Create a new workspace-level IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "label": {"type": "string", "description": "Label for the IP access list"},
                        "list_type": {
                            "type": "string",
                            "description": "Type: ALLOW or BLOCK",
                            "enum": ["ALLOW", "BLOCK"],
                        },
                        "ip_addresses": {
                            "type": "array",
                            "description": "List of IP addresses/CIDR blocks",
                        },
                        "enabled": {"type": "boolean", "description": "Whether list is enabled (default: true)"},
                    },
                    "required": ["label", "list_type", "ip_addresses"],
                },
            ),
            Tool(
                name="replace_workspace_ip_access_list",
                description="Replace/update workspace IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"},
                        "label": {"type": "string", "description": "New label"},
                        "list_type": {"type": "string", "enum": ["ALLOW", "BLOCK"]},
                        "ip_addresses": {"type": "array", "description": "New IP addresses"},
                        "enabled": {"type": "boolean", "description": "Enabled status"},
                    },
                    "required": ["ip_access_list_id", "label", "list_type", "enabled", "ip_addresses"],
                },
            ),
            Tool(
                name="delete_workspace_ip_access_list",
                description="Delete a workspace-level IP access list",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip_access_list_id": {"type": "string", "description": "The IP access list ID"}
                    },
                    "required": ["ip_access_list_id"],
                },
            ),
            # ============ Workspace Configuration ============
            Tool(
                name="get_workspace_config",
                description="Get workspace configuration settings (returns key-value pairs)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "string",
                            "description": "Comma-separated keys to retrieve (optional, returns all if not specified)",
                        }
                    },
                },
            ),
            Tool(
                name="set_workspace_config",
                description="Set workspace configuration settings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "settings": {
                            "type": "object",
                            "description": "Key-value pairs of settings to set",
                        }
                    },
                    "required": ["settings"],
                },
            ),
            # ============ Global Init Scripts ============
            Tool(
                name="list_global_init_scripts",
                description="List all global init scripts for the workspace",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_global_init_script",
                description="Get details of a specific global init script",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script_id": {"type": "string", "description": "The script ID"}
                    },
                    "required": ["script_id"],
                },
            ),
            Tool(
                name="create_global_init_script",
                description="Create a new global init script (runs on all clusters)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Script name"},
                        "script": {"type": "string", "description": "Base64-encoded script content"},
                        "enabled": {"type": "boolean", "description": "Whether script is enabled (default: true)"},
                        "position": {
                            "type": "integer",
                            "description": "Execution order position (lower runs first)",
                        },
                    },
                    "required": ["name", "script"],
                },
            ),
            Tool(
                name="update_global_init_script",
                description="Update a global init script",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script_id": {"type": "string", "description": "The script ID"},
                        "name": {"type": "string", "description": "New script name"},
                        "script": {"type": "string", "description": "New base64-encoded script content"},
                        "enabled": {"type": "boolean", "description": "New enabled status"},
                        "position": {"type": "integer", "description": "New execution position"},
                    },
                    "required": ["script_id", "name", "script"],
                },
            ),
            Tool(
                name="delete_global_init_script",
                description="Delete a global init script",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script_id": {"type": "string", "description": "The script ID"}
                    },
                    "required": ["script_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle workspace settings tool calls"""

        # ============ Tokens ============
        if name == "list_workspace_tokens":
            tokens = list(workspace_client.tokens.list())
            return [t.as_dict() for t in tokens]

        elif name == "create_workspace_token":
            kwargs = {}
            if "lifetime_seconds" in arguments:
                kwargs["lifetime_seconds"] = arguments["lifetime_seconds"]
            if "comment" in arguments:
                kwargs["comment"] = arguments["comment"]

            token_info = workspace_client.tokens.create(**kwargs)
            return token_info.as_dict()

        elif name == "revoke_workspace_token":
            workspace_client.tokens.delete(token_id=arguments["token_id"])
            return {"status": "revoked", "token_id": arguments["token_id"]}

        # ============ IP Access Lists ============
        elif name == "list_workspace_ip_access_lists":
            lists = list(workspace_client.ip_access_lists.list())
            return [l.as_dict() for l in lists]

        elif name == "get_workspace_ip_access_list":
            access_list = workspace_client.ip_access_lists.get(
                ip_access_list_id=arguments["ip_access_list_id"]
            )
            return access_list.as_dict()

        elif name == "create_workspace_ip_access_list":
            from databricks.sdk.service.settings import ListType

            list_type_map = {"ALLOW": ListType.ALLOW, "BLOCK": ListType.BLOCK}

            access_list = workspace_client.ip_access_lists.create(
                label=arguments["label"],
                list_type=list_type_map.get(arguments["list_type"]),
                ip_addresses=arguments["ip_addresses"],
                enabled=arguments.get("enabled", True),
            )
            return access_list.as_dict()

        elif name == "replace_workspace_ip_access_list":
            from databricks.sdk.service.settings import ListType

            list_type_map = {"ALLOW": ListType.ALLOW, "BLOCK": ListType.BLOCK}

            access_list = workspace_client.ip_access_lists.replace(
                ip_access_list_id=arguments["ip_access_list_id"],
                label=arguments["label"],
                list_type=list_type_map.get(arguments["list_type"]),
                enabled=arguments["enabled"],
                ip_addresses=arguments["ip_addresses"],
            )
            return access_list.as_dict()

        elif name == "delete_workspace_ip_access_list":
            workspace_client.ip_access_lists.delete(ip_access_list_id=arguments["ip_access_list_id"])
            return {"status": "deleted", "ip_access_list_id": arguments["ip_access_list_id"]}

        # ============ Workspace Configuration ============
        elif name == "get_workspace_config":
            kwargs = {}
            if "keys" in arguments:
                kwargs["keys"] = arguments["keys"]

            config = workspace_client.workspace_conf.get_status(**kwargs)
            return config.as_dict() if hasattr(config, "as_dict") else dict(config)

        elif name == "set_workspace_config":
            workspace_client.workspace_conf.set_status(**arguments["settings"])
            return {"status": "updated", "settings": arguments["settings"]}

        # ============ Global Init Scripts ============
        elif name == "list_global_init_scripts":
            scripts = list(workspace_client.global_init_scripts.list())
            return [
                {
                    "script_id": s.script_id,
                    "name": s.name,
                    "enabled": s.enabled,
                    "position": s.position,
                    "created_by": s.created_by,
                    "created_at": s.created_at,
                }
                for s in scripts
            ]

        elif name == "get_global_init_script":
            script = workspace_client.global_init_scripts.get(script_id=arguments["script_id"])
            return script.as_dict()

        elif name == "create_global_init_script":
            script = workspace_client.global_init_scripts.create(
                name=arguments["name"],
                script=arguments["script"],
                enabled=arguments.get("enabled", True),
                position=arguments.get("position"),
            )
            return {"script_id": script.script_id, "status": "created"}

        elif name == "update_global_init_script":
            workspace_client.global_init_scripts.update(
                script_id=arguments["script_id"],
                name=arguments["name"],
                script=arguments["script"],
                enabled=arguments.get("enabled"),
                position=arguments.get("position"),
            )
            return {"status": "updated", "script_id": arguments["script_id"]}

        elif name == "delete_global_init_script":
            workspace_client.global_init_scripts.delete(script_id=arguments["script_id"])
            return {"status": "deleted", "script_id": arguments["script_id"]}

        return None

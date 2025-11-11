"""
Cluster Policies API Handler
Manage cluster policies for governance and cost control
https://docs.databricks.com/api/workspace/clusterpolicies
"""
from typing import Any
from mcp.types import Tool


class ClusterPoliciesHandler:
    """Handler for Databricks Cluster Policies API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of cluster policy management tools"""
        return [
            Tool(
                name="list_cluster_policies",
                description="List all cluster policies in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sort_column": {
                            "type": "string",
                            "description": "Sort by column (POLICY_CREATION_TIME, POLICY_NAME)",
                        },
                        "sort_order": {
                            "type": "string",
                            "description": "Sort order (ASC or DESC)",
                        },
                    },
                },
            ),
            Tool(
                name="get_cluster_policy",
                description="Get details of a specific cluster policy",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string", "description": "The cluster policy ID"}
                    },
                    "required": ["policy_id"],
                },
            ),
            Tool(
                name="create_cluster_policy",
                description="Create a new cluster policy for governance and cost control",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Policy name"},
                        "definition": {
                            "type": "string",
                            "description": "Policy definition in JSON format (cluster configuration rules)",
                        },
                        "description": {"type": "string", "description": "Policy description"},
                        "max_clusters_per_user": {
                            "type": "integer",
                            "description": "Maximum clusters per user (optional)",
                        },
                        "policy_family_id": {
                            "type": "string",
                            "description": "Policy family ID (for built-in policies)",
                        },
                        "policy_family_definition_overrides": {
                            "type": "string",
                            "description": "Overrides for policy family definition",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="edit_cluster_policy",
                description="Edit/update an existing cluster policy",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string", "description": "The cluster policy ID"},
                        "name": {"type": "string", "description": "New policy name"},
                        "definition": {
                            "type": "string",
                            "description": "New policy definition in JSON format",
                        },
                        "description": {"type": "string", "description": "New policy description"},
                        "max_clusters_per_user": {"type": "integer", "description": "New max clusters per user"},
                        "policy_family_definition_overrides": {
                            "type": "string",
                            "description": "New overrides",
                        },
                    },
                    "required": ["policy_id", "name"],
                },
            ),
            Tool(
                name="delete_cluster_policy",
                description="Delete a cluster policy (built-in policies cannot be deleted)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string", "description": "The cluster policy ID"}
                    },
                    "required": ["policy_id"],
                },
            ),
            Tool(
                name="list_policy_families",
                description="List all available policy families (built-in policy templates)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer", "description": "Maximum number of results"},
                        "page_token": {"type": "string", "description": "Page token for pagination"},
                    },
                },
            ),
            Tool(
                name="get_policy_family",
                description="Get details of a specific policy family",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "policy_family_id": {"type": "string", "description": "The policy family ID"}
                    },
                    "required": ["policy_family_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle cluster policy tool calls"""

        if name == "list_cluster_policies":
            kwargs = {}
            if "sort_column" in arguments:
                kwargs["sort_column"] = arguments["sort_column"]
            if "sort_order" in arguments:
                kwargs["sort_order"] = arguments["sort_order"]

            policies = list(workspace_client.cluster_policies.list(**kwargs))
            return [
                {
                    "policy_id": p.policy_id,
                    "name": p.name,
                    "description": p.description,
                    "is_default": p.is_default,
                    "creator_user_name": p.creator_user_name,
                }
                for p in policies
            ]

        elif name == "get_cluster_policy":
            policy = workspace_client.cluster_policies.get(policy_id=arguments["policy_id"])
            return policy.as_dict()

        elif name == "create_cluster_policy":
            kwargs = {
                "name": arguments["name"],
            }
            if "definition" in arguments:
                kwargs["definition"] = arguments["definition"]
            if "description" in arguments:
                kwargs["description"] = arguments["description"]
            if "max_clusters_per_user" in arguments:
                kwargs["max_clusters_per_user"] = arguments["max_clusters_per_user"]
            if "policy_family_id" in arguments:
                kwargs["policy_family_id"] = arguments["policy_family_id"]
            if "policy_family_definition_overrides" in arguments:
                kwargs["policy_family_definition_overrides"] = arguments["policy_family_definition_overrides"]

            policy = workspace_client.cluster_policies.create(**kwargs)
            return {"policy_id": policy.policy_id, "status": "created"}

        elif name == "edit_cluster_policy":
            kwargs = {
                "policy_id": arguments["policy_id"],
                "name": arguments["name"],
            }
            if "definition" in arguments:
                kwargs["definition"] = arguments["definition"]
            if "description" in arguments:
                kwargs["description"] = arguments["description"]
            if "max_clusters_per_user" in arguments:
                kwargs["max_clusters_per_user"] = arguments["max_clusters_per_user"]
            if "policy_family_definition_overrides" in arguments:
                kwargs["policy_family_definition_overrides"] = arguments["policy_family_definition_overrides"]

            workspace_client.cluster_policies.edit(**kwargs)
            return {"status": "updated", "policy_id": arguments["policy_id"]}

        elif name == "delete_cluster_policy":
            workspace_client.cluster_policies.delete(policy_id=arguments["policy_id"])
            return {"status": "deleted", "policy_id": arguments["policy_id"]}

        elif name == "list_policy_families":
            kwargs = {}
            if "max_results" in arguments:
                kwargs["max_results"] = arguments["max_results"]
            if "page_token" in arguments:
                kwargs["page_token"] = arguments["page_token"]

            families = list(workspace_client.policy_families.list(**kwargs))
            return [f.as_dict() for f in families]

        elif name == "get_policy_family":
            family = workspace_client.policy_families.get(policy_family_id=arguments["policy_family_id"])
            return family.as_dict()

        return None

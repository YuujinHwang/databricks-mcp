"""
Instance Pools API Handler
Manage instance pools for cluster creation optimization
https://docs.databricks.com/api/workspace/instancepools
"""
from typing import Any
from mcp.types import Tool


class InstancePoolsHandler:
    """Handler for Databricks Instance Pools API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of instance pool management tools"""
        return [
            Tool(
                name="list_instance_pools",
                description="List all instance pools in the workspace",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_instance_pool",
                description="Get details of a specific instance pool",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_pool_id": {"type": "string", "description": "The instance pool ID"}
                    },
                    "required": ["instance_pool_id"],
                },
            ),
            Tool(
                name="create_instance_pool",
                description="Create a new instance pool for cluster optimization",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_pool_name": {"type": "string", "description": "Name of the instance pool"},
                        "node_type_id": {"type": "string", "description": "Node type (e.g., 'i3.xlarge', 'Standard_DS3_v2')"},
                        "min_idle_instances": {
                            "type": "integer",
                            "description": "Minimum number of idle instances to maintain (default: 0)",
                        },
                        "max_capacity": {
                            "type": "integer",
                            "description": "Maximum number of instances in the pool",
                        },
                        "idle_instance_autotermination_minutes": {
                            "type": "integer",
                            "description": "Minutes before idle instances terminate (default: 60)",
                        },
                        "enable_elastic_disk": {
                            "type": "boolean",
                            "description": "Enable elastic disk (auto-expand storage)",
                        },
                        "disk_spec": {
                            "type": "object",
                            "description": "Disk specification for instances",
                        },
                        "preloaded_spark_versions": {
                            "type": "array",
                            "description": "Spark versions to preload (speeds up cluster creation)",
                        },
                        "aws_attributes": {
                            "type": "object",
                            "description": "AWS-specific attributes (availability, zone_id, spot_bid_price_percent)",
                        },
                        "azure_attributes": {
                            "type": "object",
                            "description": "Azure-specific attributes",
                        },
                        "custom_tags": {
                            "type": "object",
                            "description": "Custom tags for instances",
                        },
                    },
                    "required": ["instance_pool_name", "node_type_id"],
                },
            ),
            Tool(
                name="edit_instance_pool",
                description="Edit/update an existing instance pool configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_pool_id": {"type": "string", "description": "The instance pool ID"},
                        "instance_pool_name": {"type": "string", "description": "New name for the pool"},
                        "node_type_id": {"type": "string", "description": "New node type"},
                        "min_idle_instances": {"type": "integer", "description": "New minimum idle instances"},
                        "max_capacity": {"type": "integer", "description": "New maximum capacity"},
                        "idle_instance_autotermination_minutes": {
                            "type": "integer",
                            "description": "New autotermination time",
                        },
                        "custom_tags": {"type": "object", "description": "New custom tags"},
                    },
                    "required": ["instance_pool_id", "instance_pool_name", "node_type_id"],
                },
            ),
            Tool(
                name="delete_instance_pool",
                description="Delete an instance pool (must have no running clusters)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_pool_id": {"type": "string", "description": "The instance pool ID"}
                    },
                    "required": ["instance_pool_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle instance pool tool calls"""

        if name == "list_instance_pools":
            pools = list(workspace_client.instance_pools.list())
            return [
                {
                    "instance_pool_id": p.instance_pool_id,
                    "instance_pool_name": p.instance_pool_name,
                    "node_type_id": p.node_type_id,
                    "state": p.state.value if p.state else None,
                    "stats": p.stats.as_dict() if p.stats else None,
                }
                for p in pools
            ]

        elif name == "get_instance_pool":
            pool = workspace_client.instance_pools.get(instance_pool_id=arguments["instance_pool_id"])
            return pool.as_dict()

        elif name == "create_instance_pool":
            pool = workspace_client.instance_pools.create(
                instance_pool_name=arguments["instance_pool_name"],
                node_type_id=arguments["node_type_id"],
                min_idle_instances=arguments.get("min_idle_instances", 0),
                max_capacity=arguments.get("max_capacity"),
                idle_instance_autotermination_minutes=arguments.get("idle_instance_autotermination_minutes", 60),
                enable_elastic_disk=arguments.get("enable_elastic_disk", True),
                disk_spec=arguments.get("disk_spec"),
                preloaded_spark_versions=arguments.get("preloaded_spark_versions"),
                aws_attributes=arguments.get("aws_attributes"),
                azure_attributes=arguments.get("azure_attributes"),
                custom_tags=arguments.get("custom_tags"),
            )
            return {"instance_pool_id": pool.instance_pool_id, "status": "created"}

        elif name == "edit_instance_pool":
            workspace_client.instance_pools.edit(
                instance_pool_id=arguments["instance_pool_id"],
                instance_pool_name=arguments["instance_pool_name"],
                node_type_id=arguments["node_type_id"],
                min_idle_instances=arguments.get("min_idle_instances"),
                max_capacity=arguments.get("max_capacity"),
                idle_instance_autotermination_minutes=arguments.get("idle_instance_autotermination_minutes"),
                custom_tags=arguments.get("custom_tags"),
            )
            return {"status": "updated", "instance_pool_id": arguments["instance_pool_id"]}

        elif name == "delete_instance_pool":
            workspace_client.instance_pools.delete(instance_pool_id=arguments["instance_pool_id"])
            return {"status": "deleted", "instance_pool_id": arguments["instance_pool_id"]}

        return None

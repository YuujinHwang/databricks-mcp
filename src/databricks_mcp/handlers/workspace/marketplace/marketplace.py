"""
Databricks Marketplace API Handler
Manage marketplace listings, installations, and fulfillments
https://docs.databricks.com/api/workspace/marketplace
"""
from typing import Any
from mcp.types import Tool


class MarketplaceHandler:
    """Handler for Databricks Marketplace API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            Tool(
                name="list_marketplace_listings",
                description="List all marketplace listings",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_marketplace_listing",
                description="Get listing details",
                inputSchema={
                    "type": "object",
                    "properties": {"id": {"type": "string"}},
                    "required": ["id"],
                },
            ),
            Tool(
                name="list_marketplace_installations",
                description="List installed marketplace assets",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="create_marketplace_installation",
                description="Install a marketplace listing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "listing_id": {"type": "string"},
                        "catalog_name": {"type": "string"},
                        "share_name": {"type": "string"},
                    },
                    "required": ["listing_id"],
                },
            ),
            Tool(
                name="delete_marketplace_installation",
                description="Uninstall marketplace asset",
                inputSchema={
                    "type": "object",
                    "properties": {"installation_id": {"type": "string"}},
                    "required": ["installation_id"],
                },
            ),
            Tool(
                name="list_marketplace_fulfillments",
                description="List fulfillments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "listing_id": {"type": "string"},
                        "max_results": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        if name == "list_marketplace_listings":
            listings = list(workspace_client.marketplace_listings.list(**{k: v for k, v in arguments.items() if v}))
            return [l.as_dict() for l in listings]
        elif name == "get_marketplace_listing":
            return workspace_client.marketplace_listings.get(id=arguments["id"]).as_dict()
        elif name == "list_marketplace_installations":
            installs = list(workspace_client.consumer_installations.list(**{k: v for k, v in arguments.items() if v}))
            return [i.as_dict() for i in installs]
        elif name == "create_marketplace_installation":
            return workspace_client.consumer_installations.create(**arguments).as_dict()
        elif name == "delete_marketplace_installation":
            workspace_client.consumer_installations.delete(installation_id=arguments["installation_id"])
            return {"status": "deleted", "installation_id": arguments["installation_id"]}
        elif name == "list_marketplace_fulfillments":
            fulfillments = list(workspace_client.consumer_fulfillments.list(**{k: v for k, v in arguments.items() if v}))
            return [f.as_dict() for f in fulfillments]
        return None

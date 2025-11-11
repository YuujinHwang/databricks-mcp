"""
Lakeview Dashboards API Handler
Manage Lakeview dashboards (new dashboard experience)
https://docs.databricks.com/api/workspace/lakeview
"""
from typing import Any
from mcp.types import Tool


class DashboardsHandler:
    """Handler for Lakeview Dashboards API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        return [
            # ============ Dashboard Management ============
            Tool(
                name="list_dashboards",
                description="List all Lakeview dashboards",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                },
            ),
            Tool(
                name="get_dashboard",
                description="Get dashboard details",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="create_dashboard",
                description="Create a new Lakeview dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "display_name": {"type": "string"},
                        "warehouse_id": {"type": "string"},
                        "parent_path": {"type": "string"},
                        "serialized_dashboard": {"type": "string"},
                    },
                    "required": ["display_name"],
                },
            ),
            Tool(
                name="update_dashboard",
                description="Update dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "display_name": {"type": "string"},
                        "serialized_dashboard": {"type": "string"},
                        "etag": {"type": "string"},
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="delete_dashboard",
                description="Delete dashboard (trash)",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="migrate_dashboard",
                description="Migrate a dashboard from the old dashboard experience to Lakeview",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source_dashboard_id": {
                            "type": "string",
                            "description": "ID of the legacy dashboard to migrate",
                        },
                        "display_name": {"type": "string", "description": "Display name for new Lakeview dashboard"},
                        "parent_path": {"type": "string", "description": "Parent workspace path"},
                    },
                    "required": ["source_dashboard_id"],
                },
            ),
            # ============ Publishing ============
            Tool(
                name="publish_dashboard",
                description="Publish dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "embed_credentials": {"type": "boolean"},
                        "warehouse_id": {"type": "string"},
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="unpublish_dashboard",
                description="Unpublish dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="get_published_dashboard",
                description="Get published dashboard details",
                inputSchema={
                    "type": "object",
                    "properties": {"dashboard_id": {"type": "string"}},
                    "required": ["dashboard_id"],
                },
            ),
            # ============ Dashboard Schedules ============
            Tool(
                name="list_dashboard_schedules",
                description="List all schedules for a dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string", "description": "Dashboard ID"},
                        "page_size": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="get_dashboard_schedule",
                description="Get dashboard schedule details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id"],
                },
            ),
            Tool(
                name="create_dashboard_schedule",
                description="Create a dashboard refresh schedule",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "display_name": {"type": "string"},
                        "cron_schedule": {
                            "type": "object",
                            "description": "Cron schedule config (quartz_cron_expression, timezone_id)",
                        },
                        "pause_status": {"type": "string", "description": "PAUSED or UNPAUSED"},
                    },
                    "required": ["dashboard_id", "cron_schedule"],
                },
            ),
            Tool(
                name="update_dashboard_schedule",
                description="Update dashboard schedule",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "display_name": {"type": "string"},
                        "cron_schedule": {"type": "object"},
                        "pause_status": {"type": "string"},
                        "etag": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id"],
                },
            ),
            Tool(
                name="delete_dashboard_schedule",
                description="Delete a dashboard schedule",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "etag": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id"],
                },
            ),
            # ============ Schedule Subscriptions ============
            Tool(
                name="list_schedule_subscriptions",
                description="List all subscriptions for a dashboard schedule",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "page_size": {"type": "integer"},
                        "page_token": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id"],
                },
            ),
            Tool(
                name="get_schedule_subscription",
                description="Get schedule subscription details",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "subscription_id": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id", "subscription_id"],
                },
            ),
            Tool(
                name="create_schedule_subscription",
                description="Create a subscription for a dashboard schedule (email notifications)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "subscriber": {
                            "type": "object",
                            "description": "Subscriber info (user_subscriber with user_name or destination_subscriber with destination_id)",
                        },
                    },
                    "required": ["dashboard_id", "schedule_id", "subscriber"],
                },
            ),
            Tool(
                name="delete_schedule_subscription",
                description="Delete a schedule subscription",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {"type": "string"},
                        "schedule_id": {"type": "string"},
                        "subscription_id": {"type": "string"},
                        "etag": {"type": "string"},
                    },
                    "required": ["dashboard_id", "schedule_id", "subscription_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        # ============ Dashboard Management ============
        if name == "list_dashboards":
            dashboards = list(workspace_client.lakeview.list(**{k: v for k, v in arguments.items() if v}))
            return [d.as_dict() for d in dashboards]

        elif name == "get_dashboard":
            return workspace_client.lakeview.get(dashboard_id=arguments["dashboard_id"]).as_dict()

        elif name == "create_dashboard":
            return workspace_client.lakeview.create(**arguments).as_dict()

        elif name == "update_dashboard":
            return workspace_client.lakeview.update(**arguments).as_dict()

        elif name == "delete_dashboard":
            workspace_client.lakeview.trash(dashboard_id=arguments["dashboard_id"])
            return {"status": "deleted", "dashboard_id": arguments["dashboard_id"]}

        elif name == "migrate_dashboard":
            return workspace_client.lakeview.migrate(**arguments).as_dict()

        # ============ Publishing ============
        elif name == "publish_dashboard":
            return workspace_client.lakeview.publish(**arguments).as_dict()

        elif name == "unpublish_dashboard":
            workspace_client.lakeview.unpublish(dashboard_id=arguments["dashboard_id"])
            return {"status": "unpublished", "dashboard_id": arguments["dashboard_id"]}

        elif name == "get_published_dashboard":
            return workspace_client.lakeview.get_published(dashboard_id=arguments["dashboard_id"]).as_dict()

        # ============ Dashboard Schedules ============
        elif name == "list_dashboard_schedules":
            schedules = list(
                workspace_client.lakeview.list_schedules(
                    dashboard_id=arguments["dashboard_id"],
                    page_size=arguments.get("page_size"),
                    page_token=arguments.get("page_token"),
                )
            )
            return [s.as_dict() for s in schedules]

        elif name == "get_dashboard_schedule":
            return workspace_client.lakeview.get_schedule(
                dashboard_id=arguments["dashboard_id"],
                schedule_id=arguments["schedule_id"],
            ).as_dict()

        elif name == "create_dashboard_schedule":
            return workspace_client.lakeview.create_schedule(**arguments).as_dict()

        elif name == "update_dashboard_schedule":
            return workspace_client.lakeview.update_schedule(**arguments).as_dict()

        elif name == "delete_dashboard_schedule":
            workspace_client.lakeview.delete_schedule(
                dashboard_id=arguments["dashboard_id"],
                schedule_id=arguments["schedule_id"],
                etag=arguments.get("etag"),
            )
            return {
                "status": "deleted",
                "dashboard_id": arguments["dashboard_id"],
                "schedule_id": arguments["schedule_id"],
            }

        # ============ Schedule Subscriptions ============
        elif name == "list_schedule_subscriptions":
            subscriptions = list(
                workspace_client.lakeview.list_subscriptions(
                    dashboard_id=arguments["dashboard_id"],
                    schedule_id=arguments["schedule_id"],
                    page_size=arguments.get("page_size"),
                    page_token=arguments.get("page_token"),
                )
            )
            return [s.as_dict() for s in subscriptions]

        elif name == "get_schedule_subscription":
            return workspace_client.lakeview.get_subscription(
                dashboard_id=arguments["dashboard_id"],
                schedule_id=arguments["schedule_id"],
                subscription_id=arguments["subscription_id"],
            ).as_dict()

        elif name == "create_schedule_subscription":
            return workspace_client.lakeview.create_subscription(**arguments).as_dict()

        elif name == "delete_schedule_subscription":
            workspace_client.lakeview.delete_subscription(
                dashboard_id=arguments["dashboard_id"],
                schedule_id=arguments["schedule_id"],
                subscription_id=arguments["subscription_id"],
                etag=arguments.get("etag"),
            )
            return {
                "status": "deleted",
                "dashboard_id": arguments["dashboard_id"],
                "schedule_id": arguments["schedule_id"],
                "subscription_id": arguments["subscription_id"],
            }

        return None

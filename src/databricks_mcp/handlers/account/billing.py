"""
Billing API Handler
Handles account-level billing operations following Databricks Billing API documentation
https://docs.databricks.com/api/account/billableusage
https://docs.databricks.com/api/account/budgets
"""
from typing import Any
from mcp.types import Tool


class BillingHandler:
    """Handler for Databricks Billing API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of billing management tools"""
        return [
            # Billable Usage
            Tool(
                name="download_billable_usage",
                description="Download billable usage logs for the account for a specific date range",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start_month": {
                            "type": "string",
                            "description": "Start month in YYYY-MM format (e.g., '2025-01')",
                        },
                        "end_month": {
                            "type": "string",
                            "description": "End month in YYYY-MM format (e.g., '2025-01')",
                        },
                    },
                    "required": ["start_month", "end_month"],
                },
            ),
            # Budgets
            Tool(
                name="list_budgets",
                description="List all budget configurations for the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of budgets to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_budget",
                description="Get details of a specific budget configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "budget_id": {"type": "string", "description": "The budget ID"}
                    },
                    "required": ["budget_id"],
                },
            ),
            Tool(
                name="create_budget",
                description="Create a new budget configuration for cost management",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "budget_configuration_id": {
                            "type": "string",
                            "description": "Unique identifier for the budget configuration",
                        },
                        "filter": {
                            "type": "object",
                            "description": "Filter criteria for the budget (workspace_id, tags, etc.)",
                        },
                        "target_amount": {
                            "type": "string",
                            "description": "Target budget amount",
                        },
                        "alert_configurations": {
                            "type": "array",
                            "description": "Alert configurations for budget notifications",
                        },
                    },
                    "required": ["budget_configuration_id"],
                },
            ),
            Tool(
                name="update_budget",
                description="Update an existing budget configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "budget_id": {"type": "string", "description": "The budget ID"},
                        "budget_configuration_id": {
                            "type": "string",
                            "description": "Unique identifier for the budget configuration",
                        },
                        "filter": {
                            "type": "object",
                            "description": "Filter criteria for the budget",
                        },
                        "target_amount": {
                            "type": "string",
                            "description": "Target budget amount",
                        },
                        "alert_configurations": {
                            "type": "array",
                            "description": "Alert configurations",
                        },
                    },
                    "required": ["budget_id"],
                },
            ),
            Tool(
                name="delete_budget",
                description="Delete a budget configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "budget_id": {"type": "string", "description": "The budget ID"}
                    },
                    "required": ["budget_id"],
                },
            ),
            # Log Delivery
            Tool(
                name="list_log_delivery_configs",
                description="List all log delivery configurations for the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of configs to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_log_delivery_config",
                description="Get details of a specific log delivery configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_delivery_config_id": {
                            "type": "string",
                            "description": "The log delivery configuration ID",
                        }
                    },
                    "required": ["log_delivery_config_id"],
                },
            ),
            Tool(
                name="create_log_delivery_config",
                description="Create a log delivery configuration for billable usage or audit logs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "config_name": {
                            "type": "string",
                            "description": "Name of the log delivery configuration",
                        },
                        "log_type": {
                            "type": "string",
                            "description": "Type of logs (BILLABLE_USAGE or AUDIT_LOGS)",
                            "enum": ["BILLABLE_USAGE", "AUDIT_LOGS"],
                        },
                        "output_format": {
                            "type": "string",
                            "description": "Output format (JSON or CSV)",
                            "enum": ["JSON", "CSV"],
                        },
                        "credentials_id": {
                            "type": "string",
                            "description": "Credentials ID for accessing the storage location",
                        },
                        "storage_configuration_id": {
                            "type": "string",
                            "description": "Storage configuration ID",
                        },
                        "workspace_ids_filter": {
                            "type": "array",
                            "description": "Optional filter for specific workspace IDs",
                        },
                    },
                    "required": ["config_name", "log_type", "output_format"],
                },
            ),
            Tool(
                name="update_log_delivery_config_status",
                description="Enable or disable a log delivery configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "log_delivery_config_id": {
                            "type": "string",
                            "description": "The log delivery configuration ID",
                        },
                        "status": {
                            "type": "string",
                            "description": "Status to set (ENABLED or DISABLED)",
                            "enum": ["ENABLED", "DISABLED"],
                        },
                    },
                    "required": ["log_delivery_config_id", "status"],
                },
            ),
            # Usage Dashboards
            Tool(
                name="list_usage_dashboards",
                description="List all usage dashboards for the account",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of dashboards to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_usage_dashboard",
                description="Get details of a specific usage dashboard",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_id": {
                            "type": "string",
                            "description": "The usage dashboard ID",
                        }
                    },
                    "required": ["dashboard_id"],
                },
            ),
            Tool(
                name="create_usage_dashboard",
                description="Create a new usage dashboard for visualizing account usage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_name": {
                            "type": "string",
                            "description": "Name of the usage dashboard",
                        },
                        "workspace_id": {
                            "type": "integer",
                            "description": "Workspace ID where the dashboard will be created",
                        },
                    },
                    "required": ["workspace_id"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, account_client, run_operation) -> Any:
        """Handle billing-related tool calls"""

        # Billable Usage
        if name == "download_billable_usage":
            start_month = arguments["start_month"]
            end_month = arguments["end_month"]

            result = account_client.billable_usage.download(
                start_month=start_month, end_month=end_month
            )

            # Convert result to list if it's an iterator
            if hasattr(result, "__iter__"):
                usage_records = list(result)
                return {
                    "usage_records": [r.as_dict() for r in usage_records],
                    "count": len(usage_records),
                    "start_month": start_month,
                    "end_month": end_month,
                }
            else:
                return result.as_dict() if hasattr(result, "as_dict") else result

        # Budgets - List
        elif name == "list_budgets":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            budgets = []
            count = 0
            for budget in account_client.budgets.list():
                if count >= page_size:
                    break
                budgets.append(budget.as_dict())
                count += 1

            return {"budgets": budgets, "count": len(budgets), "page_size": page_size}

        # Budgets - Get
        elif name == "get_budget":
            budget = account_client.budgets.get(budget_id=arguments["budget_id"])
            return budget.as_dict()

        # Budgets - Create
        elif name == "create_budget":
            from databricks.sdk.service.billing import Budget, BudgetConfiguration

            # Build budget configuration
            config = BudgetConfiguration(
                budget_configuration_id=arguments["budget_configuration_id"],
                filter=arguments.get("filter"),
                target_amount=arguments.get("target_amount"),
                alert_configurations=arguments.get("alert_configurations"),
            )

            budget = Budget(budget_configuration=config)

            result = account_client.budgets.create(budget=budget)
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "created"}

        # Budgets - Update
        elif name == "update_budget":
            from databricks.sdk.service.billing import Budget, BudgetConfiguration

            config = BudgetConfiguration(
                budget_configuration_id=arguments.get("budget_configuration_id"),
                filter=arguments.get("filter"),
                target_amount=arguments.get("target_amount"),
                alert_configurations=arguments.get("alert_configurations"),
            )

            budget = Budget(budget_configuration=config)

            result = account_client.budgets.update(budget_id=arguments["budget_id"], budget=budget)
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "updated"}

        # Budgets - Delete
        elif name == "delete_budget":
            account_client.budgets.delete(budget_id=arguments["budget_id"])
            return {"status": "deleted", "budget_id": arguments["budget_id"]}

        # Log Delivery - List
        elif name == "list_log_delivery_configs":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            configs = []
            count = 0
            for config in account_client.log_delivery.list():
                if count >= page_size:
                    break
                configs.append(config.as_dict())
                count += 1

            return {"log_delivery_configs": configs, "count": len(configs), "page_size": page_size}

        # Log Delivery - Get
        elif name == "get_log_delivery_config":
            config = account_client.log_delivery.get(
                log_delivery_configuration_id=arguments["log_delivery_config_id"]
            )
            return config.as_dict()

        # Log Delivery - Create
        elif name == "create_log_delivery_config":
            from databricks.sdk.service.billing import (
                CreateLogDeliveryConfigurationParams,
                LogType,
                OutputFormat,
            )

            log_type_map = {"BILLABLE_USAGE": LogType.BILLABLE_USAGE, "AUDIT_LOGS": LogType.AUDIT_LOGS}

            format_map = {"JSON": OutputFormat.JSON, "CSV": OutputFormat.CSV}

            params = CreateLogDeliveryConfigurationParams(
                config_name=arguments.get("config_name"),
                log_type=log_type_map.get(arguments["log_type"]),
                output_format=format_map.get(arguments["output_format"]),
                credentials_id=arguments.get("credentials_id"),
                storage_configuration_id=arguments.get("storage_configuration_id"),
                workspace_ids_filter=arguments.get("workspace_ids_filter"),
            )

            result = account_client.log_delivery.create(
                log_delivery_configuration=params
            )
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "created"}

        # Log Delivery - Update Status
        elif name == "update_log_delivery_config_status":
            from databricks.sdk.service.billing import LogDeliveryConfigStatus

            status_map = {
                "ENABLED": LogDeliveryConfigStatus.ENABLED,
                "DISABLED": LogDeliveryConfigStatus.DISABLED,
            }

            result = account_client.log_delivery.patch_status(
                log_delivery_configuration_id=arguments["log_delivery_config_id"],
                status=status_map.get(arguments["status"]),
            )
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "updated"}

        # Usage Dashboards - List
        elif name == "list_usage_dashboards":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            dashboards = []
            count = 0
            for dashboard in account_client.usage_dashboards.list():
                if count >= page_size:
                    break
                dashboards.append(dashboard.as_dict())
                count += 1

            return {"usage_dashboards": dashboards, "count": len(dashboards), "page_size": page_size}

        # Usage Dashboards - Get
        elif name == "get_usage_dashboard":
            dashboard = account_client.usage_dashboards.get(dashboard_id=arguments["dashboard_id"])
            return dashboard.as_dict()

        # Usage Dashboards - Create
        elif name == "create_usage_dashboard":
            from databricks.sdk.service.billing import CreateBillingUsageDashboardRequest

            request = CreateBillingUsageDashboardRequest(
                dashboard_name=arguments.get("dashboard_name"),
                workspace_id=arguments["workspace_id"],
            )

            result = account_client.usage_dashboards.create(dashboard=request)
            return result.as_dict() if hasattr(result, "as_dict") else {"status": "created"}

        return None

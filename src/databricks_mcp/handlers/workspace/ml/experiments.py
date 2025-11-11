"""
MLflow Experiments API Handler
Manage MLflow experiments and runs for ML model tracking
https://docs.databricks.com/api/workspace/experiments
"""
from typing import Any
from mcp.types import Tool


class ExperimentsHandler:
    """Handler for MLflow Experiments API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of MLflow experiment tools"""
        return [
            # ============ Experiments ============
            Tool(
                name="list_experiments",
                description="List all MLflow experiments in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "max_results": {"type": "integer", "description": "Maximum results to return"},
                        "page_token": {"type": "string", "description": "Token for pagination"},
                        "view_type": {
                            "type": "string",
                            "description": "ACTIVE_ONLY, DELETED_ONLY, or ALL (default: ACTIVE_ONLY)",
                        },
                    },
                },
            ),
            Tool(
                name="get_experiment",
                description="Get details of a specific MLflow experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"}
                    },
                    "required": ["experiment_id"],
                },
            ),
            Tool(
                name="get_experiment_by_name",
                description="Get experiment by name (path)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_name": {"type": "string", "description": "Experiment name/path"}
                    },
                    "required": ["experiment_name"],
                },
            ),
            Tool(
                name="create_experiment",
                description="Create a new MLflow experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Experiment name (path in workspace)"},
                        "artifact_location": {
                            "type": "string",
                            "description": "Optional artifact storage location",
                        },
                        "tags": {
                            "type": "array",
                            "description": "Optional tags (array of {key, value} objects)",
                        },
                    },
                    "required": ["name"],
                },
            ),
            Tool(
                name="update_experiment",
                description="Update experiment name",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"},
                        "new_name": {"type": "string", "description": "New experiment name"},
                    },
                    "required": ["experiment_id", "new_name"],
                },
            ),
            Tool(
                name="delete_experiment",
                description="Delete (archive) an MLflow experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"}
                    },
                    "required": ["experiment_id"],
                },
            ),
            Tool(
                name="restore_experiment",
                description="Restore a deleted MLflow experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"}
                    },
                    "required": ["experiment_id"],
                },
            ),
            Tool(
                name="set_experiment_tag",
                description="Set a tag on an experiment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"},
                        "key": {"type": "string", "description": "Tag key"},
                        "value": {"type": "string", "description": "Tag value"},
                    },
                    "required": ["experiment_id", "key", "value"],
                },
            ),
            # ============ Runs (Basic operations) ============
            Tool(
                name="search_runs",
                description="Search MLflow runs across experiments",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_ids": {
                            "type": "array",
                            "description": "List of experiment IDs to search",
                        },
                        "filter": {
                            "type": "string",
                            "description": "Filter expression (e.g., \"metrics.accuracy > 0.9\")",
                        },
                        "max_results": {"type": "integer", "description": "Maximum results"},
                        "order_by": {
                            "type": "array",
                            "description": "Order by clauses (e.g., [\"metrics.accuracy DESC\"])",
                        },
                        "page_token": {"type": "string", "description": "Pagination token"},
                    },
                },
            ),
            Tool(
                name="get_run",
                description="Get details of a specific MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"}
                    },
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="create_run",
                description="Create a new MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "experiment_id": {"type": "string", "description": "The experiment ID"},
                        "run_name": {"type": "string", "description": "Optional run name"},
                        "start_time": {"type": "integer", "description": "Start time (Unix timestamp ms)"},
                        "tags": {"type": "array", "description": "Run tags"},
                    },
                    "required": ["experiment_id"],
                },
            ),
            Tool(
                name="update_run",
                description="Update run status and end time",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"},
                        "status": {
                            "type": "string",
                            "description": "RUNNING, SCHEDULED, FINISHED, FAILED, KILLED",
                        },
                        "end_time": {"type": "integer", "description": "End time (Unix timestamp ms)"},
                    },
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="delete_run",
                description="Delete (archive) an MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"}
                    },
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="restore_run",
                description="Restore a deleted MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"}
                    },
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="log_metric",
                description="Log a metric for an MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"},
                        "key": {"type": "string", "description": "Metric name"},
                        "value": {"type": "number", "description": "Metric value"},
                        "timestamp": {"type": "integer", "description": "Timestamp (Unix ms)"},
                        "step": {"type": "integer", "description": "Training step"},
                    },
                    "required": ["run_id", "key", "value"],
                },
            ),
            Tool(
                name="log_param",
                description="Log a parameter for an MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"},
                        "key": {"type": "string", "description": "Parameter name"},
                        "value": {"type": "string", "description": "Parameter value"},
                    },
                    "required": ["run_id", "key", "value"],
                },
            ),
            Tool(
                name="set_run_tag",
                description="Set a tag on an MLflow run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "run_id": {"type": "string", "description": "The run ID"},
                        "key": {"type": "string", "description": "Tag key"},
                        "value": {"type": "string", "description": "Tag value"},
                    },
                    "required": ["run_id", "key", "value"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle MLflow experiments tool calls"""

        # ============ Experiments ============
        if name == "list_experiments":
            kwargs = {}
            if "max_results" in arguments:
                kwargs["max_results"] = arguments["max_results"]
            if "page_token" in arguments:
                kwargs["page_token"] = arguments["page_token"]
            if "view_type" in arguments:
                kwargs["view_type"] = arguments["view_type"]

            experiments = list(workspace_client.experiments.list(**kwargs))
            return [e.as_dict() for e in experiments]

        elif name == "get_experiment":
            exp = workspace_client.experiments.get_experiment(experiment_id=arguments["experiment_id"])
            return exp.as_dict()

        elif name == "get_experiment_by_name":
            exp = workspace_client.experiments.get_by_name(experiment_name=arguments["experiment_name"])
            return exp.as_dict()

        elif name == "create_experiment":
            exp_id = workspace_client.experiments.create_experiment(
                name=arguments["name"],
                artifact_location=arguments.get("artifact_location"),
                tags=arguments.get("tags"),
            )
            return {"experiment_id": exp_id, "status": "created"}

        elif name == "update_experiment":
            workspace_client.experiments.update_experiment(
                experiment_id=arguments["experiment_id"],
                new_name=arguments["new_name"],
            )
            return {"status": "updated", "experiment_id": arguments["experiment_id"]}

        elif name == "delete_experiment":
            workspace_client.experiments.delete_experiment(experiment_id=arguments["experiment_id"])
            return {"status": "deleted", "experiment_id": arguments["experiment_id"]}

        elif name == "restore_experiment":
            workspace_client.experiments.restore_experiment(experiment_id=arguments["experiment_id"])
            return {"status": "restored", "experiment_id": arguments["experiment_id"]}

        elif name == "set_experiment_tag":
            workspace_client.experiments.set_experiment_tag(
                experiment_id=arguments["experiment_id"],
                key=arguments["key"],
                value=arguments["value"],
            )
            return {"status": "tag_set", "experiment_id": arguments["experiment_id"]}

        # ============ Runs ============
        elif name == "search_runs":
            kwargs = {}
            if "experiment_ids" in arguments:
                kwargs["experiment_ids"] = arguments["experiment_ids"]
            if "filter" in arguments:
                kwargs["filter_string"] = arguments["filter"]
            if "max_results" in arguments:
                kwargs["max_results"] = arguments["max_results"]
            if "order_by" in arguments:
                kwargs["order_by"] = arguments["order_by"]
            if "page_token" in arguments:
                kwargs["page_token"] = arguments["page_token"]

            runs = list(workspace_client.experiments.search_runs(**kwargs))
            return [r.as_dict() for r in runs]

        elif name == "get_run":
            run = workspace_client.experiments.get_run(run_id=arguments["run_id"])
            return run.as_dict()

        elif name == "create_run":
            run = workspace_client.experiments.create_run(
                experiment_id=arguments["experiment_id"],
                run_name=arguments.get("run_name"),
                start_time=arguments.get("start_time"),
                tags=arguments.get("tags"),
            )
            return run.as_dict()

        elif name == "update_run":
            kwargs = {"run_id": arguments["run_id"]}
            if "status" in arguments:
                kwargs["status"] = arguments["status"]
            if "end_time" in arguments:
                kwargs["end_time"] = arguments["end_time"]

            run = workspace_client.experiments.update_run(**kwargs)
            return run.as_dict()

        elif name == "delete_run":
            workspace_client.experiments.delete_run(run_id=arguments["run_id"])
            return {"status": "deleted", "run_id": arguments["run_id"]}

        elif name == "restore_run":
            workspace_client.experiments.restore_run(run_id=arguments["run_id"])
            return {"status": "restored", "run_id": arguments["run_id"]}

        elif name == "log_metric":
            workspace_client.experiments.log_metric(
                run_id=arguments["run_id"],
                key=arguments["key"],
                value=arguments["value"],
                timestamp=arguments.get("timestamp"),
                step=arguments.get("step", 0),
            )
            return {"status": "logged", "run_id": arguments["run_id"], "metric": arguments["key"]}

        elif name == "log_param":
            workspace_client.experiments.log_param(
                run_id=arguments["run_id"],
                key=arguments["key"],
                value=arguments["value"],
            )
            return {"status": "logged", "run_id": arguments["run_id"], "param": arguments["key"]}

        elif name == "set_run_tag":
            workspace_client.experiments.set_tag(
                run_id=arguments["run_id"],
                key=arguments["key"],
                value=arguments["value"],
            )
            return {"status": "tag_set", "run_id": arguments["run_id"]}

        return None

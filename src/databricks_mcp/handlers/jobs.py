"""
Jobs API Handler
Handles all job-related operations following Databricks Jobs API documentation
https://docs.databricks.com/api/workspace/jobs
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from mcp.types import Tool


class JobsHandler:
    """Handler for Databricks Jobs API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of job management tools"""
        return [
            Tool(
                name="list_jobs",
                description="List all jobs in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of jobs to return",
                        },
                        "name": {"type": "string", "description": "Filter by job name"},
                    },
                },
            ),
            Tool(
                name="get_job",
                description="Get details of a specific job",
                inputSchema={
                    "type": "object",
                    "properties": {"job_id": {"type": "integer", "description": "The job ID"}},
                    "required": ["job_id"],
                },
            ),
            Tool(
                name="create_job",
                description="Create a new job",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Job name"},
                        "tasks": {
                            "type": "string",
                            "description": "JSON string of task configurations",
                        },
                        "job_clusters": {
                            "type": "string",
                            "description": "JSON string of job cluster configurations",
                        },
                    },
                    "required": ["name", "tasks"],
                },
            ),
            Tool(
                name="run_job",
                description="Trigger a job run",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_id": {"type": "integer", "description": "The job ID"},
                        "notebook_params": {
                            "type": "string",
                            "description": "JSON string of notebook parameters",
                        },
                    },
                    "required": ["job_id"],
                },
            ),
            Tool(
                name="get_run",
                description="Get details of a specific job run",
                inputSchema={
                    "type": "object",
                    "properties": {"run_id": {"type": "integer", "description": "The run ID"}},
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="cancel_run",
                description="Cancel a job run",
                inputSchema={
                    "type": "object",
                    "properties": {"run_id": {"type": "integer", "description": "The run ID"}},
                    "required": ["run_id"],
                },
            ),
            Tool(
                name="delete_job",
                description="Delete a job",
                inputSchema={
                    "type": "object",
                    "properties": {"job_id": {"type": "integer", "description": "The job ID"}},
                    "required": ["job_id"],
                },
            ),
            Tool(
                name="get_jobs_batch",
                description="Get details of multiple jobs in a single operation (batch get)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Array of job IDs to fetch"
                        }
                    },
                    "required": ["job_ids"],
                },
            ),
            Tool(
                name="delete_jobs_batch",
                description="Delete multiple jobs in a single operation (batch delete)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Array of job IDs to delete"
                        }
                    },
                    "required": ["job_ids"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """Handle job-related tool calls"""
        if name == "list_jobs":
            kwargs = {}
            if "limit" in arguments:
                kwargs["limit"] = arguments["limit"]
            if "name" in arguments:
                kwargs["name"] = arguments["name"]

            def _list_jobs():
                jobs = []
                for j in workspace_client.jobs.list(**kwargs):
                    jobs.append({
                        "job_id": j.job_id,
                        "settings": {
                            "name": j.settings.name if j.settings else None,
                            "tasks": len(j.settings.tasks) if j.settings and j.settings.tasks else 0,
                        },
                    })
                return jobs

            jobs = run_operation(_list_jobs)
            return {"jobs": jobs, "count": len(jobs)}

        elif name == "get_job":
            job = run_operation(lambda: workspace_client.jobs.get(job_id=arguments["job_id"]))
            return job.as_dict()

        elif name == "create_job":
            tasks = json.loads(arguments["tasks"])
            job_clusters = (
                json.loads(arguments["job_clusters"])
                if "job_clusters" in arguments
                else None
            )

            job = run_operation(lambda: workspace_client.jobs.create(
                name=arguments["name"], tasks=tasks, job_clusters=job_clusters
            ))
            return {"job_id": job.job_id, "status": "created"}

        elif name == "run_job":
            kwargs = {"job_id": arguments["job_id"]}
            if "notebook_params" in arguments:
                kwargs["notebook_params"] = json.loads(arguments["notebook_params"])

            run = run_operation(lambda: workspace_client.jobs.run_now(**kwargs).result())
            return {"run_id": run.run_id, "status": "completed"}

        elif name == "get_run":
            run = workspace_client.jobs.get_run(run_id=arguments["run_id"])
            return run.as_dict()

        elif name == "cancel_run":
            workspace_client.jobs.cancel_run(run_id=arguments["run_id"])
            return {"status": "cancelled", "run_id": arguments["run_id"]}

        elif name == "delete_job":
            workspace_client.jobs.delete(job_id=arguments["job_id"])
            return {"status": "deleted", "job_id": arguments["job_id"]}

        elif name == "get_jobs_batch":
            job_ids = arguments["job_ids"]

            def get_job(job_id):
                try:
                    job = workspace_client.jobs.get(job_id=job_id)
                    return {"job_id": job_id, "data": job.as_dict(), "status": "success"}
                except Exception as e:
                    return {"job_id": job_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_job, jid) for jid in job_ids]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(job_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_jobs_batch":
            job_ids = arguments["job_ids"]

            def delete_job(job_id):
                try:
                    workspace_client.jobs.delete(job_id=job_id)
                    return {"job_id": job_id, "status": "success"}
                except Exception as e:
                    return {"job_id": job_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_job, jid) for jid in job_ids]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(job_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None

"""
Clusters API Handler
Handles all cluster-related operations following Databricks Clusters API documentation
https://docs.databricks.com/api/workspace/clusters
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from mcp.types import Tool


class ClustersHandler:
    """Handler for Databricks Clusters API operations"""

    @staticmethod
    def get_tools() -> list[Tool]:
        """Return list of cluster management tools"""
        return [
            Tool(
                name="list_clusters",
                description="List all clusters in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "page_size": {
                            "type": "integer",
                            "description": "Maximum number of clusters to return (default: 100, max: 1000)",
                        },
                    },
                },
            ),
            Tool(
                name="get_cluster",
                description="Get details of a specific cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_id": {"type": "string", "description": "The cluster ID"}
                    },
                    "required": ["cluster_id"],
                },
            ),
            Tool(
                name="create_cluster",
                description="Create a new cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_name": {"type": "string", "description": "Name for the cluster"},
                        "spark_version": {"type": "string", "description": "Spark version"},
                        "node_type_id": {"type": "string", "description": "Node type"},
                        "num_workers": {"type": "integer", "description": "Number of workers"},
                        "autoscale": {
                            "type": "object",
                            "description": "Autoscale configuration",
                            "properties": {
                                "min_workers": {"type": "integer"},
                                "max_workers": {"type": "integer"},
                            },
                        },
                    },
                    "required": ["cluster_name", "spark_version", "node_type_id"],
                },
            ),
            Tool(
                name="start_cluster",
                description="Start a terminated cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_id": {"type": "string", "description": "The cluster ID"}
                    },
                    "required": ["cluster_id"],
                },
            ),
            Tool(
                name="terminate_cluster",
                description="Terminate a running cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_id": {"type": "string", "description": "The cluster ID"}
                    },
                    "required": ["cluster_id"],
                },
            ),
            Tool(
                name="delete_cluster",
                description="Permanently delete a cluster",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_id": {"type": "string", "description": "The cluster ID"}
                    },
                    "required": ["cluster_id"],
                },
            ),
            Tool(
                name="get_clusters_batch",
                description="Get details of multiple clusters in a single operation (batch get)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of cluster IDs to fetch"
                        }
                    },
                    "required": ["cluster_ids"],
                },
            ),
            Tool(
                name="delete_clusters_batch",
                description="Permanently delete multiple clusters in a single operation (batch delete)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cluster_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of cluster IDs to delete"
                        }
                    },
                    "required": ["cluster_ids"],
                },
            ),
        ]

    @staticmethod
    def handle(name: str, arguments: Any, workspace_client, run_operation) -> Any:
        """
        Handle cluster-related tool calls

        Args:
            name: Tool name
            arguments: Tool arguments
            workspace_client: Databricks workspace client instance
            run_operation: Function to wrap operations with retry logic

        Returns:
            Operation result
        """
        if name == "list_clusters":
            page_size = arguments.get("page_size", 100)
            page_size = min(page_size, 1000)

            def _list_clusters_paginated():
                clusters = []
                count = 0
                for c in workspace_client.clusters.list():
                    if count >= page_size:
                        break
                    clusters.append({
                        "cluster_id": c.cluster_id,
                        "cluster_name": c.cluster_name,
                        "state": str(c.state),
                        "spark_version": c.spark_version,
                        "node_type_id": c.node_type_id,
                        "num_workers": c.num_workers,
                    })
                    count += 1
                return clusters

            clusters = run_operation(_list_clusters_paginated)
            return {
                "clusters": clusters,
                "count": len(clusters),
                "page_size": page_size,
                "note": f"Returned {len(clusters)} clusters (limited to {page_size}). Use page_size parameter to adjust."
            }

        elif name == "get_cluster":
            cluster = run_operation(
                lambda: workspace_client.clusters.get(cluster_id=arguments["cluster_id"])
            )
            return cluster.as_dict()

        elif name == "create_cluster":
            from databricks.sdk.service.compute import CreateCluster, AutoScale

            create_args = {
                "cluster_name": arguments["cluster_name"],
                "spark_version": arguments["spark_version"],
                "node_type_id": arguments["node_type_id"],
            }

            if "num_workers" in arguments:
                create_args["num_workers"] = arguments["num_workers"]
            elif "autoscale" in arguments:
                autoscale = arguments["autoscale"]
                create_args["autoscale"] = AutoScale(
                    min_workers=autoscale.get("min_workers"),
                    max_workers=autoscale.get("max_workers"),
                )

            cluster = run_operation(
                lambda: workspace_client.clusters.create(**create_args).result()
            )
            return {"cluster_id": cluster.cluster_id, "status": "created"}

        elif name == "start_cluster":
            run_operation(
                lambda: workspace_client.clusters.start(cluster_id=arguments["cluster_id"]).result()
            )
            return {"status": "started", "cluster_id": arguments["cluster_id"]}

        elif name == "terminate_cluster":
            run_operation(
                lambda: workspace_client.clusters.delete(cluster_id=arguments["cluster_id"]).result()
            )
            return {"status": "terminated", "cluster_id": arguments["cluster_id"]}

        elif name == "delete_cluster":
            run_operation(
                lambda: workspace_client.clusters.permanent_delete(cluster_id=arguments["cluster_id"])
            )
            return {"status": "deleted", "cluster_id": arguments["cluster_id"]}

        elif name == "get_clusters_batch":
            cluster_ids = arguments["cluster_ids"]

            def get_cluster(cluster_id):
                try:
                    cluster = workspace_client.clusters.get(cluster_id=cluster_id)
                    return {"cluster_id": cluster_id, "data": cluster.as_dict(), "status": "success"}
                except Exception as e:
                    return {"cluster_id": cluster_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_cluster, cid) for cid in cluster_ids]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(cluster_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_clusters_batch":
            cluster_ids = arguments["cluster_ids"]

            def delete_cluster(cluster_id):
                try:
                    workspace_client.clusters.permanent_delete(cluster_id=cluster_id)
                    return {"cluster_id": cluster_id, "status": "success"}
                except Exception as e:
                    return {"cluster_id": cluster_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_cluster, cid) for cid in cluster_ids]
                results = [future.result() for future in as_completed(futures)]

            return {
                "total": len(cluster_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        return None

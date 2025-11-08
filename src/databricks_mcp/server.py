#!/usr/bin/env python3
"""
Databricks MCP Server

A Model Context Protocol (MCP) server that provides access to Databricks REST APIs,
including both Workspace and Account level operations.
"""

import os
import json
import logging
import asyncio
from typing import Any, Optional
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

from mcp.server import Server
from mcp.types import Tool, TextContent
from databricks.sdk import WorkspaceClient, AccountClient
from databricks.sdk.core import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("databricks-mcp-server")

# Global clients (will be initialized on first use)
_workspace_client: Optional[WorkspaceClient] = None
_account_client: Optional[AccountClient] = None


def get_workspace_client() -> WorkspaceClient:
    """Get or create workspace client."""
    global _workspace_client
    if _workspace_client is None:
        # Check if OAuth U2M (User-to-Machine) should be used
        auth_type = os.getenv("DATABRICKS_AUTH_TYPE", "").lower()

        if auth_type == "oauth-u2m" or auth_type == "oauth":
            # OAuth U2M authentication - will open browser for user login
            from databricks.sdk.core import Config

            config_kwargs = {
                "host": os.getenv("DATABRICKS_HOST"),
                "auth_type": "oauth-u2m",
            }

            # Optional: specify OAuth client ID if using custom OAuth app
            if os.getenv("DATABRICKS_CLIENT_ID"):
                config_kwargs["client_id"] = os.getenv("DATABRICKS_CLIENT_ID")

            logger.info("Using OAuth U2M authentication - browser login required")
            _workspace_client = WorkspaceClient(**config_kwargs)
        else:
            # Default: Authentication via environment variables or ~/.databrickscfg
            # Supports: PAT tokens, OAuth M2M, Azure CLI, etc.
            _workspace_client = WorkspaceClient()

        logger.info(f"Initialized WorkspaceClient for {_workspace_client.config.host}")
    return _workspace_client


def get_account_client() -> AccountClient:
    """Get or create account client."""
    global _account_client
    if _account_client is None:
        account_id = os.getenv("DATABRICKS_ACCOUNT_ID")
        if not account_id:
            raise ValueError(
                "DATABRICKS_ACCOUNT_ID environment variable required for account operations"
            )

        # Check if OAuth U2M should be used
        auth_type = os.getenv("DATABRICKS_AUTH_TYPE", "").lower()

        if auth_type == "oauth-u2m" or auth_type == "oauth":
            # OAuth U2M authentication
            config_kwargs = {
                "host": os.getenv("DATABRICKS_ACCOUNT_HOST", "https://accounts.cloud.databricks.com"),
                "account_id": account_id,
                "auth_type": "oauth-u2m",
            }

            if os.getenv("DATABRICKS_CLIENT_ID"):
                config_kwargs["client_id"] = os.getenv("DATABRICKS_CLIENT_ID")

            logger.info("Using OAuth U2M authentication for account client")
            _account_client = AccountClient(**config_kwargs)
        else:
            # Default authentication
            _account_client = AccountClient(account_id=account_id)

        logger.info(f"Initialized AccountClient for account {account_id}")
    return _account_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Databricks API tools."""
    return [
        # ============ Cluster Management ============
        Tool(
            name="list_clusters",
            description="List all clusters in the workspace",
            inputSchema={
                "type": "object",
                "properties": {},
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
        # ============ Jobs Management ============
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
        # ============ Workspace Management ============
        Tool(
            name="list_workspace_objects",
            description="List objects in a workspace directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Workspace path (default: /)",
                        "default": "/",
                    }
                },
            },
        ),
        Tool(
            name="get_workspace_object_status",
            description="Get status of a workspace object",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Workspace object path"}
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="export_workspace_object",
            description="Export a notebook or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Workspace path to export"},
                    "format": {
                        "type": "string",
                        "description": "Export format: SOURCE, HTML, JUPYTER, DBC",
                        "enum": ["SOURCE", "HTML", "JUPYTER", "DBC"],
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="delete_workspace_object",
            description="Delete a workspace object (notebook or directory)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Workspace path to delete"},
                    "recursive": {
                        "type": "boolean",
                        "description": "Recursively delete directory",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="mkdirs",
            description="Create a directory in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Workspace path to create"}
                },
                "required": ["path"],
            },
        ),
        # ============ DBFS (Databricks File System) ============
        Tool(
            name="list_dbfs",
            description="List files in DBFS directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "DBFS path (e.g., dbfs:/path/to/dir)",
                    }
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="get_dbfs_status",
            description="Get status of a DBFS file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "DBFS path"}
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="delete_dbfs",
            description="Delete a DBFS file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "DBFS path to delete"},
                    "recursive": {
                        "type": "boolean",
                        "description": "Recursively delete directory",
                    },
                },
                "required": ["path"],
            },
        ),
        # ============ Repos (Git Integration) ============
        Tool(
            name="list_repos",
            description="List all repos in the workspace",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_repo",
            description="Get details of a specific repo",
            inputSchema={
                "type": "object",
                "properties": {"repo_id": {"type": "string", "description": "The repo ID"}},
                "required": ["repo_id"],
            },
        ),
        Tool(
            name="create_repo",
            description="Create a new repo from Git",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Git repository URL"},
                    "provider": {
                        "type": "string",
                        "description": "Git provider: gitHub, bitbucketCloud, gitLab, etc.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Workspace path for the repo",
                    },
                },
                "required": ["url", "provider"],
            },
        ),
        Tool(
            name="update_repo",
            description="Update a repo (pull changes, change branch)",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_id": {"type": "string", "description": "The repo ID"},
                    "branch": {"type": "string", "description": "Branch name to checkout"},
                    "tag": {"type": "string", "description": "Tag to checkout"},
                },
                "required": ["repo_id"],
            },
        ),
        Tool(
            name="delete_repo",
            description="Delete a repo",
            inputSchema={
                "type": "object",
                "properties": {"repo_id": {"type": "string", "description": "The repo ID"}},
                "required": ["repo_id"],
            },
        ),
        # ============ SQL Warehouses ============
        Tool(
            name="list_warehouses",
            description="List all SQL warehouses",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_warehouse",
            description="Get details of a specific SQL warehouse",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                },
                "required": ["warehouse_id"],
            },
        ),
        Tool(
            name="start_warehouse",
            description="Start a SQL warehouse",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                },
                "required": ["warehouse_id"],
            },
        ),
        Tool(
            name="stop_warehouse",
            description="Stop a SQL warehouse",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {"type": "string", "description": "The warehouse ID"}
                },
                "required": ["warehouse_id"],
            },
        ),
        Tool(
            name="get_warehouses_batch",
            description="Get details of multiple SQL warehouses in a single operation (batch get)",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of warehouse IDs to fetch"
                    }
                },
                "required": ["warehouse_ids"],
            },
        ),
        # ============ Unity Catalog - Catalogs ============
        Tool(
            name="list_catalogs",
            description="List all Unity Catalog catalogs",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_catalog",
            description="Get details of a specific catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"}
                },
                "required": ["catalog_name"],
            },
        ),
        Tool(
            name="create_catalog",
            description="Create a new Unity Catalog catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"},
                    "comment": {"type": "string", "description": "Catalog description"},
                },
                "required": ["catalog_name"],
            },
        ),
        Tool(
            name="delete_catalog",
            description="Delete a Unity Catalog catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"},
                    "force": {
                        "type": "boolean",
                        "description": "Force delete (delete non-empty catalog)",
                    },
                },
                "required": ["catalog_name"],
            },
        ),
        # ============ Unity Catalog - Schemas ============
        Tool(
            name="list_schemas",
            description="List schemas in a catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"}
                },
                "required": ["catalog_name"],
            },
        ),
        Tool(
            name="get_schema",
            description="Get details of a specific schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_full_name": {
                        "type": "string",
                        "description": "Full schema name (catalog.schema)",
                    }
                },
                "required": ["schema_full_name"],
            },
        ),
        Tool(
            name="create_schema",
            description="Create a new schema in a catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"},
                    "schema_name": {"type": "string", "description": "The schema name"},
                    "comment": {"type": "string", "description": "Schema description"},
                },
                "required": ["catalog_name", "schema_name"],
            },
        ),
        Tool(
            name="delete_schema",
            description="Delete a schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_full_name": {
                        "type": "string",
                        "description": "Full schema name (catalog.schema)",
                    }
                },
                "required": ["schema_full_name"],
            },
        ),
        # ============ Unity Catalog - Tables ============
        Tool(
            name="list_tables",
            description="List tables in a schema",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {"type": "string", "description": "The catalog name"},
                    "schema_name": {"type": "string", "description": "The schema name"},
                },
                "required": ["catalog_name", "schema_name"],
            },
        ),
        Tool(
            name="get_table",
            description="Get details of a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_full_name": {
                        "type": "string",
                        "description": "Full table name (catalog.schema.table)",
                    }
                },
                "required": ["table_full_name"],
            },
        ),
        Tool(
            name="delete_table",
            description="Delete a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_full_name": {
                        "type": "string",
                        "description": "Full table name (catalog.schema.table)",
                    }
                },
                "required": ["table_full_name"],
            },
        ),
        Tool(
            name="delete_tables_batch",
            description="Delete multiple tables in a single operation (batch delete)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_full_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of full table names (catalog.schema.table) to delete"
                    }
                },
                "required": ["table_full_names"],
            },
        ),
        # ============ Secrets Management ============
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
        # ============ Pipelines (Delta Live Tables) ============
        Tool(
            name="list_pipelines",
            description="List all Delta Live Tables pipelines",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_pipeline",
            description="Get details of a specific pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                },
                "required": ["pipeline_id"],
            },
        ),
        Tool(
            name="start_pipeline_update",
            description="Start a pipeline update",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                },
                "required": ["pipeline_id"],
            },
        ),
        Tool(
            name="stop_pipeline",
            description="Stop a pipeline",
            inputSchema={
                "type": "object",
                "properties": {
                    "pipeline_id": {"type": "string", "description": "The pipeline ID"}
                },
                "required": ["pipeline_id"],
            },
        ),
        # ============ Account Management (Account API) ============
        Tool(
            name="list_account_workspaces",
            description="List all workspaces in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_account_workspace",
            description="Get details of a specific workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_id": {"type": "integer", "description": "The workspace ID"}
                },
                "required": ["workspace_id"],
            },
        ),
        Tool(
            name="list_account_users",
            description="List all users in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_account_user",
            description="Get details of a specific user",
            inputSchema={
                "type": "object",
                "properties": {"user_id": {"type": "string", "description": "The user ID"}},
                "required": ["user_id"],
            },
        ),
        Tool(
            name="list_account_groups",
            description="List all groups in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_account_group",
            description="Get details of a specific group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": "The group ID"}
                },
                "required": ["group_id"],
            },
        ),
        Tool(
            name="list_account_service_principals",
            description="List all service principals in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_account_metastores",
            description="List all Unity Catalog metastores in the account",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_account_metastore",
            description="Get details of a specific metastore",
            inputSchema={
                "type": "object",
                "properties": {
                    "metastore_id": {"type": "string", "description": "The metastore ID"}
                },
                "required": ["metastore_id"],
            },
        ),
        # ============ SQL Statement Execution ============
        Tool(
            name="execute_statement",
            description="Execute a SQL statement on a SQL warehouse and return results",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string",
                        "description": "The SQL warehouse ID to execute the statement on",
                    },
                    "statement": {
                        "type": "string",
                        "description": "The SQL statement to execute",
                    },
                    "catalog": {
                        "type": "string",
                        "description": "The catalog to use (optional)",
                    },
                    "schema": {
                        "type": "string",
                        "description": "The schema to use (optional)",
                    },
                    "wait_timeout": {
                        "type": "string",
                        "description": "Time to wait for results (e.g., '30s'). Use '0s' for async execution. Default is '10s'",
                    },
                    "row_limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                    },
                },
                "required": ["warehouse_id", "statement"],
            },
        ),
        Tool(
            name="get_statement",
            description="Get the status and results of a SQL statement execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "statement_id": {
                        "type": "string",
                        "description": "The statement ID returned from execute_statement",
                    }
                },
                "required": ["statement_id"],
            },
        ),
        Tool(
            name="cancel_statement_execution",
            description="Cancel an executing SQL statement",
            inputSchema={
                "type": "object",
                "properties": {
                    "statement_id": {
                        "type": "string",
                        "description": "The statement ID to cancel",
                    }
                },
                "required": ["statement_id"],
            },
        ),
        Tool(
            name="execute_statements_batch",
            description="Execute multiple SQL statements sequentially in a single operation (batch execution)",
            inputSchema={
                "type": "object",
                "properties": {
                    "warehouse_id": {
                        "type": "string",
                        "description": "The SQL warehouse ID to execute statements on",
                    },
                    "statements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Array of SQL statements to execute sequentially",
                    },
                    "catalog": {
                        "type": "string",
                        "description": "The catalog to use (optional)",
                    },
                    "schema": {
                        "type": "string",
                        "description": "The schema to use (optional)",
                    },
                    "wait_timeout": {
                        "type": "string",
                        "description": "Time to wait for results per statement (e.g., '30s'). Default is '10s'",
                    },
                    "row_limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return per statement",
                    },
                },
                "required": ["warehouse_id", "statements"],
            },
        ),
        # ============ Genie (AI/BI) ============
        Tool(
            name="start_genie_conversation",
            description="Start a new conversation in a Genie space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The Genie space ID",
                    }
                },
                "required": ["space_id"],
            },
        ),
        Tool(
            name="create_genie_message",
            description="Create a message in a Genie conversation (ask Genie a question)",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {
                        "type": "string",
                        "description": "The Genie space ID",
                    },
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID",
                    },
                    "content": {
                        "type": "string",
                        "description": "The message content (your question to Genie)",
                    },
                },
                "required": ["space_id", "conversation_id", "content"],
            },
        ),
        Tool(
            name="get_genie_message",
            description="Get details of a specific message in a Genie conversation",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "The Genie space ID"},
                    "conversation_id": {"type": "string", "description": "The conversation ID"},
                    "message_id": {"type": "string", "description": "The message ID"},
                },
                "required": ["space_id", "conversation_id", "message_id"],
            },
        ),
        Tool(
            name="get_genie_message_query_result",
            description="Get SQL query result from a Genie message that executed a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_id": {"type": "string", "description": "The Genie space ID"},
                    "conversation_id": {"type": "string", "description": "The conversation ID"},
                    "message_id": {"type": "string", "description": "The message ID"},
                    "attachment_id": {
                        "type": "string",
                        "description": "The attachment ID (query attachment)",
                    },
                },
                "required": ["space_id", "conversation_id", "message_id", "attachment_id"],
            },
        ),
        # ============ Vector Search ============
        Tool(
            name="list_vector_search_endpoints",
            description="List all vector search endpoints",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_vector_search_endpoint",
            description="Get details of a vector search endpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_name": {
                        "type": "string",
                        "description": "The endpoint name",
                    }
                },
                "required": ["endpoint_name"],
            },
        ),
        Tool(
            name="list_vector_search_indexes",
            description="List vector search indexes for an endpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_name": {
                        "type": "string",
                        "description": "The endpoint name",
                    }
                },
                "required": ["endpoint_name"],
            },
        ),
        Tool(
            name="get_vector_search_index",
            description="Get details of a vector search index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index_name": {
                        "type": "string",
                        "description": "The full index name (catalog.schema.index)",
                    }
                },
                "required": ["index_name"],
            },
        ),
        # ============ Serving Endpoints ============
        Tool(
            name="list_serving_endpoints",
            description="List all model serving endpoints",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_serving_endpoint",
            description="Get details of a serving endpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_name": {
                        "type": "string",
                        "description": "The endpoint name",
                    }
                },
                "required": ["endpoint_name"],
            },
        ),
        Tool(
            name="query_serving_endpoint",
            description="Query a serving endpoint with input data",
            inputSchema={
                "type": "object",
                "properties": {
                    "endpoint_name": {
                        "type": "string",
                        "description": "The endpoint name",
                    },
                    "inputs": {
                        "type": "string",
                        "description": "JSON string of input data for the model",
                    },
                },
                "required": ["endpoint_name", "inputs"],
            },
        ),
        # ============ Model Registry ============
        Tool(
            name="list_registered_models",
            description="List all registered models in Unity Catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "catalog_name": {
                        "type": "string",
                        "description": "Filter by catalog name",
                    },
                    "schema_name": {
                        "type": "string",
                        "description": "Filter by schema name",
                    },
                },
            },
        ),
        Tool(
            name="get_registered_model",
            description="Get details of a registered model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Full model name (catalog.schema.model)",
                    }
                },
                "required": ["model_name"],
            },
        ),
        Tool(
            name="list_model_versions",
            description="List all versions of a registered model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Full model name (catalog.schema.model)",
                    }
                },
                "required": ["model_name"],
            },
        ),
        Tool(
            name="get_model_version",
            description="Get details of a specific model version",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "Full model name (catalog.schema.model)",
                    },
                    "version": {
                        "type": "integer",
                        "description": "The model version number",
                    },
                },
                "required": ["model_name", "version"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Databricks API operations based on tool name."""
    try:
        result = None

        # ============ Cluster Operations ============
        if name == "list_clusters":
            w = get_workspace_client()
            clusters = list(w.clusters.list())
            result = [
                {
                    "cluster_id": c.cluster_id,
                    "cluster_name": c.cluster_name,
                    "state": str(c.state),
                    "spark_version": c.spark_version,
                    "node_type_id": c.node_type_id,
                    "num_workers": c.num_workers,
                }
                for c in clusters
            ]

        elif name == "get_cluster":
            w = get_workspace_client()
            cluster = w.clusters.get(cluster_id=arguments["cluster_id"])
            result = cluster.as_dict()

        elif name == "create_cluster":
            w = get_workspace_client()
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

            cluster = w.clusters.create(**create_args).result()
            result = {"cluster_id": cluster.cluster_id, "status": "created"}

        elif name == "start_cluster":
            w = get_workspace_client()
            w.clusters.start(cluster_id=arguments["cluster_id"]).result()
            result = {"status": "started", "cluster_id": arguments["cluster_id"]}

        elif name == "terminate_cluster":
            w = get_workspace_client()
            w.clusters.delete(cluster_id=arguments["cluster_id"]).result()
            result = {"status": "terminated", "cluster_id": arguments["cluster_id"]}

        elif name == "delete_cluster":
            w = get_workspace_client()
            w.clusters.permanent_delete(cluster_id=arguments["cluster_id"])
            result = {"status": "deleted", "cluster_id": arguments["cluster_id"]}

        elif name == "get_clusters_batch":
            w = get_workspace_client()
            cluster_ids = arguments["cluster_ids"]

            # Execute get operations concurrently for efficiency
            def get_cluster(cluster_id):
                try:
                    cluster = w.clusters.get(cluster_id=cluster_id)
                    return {"cluster_id": cluster_id, "data": cluster.as_dict(), "status": "success"}
                except Exception as e:
                    return {"cluster_id": cluster_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_cluster, cid) for cid in cluster_ids]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(cluster_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_clusters_batch":
            w = get_workspace_client()
            cluster_ids = arguments["cluster_ids"]

            # Execute delete operations concurrently for efficiency
            def delete_cluster(cluster_id):
                try:
                    w.clusters.permanent_delete(cluster_id=cluster_id)
                    return {"cluster_id": cluster_id, "status": "success"}
                except Exception as e:
                    return {"cluster_id": cluster_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_cluster, cid) for cid in cluster_ids]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(cluster_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Jobs Operations ============
        elif name == "list_jobs":
            w = get_workspace_client()
            kwargs = {}
            if "limit" in arguments:
                kwargs["limit"] = arguments["limit"]
            if "name" in arguments:
                kwargs["name"] = arguments["name"]

            jobs = list(w.jobs.list(**kwargs))
            result = [
                {
                    "job_id": j.job_id,
                    "settings": {
                        "name": j.settings.name if j.settings else None,
                        "tasks": len(j.settings.tasks) if j.settings and j.settings.tasks else 0,
                    },
                }
                for j in jobs
            ]

        elif name == "get_job":
            w = get_workspace_client()
            job = w.jobs.get(job_id=arguments["job_id"])
            result = job.as_dict()

        elif name == "create_job":
            w = get_workspace_client()
            tasks = json.loads(arguments["tasks"])
            job_clusters = (
                json.loads(arguments["job_clusters"])
                if "job_clusters" in arguments
                else None
            )

            job = w.jobs.create(
                name=arguments["name"], tasks=tasks, job_clusters=job_clusters
            )
            result = {"job_id": job.job_id, "status": "created"}

        elif name == "run_job":
            w = get_workspace_client()
            kwargs = {"job_id": arguments["job_id"]}
            if "notebook_params" in arguments:
                kwargs["notebook_params"] = json.loads(arguments["notebook_params"])

            run = w.jobs.run_now(**kwargs).result()
            result = {"run_id": run.run_id, "status": "completed"}

        elif name == "get_run":
            w = get_workspace_client()
            run = w.jobs.get_run(run_id=arguments["run_id"])
            result = run.as_dict()

        elif name == "cancel_run":
            w = get_workspace_client()
            w.jobs.cancel_run(run_id=arguments["run_id"])
            result = {"status": "cancelled", "run_id": arguments["run_id"]}

        elif name == "delete_job":
            w = get_workspace_client()
            w.jobs.delete(job_id=arguments["job_id"])
            result = {"status": "deleted", "job_id": arguments["job_id"]}

        elif name == "get_jobs_batch":
            w = get_workspace_client()
            job_ids = arguments["job_ids"]

            # Execute get operations concurrently for efficiency
            def get_job(job_id):
                try:
                    job = w.jobs.get(job_id=job_id)
                    return {"job_id": job_id, "data": job.as_dict(), "status": "success"}
                except Exception as e:
                    return {"job_id": job_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_job, jid) for jid in job_ids]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(job_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_jobs_batch":
            w = get_workspace_client()
            job_ids = arguments["job_ids"]

            # Execute delete operations concurrently for efficiency
            def delete_job(job_id):
                try:
                    w.jobs.delete(job_id=job_id)
                    return {"job_id": job_id, "status": "success"}
                except Exception as e:
                    return {"job_id": job_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_job, jid) for jid in job_ids]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(job_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Workspace Operations ============
        elif name == "list_workspace_objects":
            w = get_workspace_client()
            path = arguments.get("path", "/")
            objects = list(w.workspace.list(path=path))
            result = [
                {"path": o.path, "object_type": str(o.object_type), "language": str(o.language)}
                for o in objects
            ]

        elif name == "get_workspace_object_status":
            w = get_workspace_client()
            obj = w.workspace.get_status(path=arguments["path"])
            result = obj.as_dict()

        elif name == "export_workspace_object":
            w = get_workspace_client()
            from databricks.sdk.service.workspace import ExportFormat

            format_map = {
                "SOURCE": ExportFormat.SOURCE,
                "HTML": ExportFormat.HTML,
                "JUPYTER": ExportFormat.JUPYTER,
                "DBC": ExportFormat.DBC,
            }
            export_format = format_map.get(arguments.get("format", "SOURCE"))

            export = w.workspace.export(path=arguments["path"], format=export_format)
            result = {"content": export.content, "format": arguments.get("format", "SOURCE")}

        elif name == "delete_workspace_object":
            w = get_workspace_client()
            kwargs = {"path": arguments["path"]}
            if "recursive" in arguments:
                kwargs["recursive"] = arguments["recursive"]
            w.workspace.delete(**kwargs)
            result = {"status": "deleted", "path": arguments["path"]}

        elif name == "mkdirs":
            w = get_workspace_client()
            w.workspace.mkdirs(path=arguments["path"])
            result = {"status": "created", "path": arguments["path"]}

        # ============ DBFS Operations ============
        elif name == "list_dbfs":
            w = get_workspace_client()
            files = list(w.dbfs.list(path=arguments["path"]))
            result = [
                {
                    "path": f.path,
                    "is_dir": f.is_dir,
                    "file_size": f.file_size,
                }
                for f in files
            ]

        elif name == "get_dbfs_status":
            w = get_workspace_client()
            status = w.dbfs.get_status(path=arguments["path"])
            result = status.as_dict()

        elif name == "delete_dbfs":
            w = get_workspace_client()
            kwargs = {"path": arguments["path"]}
            if "recursive" in arguments:
                kwargs["recursive"] = arguments["recursive"]
            w.dbfs.delete(**kwargs)
            result = {"status": "deleted", "path": arguments["path"]}

        # ============ Repos Operations ============
        elif name == "list_repos":
            w = get_workspace_client()
            repos = list(w.repos.list())
            result = [
                {
                    "id": r.id,
                    "url": r.url,
                    "provider": r.provider,
                    "path": r.path,
                    "branch": r.branch,
                }
                for r in repos
            ]

        elif name == "get_repo":
            w = get_workspace_client()
            repo = w.repos.get(repo_id=arguments["repo_id"])
            result = repo.as_dict()

        elif name == "create_repo":
            w = get_workspace_client()
            repo = w.repos.create(
                url=arguments["url"],
                provider=arguments["provider"],
                path=arguments.get("path"),
            )
            result = {"id": repo.id, "path": repo.path, "status": "created"}

        elif name == "update_repo":
            w = get_workspace_client()
            kwargs = {"repo_id": arguments["repo_id"]}
            if "branch" in arguments:
                kwargs["branch"] = arguments["branch"]
            if "tag" in arguments:
                kwargs["tag"] = arguments["tag"]
            repo = w.repos.update(**kwargs)
            result = repo.as_dict()

        elif name == "delete_repo":
            w = get_workspace_client()
            w.repos.delete(repo_id=arguments["repo_id"])
            result = {"status": "deleted", "repo_id": arguments["repo_id"]}

        # ============ SQL Warehouse Operations ============
        elif name == "list_warehouses":
            w = get_workspace_client()
            warehouses = list(w.warehouses.list())
            result = [
                {
                    "id": wh.id,
                    "name": wh.name,
                    "state": str(wh.state),
                    "cluster_size": wh.cluster_size,
                }
                for wh in warehouses
            ]

        elif name == "get_warehouse":
            w = get_workspace_client()
            warehouse = w.warehouses.get(id=arguments["warehouse_id"])
            result = warehouse.as_dict()

        elif name == "start_warehouse":
            w = get_workspace_client()
            w.warehouses.start(id=arguments["warehouse_id"])
            result = {"status": "starting", "warehouse_id": arguments["warehouse_id"]}

        elif name == "stop_warehouse":
            w = get_workspace_client()
            w.warehouses.stop(id=arguments["warehouse_id"])
            result = {"status": "stopping", "warehouse_id": arguments["warehouse_id"]}

        elif name == "get_warehouses_batch":
            w = get_workspace_client()
            warehouse_ids = arguments["warehouse_ids"]

            # Execute get operations concurrently for efficiency
            def get_warehouse(warehouse_id):
                try:
                    warehouse = w.warehouses.get(id=warehouse_id)
                    return {"warehouse_id": warehouse_id, "data": warehouse.as_dict(), "status": "success"}
                except Exception as e:
                    return {"warehouse_id": warehouse_id, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_warehouse, wid) for wid in warehouse_ids]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(warehouse_ids),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Unity Catalog - Catalogs ============
        elif name == "list_catalogs":
            w = get_workspace_client()
            catalogs = list(w.catalogs.list())
            result = [{"name": c.name, "comment": c.comment, "owner": c.owner} for c in catalogs]

        elif name == "get_catalog":
            w = get_workspace_client()
            catalog = w.catalogs.get(name=arguments["catalog_name"])
            result = catalog.as_dict()

        elif name == "create_catalog":
            w = get_workspace_client()
            catalog = w.catalogs.create(
                name=arguments["catalog_name"], comment=arguments.get("comment")
            )
            result = {"name": catalog.name, "status": "created"}

        elif name == "delete_catalog":
            w = get_workspace_client()
            w.catalogs.delete(
                name=arguments["catalog_name"], force=arguments.get("force", False)
            )
            result = {"status": "deleted", "catalog_name": arguments["catalog_name"]}

        # ============ Unity Catalog - Schemas ============
        elif name == "list_schemas":
            w = get_workspace_client()
            schemas = list(w.schemas.list(catalog_name=arguments["catalog_name"]))
            result = [
                {"name": s.name, "full_name": s.full_name, "comment": s.comment} for s in schemas
            ]

        elif name == "get_schema":
            w = get_workspace_client()
            schema = w.schemas.get(full_name=arguments["schema_full_name"])
            result = schema.as_dict()

        elif name == "create_schema":
            w = get_workspace_client()
            schema = w.schemas.create(
                name=arguments["schema_name"],
                catalog_name=arguments["catalog_name"],
                comment=arguments.get("comment"),
            )
            result = {"name": schema.name, "full_name": schema.full_name, "status": "created"}

        elif name == "delete_schema":
            w = get_workspace_client()
            w.schemas.delete(full_name=arguments["schema_full_name"])
            result = {"status": "deleted", "schema_full_name": arguments["schema_full_name"]}

        # ============ Unity Catalog - Tables ============
        elif name == "list_tables":
            w = get_workspace_client()
            tables = list(
                w.tables.list(
                    catalog_name=arguments["catalog_name"],
                    schema_name=arguments["schema_name"],
                )
            )
            result = [
                {
                    "name": t.name,
                    "full_name": t.full_name,
                    "table_type": str(t.table_type),
                    "data_source_format": str(t.data_source_format),
                }
                for t in tables
            ]

        elif name == "get_table":
            w = get_workspace_client()
            table = w.tables.get(full_name=arguments["table_full_name"])
            result = table.as_dict()

        elif name == "delete_table":
            w = get_workspace_client()
            w.tables.delete(full_name=arguments["table_full_name"])
            result = {"status": "deleted", "table_full_name": arguments["table_full_name"]}

        elif name == "delete_tables_batch":
            w = get_workspace_client()
            table_full_names = arguments["table_full_names"]

            # Execute delete operations concurrently for efficiency
            def delete_table(table_full_name):
                try:
                    w.tables.delete(full_name=table_full_name)
                    return {"table_full_name": table_full_name, "status": "success"}
                except Exception as e:
                    return {"table_full_name": table_full_name, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_table, tname) for tname in table_full_names]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "total": len(table_full_names),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Secrets Operations ============
        elif name == "list_secret_scopes":
            w = get_workspace_client()
            scopes = list(w.secrets.list_scopes())
            result = [{"name": s.name} for s in scopes]

        elif name == "create_secret_scope":
            w = get_workspace_client()
            w.secrets.create_scope(scope=arguments["scope"])
            result = {"status": "created", "scope": arguments["scope"]}

        elif name == "delete_secret_scope":
            w = get_workspace_client()
            w.secrets.delete_scope(scope=arguments["scope"])
            result = {"status": "deleted", "scope": arguments["scope"]}

        elif name == "list_secrets":
            w = get_workspace_client()
            secrets = list(w.secrets.list_secrets(scope=arguments["scope"]))
            result = [{"key": s.key} for s in secrets]

        elif name == "put_secret":
            w = get_workspace_client()
            w.secrets.put_secret(
                scope=arguments["scope"],
                key=arguments["key"],
                string_value=arguments["string_value"],
            )
            result = {
                "status": "created",
                "scope": arguments["scope"],
                "key": arguments["key"],
            }

        elif name == "delete_secret":
            w = get_workspace_client()
            w.secrets.delete_secret(scope=arguments["scope"], key=arguments["key"])
            result = {
                "status": "deleted",
                "scope": arguments["scope"],
                "key": arguments["key"],
            }

        elif name == "put_secrets_batch":
            w = get_workspace_client()
            scope = arguments["scope"]
            secrets = arguments["secrets"]

            # Execute put operations concurrently for efficiency
            def put_secret(secret_item):
                try:
                    w.secrets.put_secret(
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

            result = {
                "scope": scope,
                "total": len(secrets),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        elif name == "delete_secrets_batch":
            w = get_workspace_client()
            scope = arguments["scope"]
            keys = arguments["keys"]

            # Execute delete operations concurrently for efficiency
            def delete_secret(key):
                try:
                    w.secrets.delete_secret(scope=scope, key=key)
                    return {"key": key, "status": "success"}
                except Exception as e:
                    return {"key": key, "error": str(e), "status": "failed"}

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(delete_secret, key) for key in keys]
                results = [future.result() for future in as_completed(futures)]

            result = {
                "scope": scope,
                "total": len(keys),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Pipelines Operations ============
        elif name == "list_pipelines":
            w = get_workspace_client()
            pipelines = list(w.pipelines.list_pipelines())
            result = [
                {
                    "pipeline_id": p.pipeline_id,
                    "name": p.name,
                    "state": str(p.state),
                }
                for p in pipelines
            ]

        elif name == "get_pipeline":
            w = get_workspace_client()
            pipeline = w.pipelines.get(pipeline_id=arguments["pipeline_id"])
            result = pipeline.as_dict()

        elif name == "start_pipeline_update":
            w = get_workspace_client()
            update = w.pipelines.start_update(pipeline_id=arguments["pipeline_id"])
            result = {"update_id": update.update_id, "status": "started"}

        elif name == "stop_pipeline":
            w = get_workspace_client()
            w.pipelines.stop(pipeline_id=arguments["pipeline_id"])
            result = {"status": "stopped", "pipeline_id": arguments["pipeline_id"]}

        # ============ Account Operations ============
        elif name == "list_account_workspaces":
            a = get_account_client()
            workspaces = list(a.workspaces.list())
            result = [
                {
                    "workspace_id": ws.workspace_id,
                    "workspace_name": ws.workspace_name,
                    "workspace_status": str(ws.workspace_status),
                    "deployment_name": ws.deployment_name,
                }
                for ws in workspaces
            ]

        elif name == "get_account_workspace":
            a = get_account_client()
            workspace = a.workspaces.get(workspace_id=arguments["workspace_id"])
            result = workspace.as_dict()

        elif name == "list_account_users":
            a = get_account_client()
            users = list(a.users.list())
            result = [
                {
                    "id": u.id,
                    "user_name": u.user_name,
                    "display_name": u.display_name,
                    "active": u.active,
                }
                for u in users
            ]

        elif name == "get_account_user":
            a = get_account_client()
            user = a.users.get(id=arguments["user_id"])
            result = user.as_dict()

        elif name == "list_account_groups":
            a = get_account_client()
            groups = list(a.groups.list())
            result = [{"id": g.id, "display_name": g.display_name} for g in groups]

        elif name == "get_account_group":
            a = get_account_client()
            group = a.groups.get(id=arguments["group_id"])
            result = group.as_dict()

        elif name == "list_account_service_principals":
            a = get_account_client()
            sps = list(a.service_principals.list())
            result = [
                {
                    "id": sp.id,
                    "application_id": sp.application_id,
                    "display_name": sp.display_name,
                    "active": sp.active,
                }
                for sp in sps
            ]

        elif name == "list_account_metastores":
            a = get_account_client()
            metastores = list(a.metastores.list())
            result = [
                {
                    "metastore_id": m.metastore_id,
                    "name": m.name,
                    "region": m.region,
                }
                for m in metastores
            ]

        elif name == "get_account_metastore":
            a = get_account_client()
            metastore = a.metastores.get(id=arguments["metastore_id"])
            result = metastore.as_dict()

        # ============ SQL Statement Execution ============
        elif name == "execute_statement":
            w = get_workspace_client()
            from databricks.sdk.service.sql import ExecuteStatementRequestParams

            params = ExecuteStatementRequestParams(
                statement=arguments["statement"],
                warehouse_id=arguments["warehouse_id"],
                catalog=arguments.get("catalog"),
                schema=arguments.get("schema"),
                wait_timeout=arguments.get("wait_timeout", "10s"),
            )

            if "row_limit" in arguments:
                params.row_limit = arguments["row_limit"]

            response = w.statement_execution.execute_statement(**params.as_dict())

            # Format response
            result = {
                "statement_id": response.statement_id,
                "status": str(response.status.state) if response.status else None,
            }

            # Include result data if available
            if response.result:
                result["result"] = {
                    "row_count": response.result.row_count,
                    "data_array": response.result.data_array[:100] if response.result.data_array else None,  # Limit to first 100 rows
                    "truncated": response.result.truncated,
                }
                if response.manifest:
                    result["manifest"] = {
                        "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                        "total_row_count": response.manifest.total_row_count,
                        "total_chunk_count": response.manifest.total_chunk_count,
                    }

        elif name == "get_statement":
            w = get_workspace_client()
            response = w.statement_execution.get_statement(statement_id=arguments["statement_id"])

            result = {
                "statement_id": response.statement_id,
                "status": str(response.status.state) if response.status else None,
            }

            if response.result:
                result["result"] = {
                    "row_count": response.result.row_count,
                    "data_array": response.result.data_array[:100] if response.result.data_array else None,
                    "truncated": response.result.truncated,
                }
                if response.manifest:
                    result["manifest"] = {
                        "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                        "total_row_count": response.manifest.total_row_count,
                    }

        elif name == "cancel_statement_execution":
            w = get_workspace_client()
            w.statement_execution.cancel_execution(statement_id=arguments["statement_id"])
            result = {"status": "cancelled", "statement_id": arguments["statement_id"]}

        elif name == "execute_statements_batch":
            w = get_workspace_client()
            from databricks.sdk.service.sql import ExecuteStatementRequestParams

            warehouse_id = arguments["warehouse_id"]
            statements = arguments["statements"]
            catalog = arguments.get("catalog")
            schema = arguments.get("schema")
            wait_timeout = arguments.get("wait_timeout", "10s")
            row_limit = arguments.get("row_limit")

            # Execute statements sequentially (they may have dependencies)
            results = []
            for idx, statement in enumerate(statements):
                try:
                    params = ExecuteStatementRequestParams(
                        statement=statement,
                        warehouse_id=warehouse_id,
                        catalog=catalog,
                        schema=schema,
                        wait_timeout=wait_timeout,
                    )

                    if row_limit:
                        params.row_limit = row_limit

                    response = w.statement_execution.execute_statement(**params.as_dict())

                    # Format response
                    statement_result = {
                        "statement_index": idx,
                        "statement": statement,
                        "statement_id": response.statement_id,
                        "status": str(response.status.state) if response.status else None,
                    }

                    # Include result data if available
                    if response.result:
                        statement_result["result"] = {
                            "row_count": response.result.row_count,
                            "data_array": response.result.data_array[:100] if response.result.data_array else None,
                            "truncated": response.result.truncated,
                        }
                        if response.manifest:
                            statement_result["manifest"] = {
                                "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                                "total_row_count": response.manifest.total_row_count,
                            }

                    results.append({"status": "success", **statement_result})

                except Exception as e:
                    results.append({
                        "statement_index": idx,
                        "statement": statement,
                        "status": "failed",
                        "error": str(e)
                    })
                    # Continue executing remaining statements even if one fails

            result = {
                "warehouse_id": warehouse_id,
                "total": len(statements),
                "successful": len([r for r in results if r["status"] == "success"]),
                "failed": len([r for r in results if r["status"] == "failed"]),
                "results": results
            }

        # ============ Genie Operations ============
        elif name == "start_genie_conversation":
            w = get_workspace_client()
            conversation = w.genie.start_conversation(space_id=arguments["space_id"])
            result = {
                "conversation_id": conversation.conversation_id,
                "space_id": arguments["space_id"],
            }

        elif name == "create_genie_message":
            w = get_workspace_client()
            from databricks.sdk.service.dashboards import MessageContent

            message = w.genie.create_message(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                content=MessageContent(query=arguments["content"]),
            )

            result = {
                "message_id": message.id,
                "conversation_id": arguments["conversation_id"],
                "status": str(message.status),
            }

            # Include attachments if available
            if message.attachments:
                result["attachments"] = [
                    {
                        "id": att.id,
                        "type": str(att.type) if hasattr(att, 'type') else None,
                    }
                    for att in message.attachments
                ]

        elif name == "get_genie_message":
            w = get_workspace_client()
            message = w.genie.get_message(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                message_id=arguments["message_id"],
            )
            result = message.as_dict()

        elif name == "get_genie_message_query_result":
            w = get_workspace_client()
            query_result = w.genie.get_message_query_result(
                space_id=arguments["space_id"],
                conversation_id=arguments["conversation_id"],
                message_id=arguments["message_id"],
                attachment_id=arguments["attachment_id"],
            )
            result = query_result.as_dict()

        # ============ Vector Search Operations ============
        elif name == "list_vector_search_endpoints":
            w = get_workspace_client()
            endpoints = list(w.vector_search_endpoints.list_endpoints())
            result = [
                {
                    "name": e.name,
                    "endpoint_type": str(e.endpoint_type) if e.endpoint_type else None,
                    "endpoint_status": str(e.endpoint_status.state) if e.endpoint_status else None,
                }
                for e in endpoints
            ]

        elif name == "get_vector_search_endpoint":
            w = get_workspace_client()
            endpoint = w.vector_search_endpoints.get_endpoint(
                endpoint_name=arguments["endpoint_name"]
            )
            result = endpoint.as_dict()

        elif name == "list_vector_search_indexes":
            w = get_workspace_client()
            indexes = list(
                w.vector_search_indexes.list_indexes(
                    endpoint_name=arguments["endpoint_name"]
                )
            )
            result = [
                {
                    "name": idx.name,
                    "index_type": str(idx.index_type) if idx.index_type else None,
                    "delta_sync_index_spec": str(idx.delta_sync_index_spec) if idx.delta_sync_index_spec else None,
                }
                for idx in indexes
            ]

        elif name == "get_vector_search_index":
            w = get_workspace_client()
            index = w.vector_search_indexes.get_index(index_name=arguments["index_name"])
            result = index.as_dict()

        # ============ Serving Endpoints Operations ============
        elif name == "list_serving_endpoints":
            w = get_workspace_client()
            endpoints = list(w.serving_endpoints.list())
            result = [
                {
                    "name": e.name,
                    "state": str(e.state.ready) if e.state else None,
                    "config": {
                        "served_models": [
                            {
                                "name": m.name,
                                "model_name": m.model_name,
                                "model_version": m.model_version,
                                "workload_size": str(m.workload_size) if m.workload_size else None,
                            }
                            for m in (e.config.served_models or [])
                        ] if e.config else None,
                    },
                }
                for e in endpoints
            ]

        elif name == "get_serving_endpoint":
            w = get_workspace_client()
            endpoint = w.serving_endpoints.get(name=arguments["endpoint_name"])
            result = endpoint.as_dict()

        elif name == "query_serving_endpoint":
            w = get_workspace_client()
            inputs = json.loads(arguments["inputs"])
            response = w.serving_endpoints.query(
                name=arguments["endpoint_name"],
                inputs=inputs,
            )
            result = response.as_dict()

        # ============ Model Registry Operations ============
        elif name == "list_registered_models":
            w = get_workspace_client()
            kwargs = {}
            if "catalog_name" in arguments:
                kwargs["catalog_name"] = arguments["catalog_name"]
            if "schema_name" in arguments:
                kwargs["schema_name"] = arguments["schema_name"]

            models = list(w.registered_models.list(**kwargs))
            result = [
                {
                    "name": m.name,
                    "full_name": m.full_name,
                    "catalog_name": m.catalog_name,
                    "schema_name": m.schema_name,
                }
                for m in models
            ]

        elif name == "get_registered_model":
            w = get_workspace_client()
            model = w.registered_models.get(full_name=arguments["model_name"])
            result = model.as_dict()

        elif name == "list_model_versions":
            w = get_workspace_client()
            versions = list(w.model_versions.list(full_name=arguments["model_name"]))
            result = [
                {
                    "version": v.version,
                    "model_name": v.model_name,
                    "status": str(v.status) if v.status else None,
                    "run_id": v.run_id,
                }
                for v in versions
            ]

        elif name == "get_model_version":
            w = get_workspace_client()
            version = w.model_versions.get(
                full_name=arguments["model_name"],
                version=arguments["version"],
            )
            result = version.as_dict()

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Format and return result
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        logger.error(f"Error executing {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def main():
    """Run the MCP server."""
    import asyncio
    from mcp.server.stdio import stdio_server

    async def aio_main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )

    asyncio.run(aio_main())


if __name__ == "__main__":
    main()

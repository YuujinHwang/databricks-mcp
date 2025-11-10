# API Reference

This document provides a comprehensive reference for all MCP tools available in the Databricks MCP Server.

## Overview

The Databricks MCP Server exposes **82 tools** across **16 categories**, providing complete access to Databricks workspace and account-level operations.

## Tool Categories

- [Clusters](#clusters) (8 tools)
- [Jobs](#jobs) (8 tools)
- [Workspace](#workspace) (5 tools)
- [DBFS](#dbfs) (3 tools)
- [Repos](#repos) (5 tools)
- [SQL Warehouses](#sql-warehouses) (5 tools)
- [Unity Catalog](#unity-catalog) (12 tools)
- [Secrets](#secrets) (8 tools)
- [Pipelines](#pipelines) (4 tools)
- [Account Management](#account-management) (9 tools)
- [SQL Execution](#sql-execution) (4 tools)
- [Genie (AI/BI)](#genie-aibi) (4 tools)
- [Vector Search](#vector-search) (4 tools)
- [Model Serving](#model-serving) (3 tools)
- [Model Registry](#model-registry) (4 tools)
- [Feature Store](#feature-store) (6 tools)

---

## Clusters

Manage Databricks compute clusters.

### list_clusters

List all clusters in the workspace.

**Parameters:**
- `page_size` (integer, optional): Number of clusters per page (default: 100, max: 1000)

**Returns:**
- Array of cluster objects with ID, name, state, and configuration

**Example:**
```json
{
  "page_size": 50
}
```

### get_cluster

Get detailed information about a specific cluster.

**Parameters:**
- `cluster_id` (string, required): The unique identifier of the cluster

**Returns:**
- Cluster object with complete configuration and status

### create_cluster

Create a new compute cluster.

**Parameters:**
- `cluster_name` (string, required): Name for the cluster
- `spark_version` (string, required): Databricks runtime version (e.g., "13.3.x-scala2.12")
- `node_type_id` (string, required): Node type (e.g., "i3.xlarge")
- `num_workers` (integer, optional): Fixed number of workers
- `autoscale` (object, optional): Autoscaling configuration
  - `min_workers` (integer): Minimum workers
  - `max_workers` (integer): Maximum workers
- `autotermination_minutes` (integer, optional): Minutes before auto-termination (default: 30)
- `spark_conf` (object, optional): Spark configuration key-value pairs
- `custom_tags` (object, optional): Custom tags for the cluster

**Returns:**
- Cluster ID of the newly created cluster

**Example:**
```json
{
  "cluster_name": "my-cluster",
  "spark_version": "13.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "autotermination_minutes": 30
}
```

### start_cluster

Start a terminated cluster.

**Parameters:**
- `cluster_id` (string, required): The cluster ID to start

**Returns:**
- Success message

### terminate_cluster

Terminate a running cluster.

**Parameters:**
- `cluster_id` (string, required): The cluster ID to terminate

**Returns:**
- Success message

### delete_cluster

Permanently delete a cluster.

**Parameters:**
- `cluster_id` (string, required): The cluster ID to delete

**Returns:**
- Success message

### get_clusters_batch

Get multiple clusters in parallel (batch operation).

**Parameters:**
- `cluster_ids` (array of strings, required): List of cluster IDs to retrieve

**Returns:**
- Array of cluster objects

**Example:**
```json
{
  "cluster_ids": ["1234-567890-abc123", "1234-567890-def456"]
}
```

### delete_clusters_batch

Delete multiple clusters in parallel (batch operation).

**Parameters:**
- `cluster_ids` (array of strings, required): List of cluster IDs to delete

**Returns:**
- Summary of deletion results

---

## Jobs

Manage Databricks jobs and job runs.

### list_jobs

List all jobs in the workspace.

**Parameters:**
- `page_size` (integer, optional): Number of jobs per page (default: 100, max: 1000)
- `name` (string, optional): Filter by job name

**Returns:**
- Array of job objects

### get_job

Get detailed information about a specific job.

**Parameters:**
- `job_id` (integer, required): The job ID

**Returns:**
- Job object with complete configuration

### create_job

Create a new job.

**Parameters:**
- `name` (string, required): Job name
- `tasks` (array, required): Array of task definitions
- `job_clusters` (array, optional): Cluster configurations for the job
- `schedule` (object, optional): Scheduling configuration
  - `quartz_cron_expression` (string): Cron expression
  - `timezone_id` (string): Timezone (e.g., "America/Los_Angeles")
- `max_concurrent_runs` (integer, optional): Maximum concurrent runs
- `timeout_seconds` (integer, optional): Job timeout
- `email_notifications` (object, optional): Email notification settings

**Returns:**
- Job ID of the newly created job

**Example:**
```json
{
  "name": "Daily ETL Job",
  "tasks": [{
    "task_key": "etl_task",
    "notebook_task": {
      "notebook_path": "/Workspace/ETL/process_data"
    },
    "existing_cluster_id": "1234-567890-abc123"
  }],
  "schedule": {
    "quartz_cron_expression": "0 0 * * * ?",
    "timezone_id": "UTC"
  }
}
```

### run_job

Trigger a job run.

**Parameters:**
- `job_id` (integer, required): The job ID to run
- `notebook_params` (object, optional): Parameters to pass to notebook tasks
- `python_params` (array, optional): Parameters for Python tasks
- `jar_params` (array, optional): Parameters for JAR tasks

**Returns:**
- Run ID of the triggered run

### get_run

Get details about a specific job run.

**Parameters:**
- `run_id` (integer, required): The run ID

**Returns:**
- Run object with status, tasks, and execution details

### cancel_run

Cancel a running job.

**Parameters:**
- `run_id` (integer, required): The run ID to cancel

**Returns:**
- Success message

### delete_job

Delete a job.

**Parameters:**
- `job_id` (integer, required): The job ID to delete

**Returns:**
- Success message

### get_jobs_batch

Get multiple jobs in parallel (batch operation).

**Parameters:**
- `job_ids` (array of integers, required): List of job IDs

**Returns:**
- Array of job objects

### delete_jobs_batch

Delete multiple jobs in parallel (batch operation).

**Parameters:**
- `job_ids` (array of integers, required): List of job IDs to delete

**Returns:**
- Summary of deletion results

---

## Workspace

Manage workspace objects (notebooks, directories, files).

### list_workspace_objects

List objects in a workspace directory.

**Parameters:**
- `path` (string, required): Workspace path (e.g., "/Users/user@example.com")
- `page_size` (integer, optional): Number of objects per page

**Returns:**
- Array of workspace objects with path, type, and metadata

### get_workspace_object_status

Get metadata for a workspace object.

**Parameters:**
- `path` (string, required): Workspace object path

**Returns:**
- Object metadata including type, size, and modification time

### export_workspace_object

Export a notebook or file.

**Parameters:**
- `path` (string, required): Path to the object
- `format` (string, optional): Export format: SOURCE, HTML, JUPYTER, DBC (default: SOURCE)

**Returns:**
- Exported content (base64 encoded for binary formats)

**Example:**
```json
{
  "path": "/Users/user@example.com/my_notebook",
  "format": "JUPYTER"
}
```

### delete_workspace_object

Delete a workspace object.

**Parameters:**
- `path` (string, required): Path to delete
- `recursive` (boolean, optional): Recursively delete directories (default: false)

**Returns:**
- Success message

### mkdirs

Create a directory in the workspace.

**Parameters:**
- `path` (string, required): Directory path to create

**Returns:**
- Success message

---

## DBFS

Manage Databricks File System (DBFS) files and directories.

### list_dbfs

List files in a DBFS directory.

**Parameters:**
- `path` (string, required): DBFS path (e.g., "/FileStore/data")

**Returns:**
- Array of file objects with path, size, and modification time

### get_dbfs_status

Get status of a DBFS file or directory.

**Parameters:**
- `path` (string, required): DBFS path

**Returns:**
- File/directory metadata

### delete_dbfs

Delete a DBFS file or directory.

**Parameters:**
- `path` (string, required): DBFS path to delete
- `recursive` (boolean, optional): Recursively delete directories (default: false)

**Returns:**
- Success message

---

## Repos

Manage Git repositories in the workspace.

### list_repos

List all Git repositories.

**Parameters:**
- `page_size` (integer, optional): Number of repos per page

**Returns:**
- Array of repository objects

### get_repo

Get details about a specific repository.

**Parameters:**
- `repo_id` (string, required): Repository ID

**Returns:**
- Repository object with URL, branch, and status

### create_repo

Create a new Git repository.

**Parameters:**
- `url` (string, required): Git repository URL (GitHub, GitLab, Bitbucket)
- `provider` (string, required): Git provider (e.g., "github", "gitlab", "bitbucket")
- `path` (string, optional): Workspace path for the repo

**Returns:**
- Repository ID

**Example:**
```json
{
  "url": "https://github.com/user/repo",
  "provider": "github",
  "path": "/Repos/user@example.com/repo"
}
```

### update_repo

Update repository branch or tag.

**Parameters:**
- `repo_id` (string, required): Repository ID
- `branch` (string, optional): Branch name
- `tag` (string, optional): Tag name

**Returns:**
- Success message

### delete_repo

Delete a repository.

**Parameters:**
- `repo_id` (string, required): Repository ID to delete

**Returns:**
- Success message

---

## SQL Warehouses

Manage SQL warehouses (formerly SQL endpoints).

### list_warehouses

List all SQL warehouses.

**Parameters:**
- None

**Returns:**
- Array of warehouse objects

### get_warehouse

Get details about a specific warehouse.

**Parameters:**
- `warehouse_id` (string, required): Warehouse ID

**Returns:**
- Warehouse configuration and status

### start_warehouse

Start a stopped SQL warehouse.

**Parameters:**
- `warehouse_id` (string, required): Warehouse ID to start

**Returns:**
- Success message

### stop_warehouse

Stop a running SQL warehouse.

**Parameters:**
- `warehouse_id` (string, required): Warehouse ID to stop

**Returns:**
- Success message

### get_warehouses_batch

Get multiple warehouses in parallel (batch operation).

**Parameters:**
- `warehouse_ids` (array of strings, required): List of warehouse IDs

**Returns:**
- Array of warehouse objects

---

## Unity Catalog

Manage Unity Catalog objects (catalogs, schemas, tables).

### Catalogs

#### list_catalogs

List all catalogs.

**Parameters:**
- None

**Returns:**
- Array of catalog objects

#### get_catalog

Get details about a specific catalog.

**Parameters:**
- `catalog_name` (string, required): Catalog name

**Returns:**
- Catalog metadata

#### create_catalog

Create a new catalog.

**Parameters:**
- `catalog_name` (string, required): Catalog name
- `comment` (string, optional): Catalog description

**Returns:**
- Catalog object

**Example:**
```json
{
  "catalog_name": "my_catalog",
  "comment": "Production data catalog"
}
```

#### delete_catalog

Delete a catalog.

**Parameters:**
- `catalog_name` (string, required): Catalog name to delete
- `force` (boolean, optional): Force delete even if not empty (default: false)

**Returns:**
- Success message

### Schemas

#### list_schemas

List all schemas in a catalog.

**Parameters:**
- `catalog_name` (string, required): Catalog name

**Returns:**
- Array of schema objects

#### get_schema

Get details about a specific schema.

**Parameters:**
- `full_name` (string, required): Schema full name (catalog.schema)

**Returns:**
- Schema metadata

#### create_schema

Create a new schema.

**Parameters:**
- `catalog_name` (string, required): Parent catalog name
- `schema_name` (string, required): Schema name
- `comment` (string, optional): Schema description

**Returns:**
- Schema object

**Example:**
```json
{
  "catalog_name": "my_catalog",
  "schema_name": "my_schema",
  "comment": "Analytics schema"
}
```

#### delete_schema

Delete a schema.

**Parameters:**
- `full_name` (string, required): Schema full name (catalog.schema)

**Returns:**
- Success message

### Tables

#### list_tables

List all tables in a schema.

**Parameters:**
- `catalog_name` (string, required): Catalog name
- `schema_name` (string, required): Schema name

**Returns:**
- Array of table objects

#### get_table

Get details about a specific table.

**Parameters:**
- `full_name` (string, required): Table full name (catalog.schema.table)

**Returns:**
- Table metadata with column information

#### delete_table

Delete a table.

**Parameters:**
- `full_name` (string, required): Table full name (catalog.schema.table)

**Returns:**
- Success message

#### delete_tables_batch

Delete multiple tables in parallel (batch operation).

**Parameters:**
- `table_names` (array of strings, required): List of table full names

**Returns:**
- Summary of deletion results

---

## Secrets

Manage Databricks secrets.

### list_secret_scopes

List all secret scopes.

**Parameters:**
- None

**Returns:**
- Array of secret scope objects

### create_secret_scope

Create a new secret scope.

**Parameters:**
- `scope_name` (string, required): Name for the scope

**Returns:**
- Success message

### delete_secret_scope

Delete a secret scope.

**Parameters:**
- `scope_name` (string, required): Scope name to delete

**Returns:**
- Success message

### list_secrets

List all secrets in a scope (keys only, values are not returned).

**Parameters:**
- `scope_name` (string, required): Scope name

**Returns:**
- Array of secret keys

### put_secret

Create or update a secret.

**Parameters:**
- `scope_name` (string, required): Scope name
- `key` (string, required): Secret key
- `string_value` (string, required): Secret value

**Returns:**
- Success message

**Example:**
```json
{
  "scope_name": "my_scope",
  "key": "api_key",
  "string_value": "secret_value_here"
}
```

### delete_secret

Delete a secret.

**Parameters:**
- `scope_name` (string, required): Scope name
- `key` (string, required): Secret key to delete

**Returns:**
- Success message

### put_secrets_batch

Create or update multiple secrets in parallel (batch operation).

**Parameters:**
- `secrets` (array, required): Array of secret objects
  - `scope_name` (string): Scope name
  - `key` (string): Secret key
  - `string_value` (string): Secret value

**Returns:**
- Summary of put results

### delete_secrets_batch

Delete multiple secrets in parallel (batch operation).

**Parameters:**
- `secrets` (array, required): Array of objects with scope_name and key

**Returns:**
- Summary of deletion results

---

## Pipelines

Manage Delta Live Tables (DLT) pipelines.

### list_pipelines

List all DLT pipelines.

**Parameters:**
- `page_size` (integer, optional): Number of pipelines per page

**Returns:**
- Array of pipeline objects

### get_pipeline

Get details about a specific pipeline.

**Parameters:**
- `pipeline_id` (string, required): Pipeline ID

**Returns:**
- Pipeline configuration and status

### start_pipeline_update

Start a pipeline update (run the pipeline).

**Parameters:**
- `pipeline_id` (string, required): Pipeline ID
- `full_refresh` (boolean, optional): Perform full refresh (default: false)

**Returns:**
- Update ID

### stop_pipeline

Stop a running pipeline.

**Parameters:**
- `pipeline_id` (string, required): Pipeline ID to stop

**Returns:**
- Success message

---

## Account Management

Manage account-level resources (requires account admin permissions).

### list_account_workspaces

List all workspaces in the account.

**Parameters:**
- None

**Returns:**
- Array of workspace objects with IDs and URLs

### get_account_workspace

Get details about a specific workspace.

**Parameters:**
- `workspace_id` (string, required): Workspace ID

**Returns:**
- Workspace configuration

### list_account_users

List all users in the account.

**Parameters:**
- None

**Returns:**
- Array of user objects

### get_account_user

Get details about a specific user.

**Parameters:**
- `user_id` (string, required): User ID

**Returns:**
- User information

### list_account_groups

List all groups in the account.

**Parameters:**
- None

**Returns:**
- Array of group objects

### get_account_group

Get details about a specific group.

**Parameters:**
- `group_id` (string, required): Group ID

**Returns:**
- Group information and members

### list_account_service_principals

List all service principals in the account.

**Parameters:**
- None

**Returns:**
- Array of service principal objects

### list_account_metastores

List all Unity Catalog metastores in the account.

**Parameters:**
- None

**Returns:**
- Array of metastore objects

### get_account_metastore

Get details about a specific metastore.

**Parameters:**
- `metastore_id` (string, required): Metastore ID

**Returns:**
- Metastore configuration

---

## SQL Execution

Execute SQL statements on SQL warehouses.

### execute_statement

Execute a SQL statement.

**Parameters:**
- `warehouse_id` (string, required): SQL warehouse ID
- `statement` (string, required): SQL statement to execute
- `catalog` (string, optional): Default catalog
- `schema` (string, optional): Default schema
- `parameters` (array, optional): Query parameters for parameterized queries

**Returns:**
- Statement execution result with data (supports chunked results for large datasets)

**Example:**
```json
{
  "warehouse_id": "abc123def456",
  "statement": "SELECT * FROM my_catalog.my_schema.my_table LIMIT 100",
  "catalog": "my_catalog",
  "schema": "my_schema"
}
```

### get_statement

Get status and results of a previously executed statement.

**Parameters:**
- `statement_id` (string, required): Statement ID from execute_statement

**Returns:**
- Statement status and result data

### cancel_statement_execution

Cancel a running SQL statement.

**Parameters:**
- `statement_id` (string, required): Statement ID to cancel

**Returns:**
- Success message

### execute_statements_batch

Execute multiple SQL statements sequentially (batch operation).

**Parameters:**
- `warehouse_id` (string, required): SQL warehouse ID
- `statements` (array of strings, required): Array of SQL statements
- `catalog` (string, optional): Default catalog
- `schema` (string, optional): Default schema

**Returns:**
- Array of execution results

**Note:** Statements are executed sequentially, not in parallel.

---

## Genie (AI/BI)

Interact with Databricks Genie AI for natural language SQL queries.

### start_genie_conversation

Start a new conversation in a Genie space.

**Parameters:**
- `space_id` (string, required): Genie space ID

**Returns:**
- Conversation ID

### create_genie_message

Send a message or question to Genie.

**Parameters:**
- `space_id` (string, required): Genie space ID
- `conversation_id` (string, required): Conversation ID
- `content` (string, required): Your question or message

**Returns:**
- Message ID

**Example:**
```json
{
  "space_id": "01ef1234567890ab",
  "conversation_id": "01ef1234567890cd",
  "content": "Show me the top 10 customers by revenue this quarter"
}
```

### get_genie_message

Get details about a specific message.

**Parameters:**
- `space_id` (string, required): Genie space ID
- `conversation_id` (string, required): Conversation ID
- `message_id` (string, required): Message ID

**Returns:**
- Message details including SQL query generated by Genie

### get_genie_message_query_result

Get the SQL query result from a Genie response.

**Parameters:**
- `space_id` (string, required): Genie space ID
- `conversation_id` (string, required): Conversation ID
- `message_id` (string, required): Message ID

**Returns:**
- Query result data

---

## Vector Search

Manage vector search endpoints and indexes.

### list_vector_search_endpoints

List all vector search endpoints.

**Parameters:**
- None

**Returns:**
- Array of endpoint objects

### get_vector_search_endpoint

Get details about a specific endpoint.

**Parameters:**
- `endpoint_name` (string, required): Endpoint name

**Returns:**
- Endpoint configuration and status

### list_vector_search_indexes

List all indexes for an endpoint.

**Parameters:**
- `endpoint_name` (string, required): Endpoint name

**Returns:**
- Array of index objects

### get_vector_search_index

Get details about a specific index.

**Parameters:**
- `index_name` (string, required): Index name

**Returns:**
- Index configuration

---

## Model Serving

Manage and query model serving endpoints.

### list_serving_endpoints

List all model serving endpoints.

**Parameters:**
- None

**Returns:**
- Array of serving endpoint objects

### get_serving_endpoint

Get details about a specific serving endpoint.

**Parameters:**
- `endpoint_name` (string, required): Endpoint name

**Returns:**
- Endpoint configuration and status

### query_serving_endpoint

Query a serving endpoint with input data.

**Parameters:**
- `endpoint_name` (string, required): Endpoint name
- `inputs` (object or array, required): Input data for the model
- `params` (object, optional): Additional parameters

**Returns:**
- Model predictions

**Example:**
```json
{
  "endpoint_name": "my-model-endpoint",
  "inputs": {
    "data": [[1.0, 2.0, 3.0, 4.0]]
  }
}
```

---

## Model Registry

Manage Unity Catalog registered models.

### list_registered_models

List all registered models.

**Parameters:**
- `catalog_name` (string, optional): Filter by catalog
- `schema_name` (string, optional): Filter by schema

**Returns:**
- Array of registered model objects

### get_registered_model

Get details about a specific model.

**Parameters:**
- `full_name` (string, required): Model full name (catalog.schema.model)

**Returns:**
- Model metadata

### list_model_versions

List all versions of a model.

**Parameters:**
- `full_name` (string, required): Model full name (catalog.schema.model)

**Returns:**
- Array of model version objects

### get_model_version

Get details about a specific model version.

**Parameters:**
- `full_name` (string, required): Model full name (catalog.schema.model)
- `version` (integer, required): Version number

**Returns:**
- Model version metadata

---

## Feature Store

Manage Feature Store tables and online stores.

### create_feature_table

Create a feature table in Unity Catalog.

**Parameters:**
- `name` (string, required): Table full name (catalog.schema.table)
- `primary_keys` (array of strings, required): Primary key column names
- `timestamp_keys` (array of strings, optional): Timestamp column names
- `description` (string, optional): Table description

**Returns:**
- Feature table metadata

**Example:**
```json
{
  "name": "my_catalog.my_schema.user_features",
  "primary_keys": ["user_id"],
  "timestamp_keys": ["timestamp"],
  "description": "User feature table"
}
```

### get_feature_table

Get feature table metadata.

**Parameters:**
- `name` (string, required): Table full name

**Returns:**
- Feature table metadata

### delete_feature_table

Delete a feature table.

**Parameters:**
- `name` (string, required): Table full name to delete

**Returns:**
- Success message

### list_feature_tables

List all feature tables in a schema.

**Parameters:**
- `catalog_name` (string, required): Catalog name
- `schema_name` (string, required): Schema name

**Returns:**
- Array of feature table objects

### create_online_store

Create an online store for real-time feature serving.

**Parameters:**
- `name` (string, required): Online store name
- `spec` (object, required): Online store specification

**Returns:**
- Online store metadata

### publish_feature_table

Publish a feature table to an online store.

**Parameters:**
- `table_name` (string, required): Feature table full name
- `online_store_name` (string, required): Target online store

**Returns:**
- Success message

---

## Common Parameters

Many tools support these common parameters:

- `page_size`: Controls pagination size (default: 100, max: 1000)
- `recursive`: For deletion operations, recursively delete contents
- `force`: Force operations even if checks would normally prevent them

## Batch Operations

The following batch operations are available for improved performance:

**Parallel Execution:**
- Clusters: get_clusters_batch, delete_clusters_batch
- Jobs: get_jobs_batch, delete_jobs_batch
- Warehouses: get_warehouses_batch
- Unity Catalog: delete_tables_batch
- Secrets: put_secrets_batch, delete_secrets_batch

**Sequential Execution:**
- SQL: execute_statements_batch (executes in order)

Batch operations use ThreadPoolExecutor with 10 max workers for parallel operations.

---

## Error Handling

All tools implement comprehensive error handling with automatic retry logic for transient errors. See [Error Handling](error-handling.md) for details.

## Rate Limiting

The server automatically handles rate limiting (429 errors) with exponential backoff. No action required from the client.

# Examples

This document provides practical examples of using the Databricks MCP Server for common tasks.

## Table of Contents

- [Getting Started](#getting-started)
- [Cluster Management](#cluster-management)
- [Job Management](#job-management)
- [SQL Operations](#sql-operations)
- [Workspace Management](#workspace-management)
- [Unity Catalog](#unity-catalog)
- [Secrets Management](#secrets-management)
- [AI/BI with Genie](#aibi-with-genie)
- [Batch Operations](#batch-operations)
- [Account Management](#account-management)

---

## Getting Started

### List Available Resources

Get an overview of your Databricks workspace:

```json
{
  "tool": "list_clusters",
  "arguments": {}
}
```

```json
{
  "tool": "list_jobs",
  "arguments": {}
}
```

```json
{
  "tool": "list_warehouses",
  "arguments": {}
}
```

---

## Cluster Management

### Create an Auto-Scaling Cluster

Create a cluster that automatically scales based on workload:

```json
{
  "tool": "create_cluster",
  "arguments": {
    "cluster_name": "auto-scaling-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "autoscale": {
      "min_workers": 2,
      "max_workers": 8
    },
    "autotermination_minutes": 30,
    "custom_tags": {
      "project": "data-pipeline",
      "environment": "production"
    }
  }
}
```

### Create a Fixed-Size Cluster

Create a cluster with a fixed number of workers:

```json
{
  "tool": "create_cluster",
  "arguments": {
    "cluster_name": "fixed-size-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 4,
    "autotermination_minutes": 60
  }
}
```

### Get Cluster Details

```json
{
  "tool": "get_cluster",
  "arguments": {
    "cluster_id": "1234-567890-abc123"
  }
}
```

### Start and Stop Clusters

**Start a terminated cluster:**
```json
{
  "tool": "start_cluster",
  "arguments": {
    "cluster_id": "1234-567890-abc123"
  }
}
```

**Terminate a running cluster:**
```json
{
  "tool": "terminate_cluster",
  "arguments": {
    "cluster_id": "1234-567890-abc123"
  }
}
```

### List Clusters with Pagination

```json
{
  "tool": "list_clusters",
  "arguments": {
    "page_size": 50
  }
}
```

---

## Job Management

### Create a Simple Notebook Job

```json
{
  "tool": "create_job",
  "arguments": {
    "name": "Daily ETL Job",
    "tasks": [{
      "task_key": "etl_task",
      "notebook_task": {
        "notebook_path": "/Workspace/ETL/process_data",
        "base_parameters": {
          "date": "{{job.start_time.iso_date}}"
        }
      },
      "existing_cluster_id": "1234-567890-abc123"
    }],
    "schedule": {
      "quartz_cron_expression": "0 0 2 * * ?",
      "timezone_id": "America/Los_Angeles"
    },
    "email_notifications": {
      "on_failure": ["data-eng@company.com"]
    }
  }
}
```

### Create a Multi-Task Job

```json
{
  "tool": "create_job",
  "arguments": {
    "name": "Multi-Stage Pipeline",
    "tasks": [
      {
        "task_key": "extract",
        "notebook_task": {
          "notebook_path": "/Workspace/Pipeline/extract"
        },
        "new_cluster": {
          "spark_version": "13.3.x-scala2.12",
          "node_type_id": "i3.xlarge",
          "num_workers": 2
        }
      },
      {
        "task_key": "transform",
        "depends_on": [{"task_key": "extract"}],
        "notebook_task": {
          "notebook_path": "/Workspace/Pipeline/transform"
        },
        "existing_cluster_id": "1234-567890-abc123"
      },
      {
        "task_key": "load",
        "depends_on": [{"task_key": "transform"}],
        "notebook_task": {
          "notebook_path": "/Workspace/Pipeline/load"
        },
        "existing_cluster_id": "1234-567890-abc123"
      }
    ]
  }
}
```

### Run a Job

**Run with default parameters:**
```json
{
  "tool": "run_job",
  "arguments": {
    "job_id": 12345
  }
}
```

**Run with custom parameters:**
```json
{
  "tool": "run_job",
  "arguments": {
    "job_id": 12345,
    "notebook_params": {
      "date": "2024-01-15",
      "environment": "production"
    }
  }
}
```

### Monitor Job Run

```json
{
  "tool": "get_run",
  "arguments": {
    "run_id": 67890
  }
}
```

### Cancel a Running Job

```json
{
  "tool": "cancel_run",
  "arguments": {
    "run_id": 67890
  }
}
```

---

## SQL Operations

### Execute a Simple Query

```json
{
  "tool": "execute_statement",
  "arguments": {
    "warehouse_id": "abc123def456",
    "statement": "SELECT * FROM sales.transactions WHERE date >= '2024-01-01' LIMIT 100",
    "catalog": "sales",
    "schema": "default"
  }
}
```

### Execute a Complex Aggregation

```json
{
  "tool": "execute_statement",
  "arguments": {
    "warehouse_id": "abc123def456",
    "statement": "SELECT customer_id, SUM(amount) as total_sales, COUNT(*) as num_orders FROM sales.transactions WHERE date >= '2024-01-01' GROUP BY customer_id ORDER BY total_sales DESC LIMIT 100",
    "catalog": "sales",
    "schema": "default"
  }
}
```

### Execute Parameterized Query

```json
{
  "tool": "execute_statement",
  "arguments": {
    "warehouse_id": "abc123def456",
    "statement": "SELECT * FROM sales.transactions WHERE date >= :start_date AND date <= :end_date",
    "parameters": [
      {"name": "start_date", "value": "2024-01-01"},
      {"name": "end_date", "value": "2024-01-31"}
    ]
  }
}
```

### Check Query Status

```json
{
  "tool": "get_statement",
  "arguments": {
    "statement_id": "01ef1234-5678-90ab-cdef-1234567890ab"
  }
}
```

### Execute Multiple Statements

```json
{
  "tool": "execute_statements_batch",
  "arguments": {
    "warehouse_id": "abc123def456",
    "statements": [
      "CREATE TABLE IF NOT EXISTS temp.results AS SELECT * FROM source.data WHERE date = '2024-01-01'",
      "INSERT INTO analytics.summary SELECT * FROM temp.results",
      "DROP TABLE temp.results"
    ],
    "catalog": "analytics"
  }
}
```

---

## Workspace Management

### List Workspace Contents

```json
{
  "tool": "list_workspace_objects",
  "arguments": {
    "path": "/Users/user@example.com"
  }
}
```

### Export a Notebook

**Export as Jupyter:**
```json
{
  "tool": "export_workspace_object",
  "arguments": {
    "path": "/Users/user@example.com/my_analysis",
    "format": "JUPYTER"
  }
}
```

**Export as HTML:**
```json
{
  "tool": "export_workspace_object",
  "arguments": {
    "path": "/Users/user@example.com/my_analysis",
    "format": "HTML"
  }
}
```

### Create Directories

```json
{
  "tool": "mkdirs",
  "arguments": {
    "path": "/Workspace/Projects/NewProject"
  }
}
```

### Delete Workspace Objects

**Delete a single notebook:**
```json
{
  "tool": "delete_workspace_object",
  "arguments": {
    "path": "/Users/user@example.com/old_notebook"
  }
}
```

**Delete a directory recursively:**
```json
{
  "tool": "delete_workspace_object",
  "arguments": {
    "path": "/Workspace/Projects/OldProject",
    "recursive": true
  }
}
```

---

## Unity Catalog

### Create a Three-Level Namespace

**1. Create catalog:**
```json
{
  "tool": "create_catalog",
  "arguments": {
    "catalog_name": "production",
    "comment": "Production data catalog"
  }
}
```

**2. Create schema:**
```json
{
  "tool": "create_schema",
  "arguments": {
    "catalog_name": "production",
    "schema_name": "sales",
    "comment": "Sales data schema"
  }
}
```

**3. Query tables:**
```json
{
  "tool": "list_tables",
  "arguments": {
    "catalog_name": "production",
    "schema_name": "sales"
  }
}
```

### Explore Catalog Hierarchy

**List all catalogs:**
```json
{
  "tool": "list_catalogs",
  "arguments": {}
}
```

**List schemas in a catalog:**
```json
{
  "tool": "list_schemas",
  "arguments": {
    "catalog_name": "production"
  }
}
```

**List tables in a schema:**
```json
{
  "tool": "list_tables",
  "arguments": {
    "catalog_name": "production",
    "schema_name": "sales"
  }
}
```

### Get Table Details

```json
{
  "tool": "get_table",
  "arguments": {
    "full_name": "production.sales.transactions"
  }
}
```

### Delete Resources

**Delete a table:**
```json
{
  "tool": "delete_table",
  "arguments": {
    "full_name": "production.sales.temp_table"
  }
}
```

**Delete a schema:**
```json
{
  "tool": "delete_schema",
  "arguments": {
    "full_name": "production.temp_schema"
  }
}
```

**Delete a catalog (with force):**
```json
{
  "tool": "delete_catalog",
  "arguments": {
    "catalog_name": "old_catalog",
    "force": true
  }
}
```

---

## Secrets Management

### Create and Manage Secrets

**1. Create a secret scope:**
```json
{
  "tool": "create_secret_scope",
  "arguments": {
    "scope_name": "api-keys"
  }
}
```

**2. Add secrets:**
```json
{
  "tool": "put_secret",
  "arguments": {
    "scope_name": "api-keys",
    "key": "openai_api_key",
    "string_value": "sk-..."
  }
}
```

```json
{
  "tool": "put_secret",
  "arguments": {
    "scope_name": "api-keys",
    "key": "stripe_api_key",
    "string_value": "sk_live_..."
  }
}
```

**3. List secrets:**
```json
{
  "tool": "list_secrets",
  "arguments": {
    "scope_name": "api-keys"
  }
}
```

**4. Delete a secret:**
```json
{
  "tool": "delete_secret",
  "arguments": {
    "scope_name": "api-keys",
    "key": "old_api_key"
  }
}
```

---

## AI/BI with Genie

### Natural Language SQL Queries

**1. Start a conversation:**
```json
{
  "tool": "start_genie_conversation",
  "arguments": {
    "space_id": "01ef1234567890ab"
  }
}
```

**2. Ask a question:**
```json
{
  "tool": "create_genie_message",
  "arguments": {
    "space_id": "01ef1234567890ab",
    "conversation_id": "01ef1234567890cd",
    "content": "Show me the top 10 customers by revenue this quarter"
  }
}
```

**3. Get the results:**
```json
{
  "tool": "get_genie_message_query_result",
  "arguments": {
    "space_id": "01ef1234567890ab",
    "conversation_id": "01ef1234567890cd",
    "message_id": "01ef1234567890ef"
  }
}
```

### Complex Analytics Questions

```json
{
  "tool": "create_genie_message",
  "arguments": {
    "space_id": "01ef1234567890ab",
    "conversation_id": "01ef1234567890cd",
    "content": "What is the month-over-month growth rate for each product category?"
  }
}
```

```json
{
  "tool": "create_genie_message",
  "arguments": {
    "space_id": "01ef1234567890ab",
    "conversation_id": "01ef1234567890cd",
    "content": "Which regions have the highest customer churn rate?"
  }
}
```

---

## Batch Operations

### Get Multiple Clusters

```json
{
  "tool": "get_clusters_batch",
  "arguments": {
    "cluster_ids": [
      "1234-567890-abc123",
      "1234-567890-def456",
      "1234-567890-ghi789"
    ]
  }
}
```

### Delete Multiple Tables

```json
{
  "tool": "delete_tables_batch",
  "arguments": {
    "table_names": [
      "production.temp.table1",
      "production.temp.table2",
      "production.temp.table3"
    ]
  }
}
```

### Bulk Secret Operations

**Add multiple secrets:**
```json
{
  "tool": "put_secrets_batch",
  "arguments": {
    "secrets": [
      {
        "scope_name": "api-keys",
        "key": "api_key_1",
        "string_value": "value1"
      },
      {
        "scope_name": "api-keys",
        "key": "api_key_2",
        "string_value": "value2"
      },
      {
        "scope_name": "api-keys",
        "key": "api_key_3",
        "string_value": "value3"
      }
    ]
  }
}
```

**Delete multiple secrets:**
```json
{
  "tool": "delete_secrets_batch",
  "arguments": {
    "secrets": [
      {"scope_name": "api-keys", "key": "old_key_1"},
      {"scope_name": "api-keys", "key": "old_key_2"},
      {"scope_name": "api-keys", "key": "old_key_3"}
    ]
  }
}
```

---

## Account Management

### List Account Resources

**List all workspaces:**
```json
{
  "tool": "list_account_workspaces",
  "arguments": {}
}
```

**List all users:**
```json
{
  "tool": "list_account_users",
  "arguments": {}
}
```

**List all groups:**
```json
{
  "tool": "list_account_groups",
  "arguments": {}
}
```

**List service principals:**
```json
{
  "tool": "list_account_service_principals",
  "arguments": {}
}
```

### Get Account Details

**Get workspace details:**
```json
{
  "tool": "get_account_workspace",
  "arguments": {
    "workspace_id": "1234567890123456"
  }
}
```

**Get user details:**
```json
{
  "tool": "get_account_user",
  "arguments": {
    "user_id": "1234567890123456"
  }
}
```

**Get group details:**
```json
{
  "tool": "get_account_group",
  "arguments": {
    "group_id": "1234567890123456"
  }
}
```

---

## Real-World Workflows

### Workflow 1: Daily Data Pipeline

**Setup:**
1. Create a cluster
2. Create a scheduled job
3. Configure email notifications

```json
// Step 1: Create cluster
{
  "tool": "create_cluster",
  "arguments": {
    "cluster_name": "etl-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 4,
    "autotermination_minutes": 30
  }
}

// Step 2: Create job (use cluster_id from step 1)
{
  "tool": "create_job",
  "arguments": {
    "name": "Daily Sales ETL",
    "tasks": [{
      "task_key": "etl",
      "notebook_task": {
        "notebook_path": "/Workspace/ETL/daily_sales"
      },
      "existing_cluster_id": "1234-567890-abc123"
    }],
    "schedule": {
      "quartz_cron_expression": "0 0 2 * * ?",
      "timezone_id": "UTC"
    },
    "email_notifications": {
      "on_failure": ["data-team@company.com"],
      "on_success": ["data-team@company.com"]
    }
  }
}
```

### Workflow 2: Ad-Hoc Analysis

**Interactive analysis workflow:**

```json
// 1. Start a SQL warehouse
{
  "tool": "start_warehouse",
  "arguments": {
    "warehouse_id": "abc123"
  }
}

// 2. Run exploratory queries
{
  "tool": "execute_statement",
  "arguments": {
    "warehouse_id": "abc123",
    "statement": "SELECT COUNT(*), AVG(price), MAX(price) FROM sales.transactions WHERE date >= '2024-01-01'"
  }
}

// 3. Export results via notebook
{
  "tool": "export_workspace_object",
  "arguments": {
    "path": "/Users/analyst@company.com/analysis_results",
    "format": "HTML"
  }
}

// 4. Stop warehouse when done
{
  "tool": "stop_warehouse",
  "arguments": {
    "warehouse_id": "abc123"
  }
}
```

### Workflow 3: Environment Setup

**Setting up a new project:**

```json
// 1. Create catalog and schema
{
  "tool": "create_catalog",
  "arguments": {
    "catalog_name": "project_x",
    "comment": "Project X data catalog"
  }
}

{
  "tool": "create_schema",
  "arguments": {
    "catalog_name": "project_x",
    "schema_name": "staging"
  }
}

{
  "tool": "create_schema",
  "arguments": {
    "catalog_name": "project_x",
    "schema_name": "production"
  }
}

// 2. Create workspace directories
{
  "tool": "mkdirs",
  "arguments": {
    "path": "/Workspace/Projects/ProjectX"
  }
}

// 3. Set up secrets
{
  "tool": "create_secret_scope",
  "arguments": {
    "scope_name": "project-x-keys"
  }
}

{
  "tool": "put_secret",
  "arguments": {
    "scope_name": "project-x-keys",
    "key": "api_key",
    "string_value": "sk-..."
  }
}

// 4. Create project cluster
{
  "tool": "create_cluster",
  "arguments": {
    "cluster_name": "project-x-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "autoscale": {
      "min_workers": 2,
      "max_workers": 10
    },
    "custom_tags": {
      "project": "project-x",
      "team": "data-science"
    }
  }
}
```

---

## Tips and Best Practices

### Performance

- **Use batch operations** when working with multiple resources
- **Specify page_size** for large lists to control memory usage
- **Stop warehouses** when not in use to save costs
- **Use autotermination** for development clusters

### Organization

- **Use descriptive names** for clusters, jobs, and resources
- **Add tags** to clusters for cost tracking
- **Use comments** when creating Unity Catalog objects
- **Organize workspaces** with clear folder structures

### Security

- **Use secrets** for API keys and credentials
- **Don't hardcode** sensitive values in notebooks
- **Set appropriate permissions** on Unity Catalog objects
- **Use service principals** for production jobs

### Cost Optimization

- **Terminate unused clusters** promptly
- **Use autoscaling** to match workload
- **Stop warehouses** when not querying
- **Use smaller instance types** for development

---

## Next Steps

- See [API Reference](api-reference.md) for complete tool documentation
- See [Error Handling](error-handling.md) for troubleshooting
- See [Configuration](configuration.md) for advanced setup
- See [Authentication](authentication.md) for auth methods

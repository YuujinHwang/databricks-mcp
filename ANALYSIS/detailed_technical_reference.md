# Detailed Technical Reference - Result Set Handling

## Architecture Overview

```
MCP Client (Claude)
       ↓
 stdio_server() [Line 1815-1820]
       ↓
call_tool(name, arguments) [Line 1057-1807]
       ↓
Tool Implementation (100+ branches)
       ↓
Databricks SDK Client
       ↓
Databricks REST API
       ↓
Response → JSON Serialization [Line 1802] → TextContent
```

---

## Critical Code Sections

### 1. Result Limiting in SQL Execution

**File**: `/home/user/databricks-mcp/src/databricks_mcp/server.py`

#### execute_statement (Lines 1557-1592)
```python
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
        params.row_limit = arguments["row_limit"]  # PARAMETER SUPPORTED

    response = w.statement_execution.execute_statement(**params.as_dict())

    result = {
        "statement_id": response.statement_id,
        "status": str(response.status.state) if response.status else None,
    }

    # Include result data if available
    if response.result:
        result["result"] = {
            "row_count": response.result.row_count,
            "data_array": response.result.data_array[:100] if response.result.data_array else None,  # <-- CRITICAL LIMIT
            "truncated": response.result.truncated,  # FLAG ACKNOWLEDGES MORE DATA EXISTS
        }
        if response.manifest:
            result["manifest"] = {
                "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                "total_row_count": response.manifest.total_row_count,  # TOTAL AVAILABLE
                "total_chunk_count": response.manifest.total_chunk_count,  # CHUNKS AVAILABLE BUT UNUSED
            }
```

**Issues**:
1. Line 1584: `[:100]` slicing hard-coded - ignores actual result size
2. Line 1585: `truncated` flag indicates more rows exist but doesn't fetch them
3. Lines 1590-1591: Manifest shows total rows and chunks available but never fetches them
4. API supports `row_limit` parameter but not `chunk` fetching in subsequent calls

#### get_statement (Lines 1594-1613)
```python
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
            "data_array": response.result.data_array[:100] if response.result.data_array else None,  # <-- SAME LIMIT
            "truncated": response.result.truncated,
        }
        if response.manifest:
            result["manifest"] = {
                "schema": response.manifest.schema.as_dict() if response.manifest.schema else None,
                "total_row_count": response.manifest.total_row_count,
            }
```

**Same Issues**: Identical 100-row limitation

---

### 2. List Operations - All 25 Instances

#### Pattern 1: Simple List (No Parameters)
```python
# Line 1066 - list_clusters
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
    for c in clusters  # ITERATOR MATERIALIZED HERE
]

# Line 1301 - list_warehouses
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

# Line 1330 - list_catalogs
catalogs = list(w.catalogs.list())
result = [{"name": c.name, "comment": c.comment, "owner": c.owner} for c in catalogs]

# Lines 1677, 1718, etc. - Similar pattern for:
# - list_vector_search_endpoints()
# - list_serving_endpoints()
```

#### Pattern 2: List with Nested API Call
```python
# Line 1355 - list_schemas
schemas = list(w.schemas.list(catalog_name=arguments["catalog_name"]))
result = [
    {"name": s.name, "full_name": s.full_name, "comment": s.comment} for s in schemas
]

# Line 1383 - list_tables
tables = list(
    w.tables.list(
        catalog_name=arguments["catalog_name"],
        schema_name=arguments["schema_name"],
    )
)

# Line 1697 - list_vector_search_indexes
indexes = list(
    w.vector_search_indexes.list_indexes(
        endpoint_name=arguments["endpoint_name"]
    )
)
```

#### Pattern 3: Account-Level Lists
```python
# Line 1482 - list_account_workspaces
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

# Lines 1500, 1518, 1528, 1541 - Similar for:
# - list_account_users()
# - list_account_groups()
# - list_account_service_principals()
# - list_account_metastores()
```

#### Pattern 4: The ONLY Tool with Limit Parameter
```python
# Lines 1122-1140 - list_jobs (EXCEPTION)
elif name == "list_jobs":
    w = get_workspace_client()
    kwargs = {}
    if "limit" in arguments:
        kwargs["limit"] = arguments["limit"]  # <-- ONLY TOOL WITH LIMIT!
    if "name" in arguments:
        kwargs["name"] = arguments["name"]

    jobs = list(w.jobs.list(**kwargs))  # BUT STILL MATERIALIZES ALL INTO MEMORY
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
```

**Problem**: Even though `limit` is passed to SDK, all matching results still loaded by `list()` call

---

### 3. JSON Serialization & Final Output

**Line 1802** - All responses serialized at once:
```python
return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
```

Called from `call_tool()` function (Line 1057-1807), which must:
1. Load all data into memory
2. Format as Python dict
3. Serialize entire dict to JSON string
4. Return as single TextContent message

**Memory Impact**:
- 100,000 items list operation → hundreds of MB JSON string
- Large SQL result set → megabytes of data
- No streaming capability → entire response must complete before sending

---

### 4. Large File Handling

**Lines 1200-1213** - Workspace Export:
```python
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
    # ENTIRE FILE CONTENT RETURNED - NO SIZE LIMIT!
```

**Issues**:
- No file size check
- Entire file loaded into memory
- Content base64-encoded and JSON-serialized
- Large notebooks (>10MB) would cause issues

---

### 5. Genie Query Result Handling

**Lines 1664-1672**:
```python
elif name == "get_genie_message_query_result":
    w = get_workspace_client()
    query_result = w.genie.get_message_query_result(
        space_id=arguments["space_id"],
        conversation_id=arguments["conversation_id"],
        message_id=arguments["message_id"],
        attachment_id=arguments["attachment_id"],
    )
    result = query_result.as_dict()  # <-- NO SIZE CONSIDERATION
    # Returns entire result as-is, could be large dataset
```

**Risk**: Genie might return large query results without limitation

---

### 6. Global Client Initialization

**Lines 32-60** - WorkspaceClient:
```python
def get_workspace_client() -> WorkspaceClient:
    """Get or create workspace client."""
    global _workspace_client
    if _workspace_client is None:
        auth_type = os.getenv("DATABRICKS_AUTH_TYPE", "").lower()

        if auth_type == "oauth-u2m" or auth_type == "oauth":
            config_kwargs = {
                "host": os.getenv("DATABRICKS_HOST"),
                "auth_type": "oauth-u2m",
            }
            if os.getenv("DATABRICKS_CLIENT_ID"):
                config_kwargs["client_id"] = os.getenv("DATABRICKS_CLIENT_ID")

            logger.info("Using OAuth U2M authentication - browser login required")
            _workspace_client = WorkspaceClient(**config_kwargs)
        else:
            _workspace_client = WorkspaceClient()

        logger.info(f"Initialized WorkspaceClient for {_workspace_client.config.host}")
    return _workspace_client
```

**Global State Issue**: Single workspace client for entire session - good for efficiency but could cause issues if authentication changes

---

## Data Flow Analysis

### SQL Query Execution Flow
```
User Request (execute_statement)
    ↓
ExecuteStatementRequestParams
    ↓
w.statement_execution.execute_statement(**params)
    ↓
Response {
    statement_id: str
    status: { state: str }
    result: {
        row_count: int
        data_array: [row1, row2, ...]  ← API RETURNS ALL AVAILABLE
        truncated: bool
    }
    manifest: {
        schema: {...}
        total_row_count: int            ← SHOWS TOTAL
        total_chunk_count: int          ← SHOWS CHUNKS AVAILABLE
    }
}
    ↓
MCP Server Processing [Line 1584]
    ↓
result["data_array"] = response.result.data_array[:100]  ← SLICED TO 100
    ↓
json.dumps() [Line 1802]
    ↓
TextContent → MCP Client
```

**Gap**: Between manifest showing total_chunk_count and server only returning first 100 rows

---

## List Operations Data Flow

```
User Request (e.g., list_clusters)
    ↓
w.clusters.list()  ← Returns SDK Iterator
    ↓
list(w.clusters.list())  ← FORCES FULL MATERIALIZATION
    ↓
list comprehension in lines 1067-1077
    ↓
result = [
    {extracted fields} for c in clusters
]
    ↓
json.dumps() [Line 1802]
    ↓
TextContent → MCP Client
```

**Problem**: Step 2 - forces full materialization instead of streaming

---

## Tool Definition vs Implementation

### Example: execute_statement

**Tool Definition** (Lines 775-807):
```python
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
)
```

**Implementation** (Lines 1557-1592):
- Supports `row_limit` parameter
- BUT: Ignores it and always limits to 100 in results (line 1584)
- Parameter goes into ExecuteStatementRequestParams but doesn't affect result slicing

---

## Missing Pagination/Streaming Infrastructure

### What Would Be Needed

#### 1. For SQL Results
```python
# NOT IMPLEMENTED:
def get_statement_chunk(statement_id: str, chunk_index: int) -> chunk_data
def list_statement_chunks(statement_id: str) -> list[chunk_metadata]
```

#### 2. For List Operations
```python
# NOT IMPLEMENTED:
def list_clusters_paginated(offset: int = 0, limit: int = 100) -> paginated_response
def list_clusters_stream() -> Iterator[cluster]
```

#### 3. For Large Files
```python
# NOT IMPLEMENTED:
def export_workspace_object_streaming(path: str) -> Iterator[bytes]
def get_export_status(export_id: str) -> status
```

---

## Summary of Critical Locations

| Issue | File | Lines | Severity |
|-------|------|-------|----------|
| SQL 100-row limit | server.py | 1584, 1606 | CRITICAL |
| All lists materialized | server.py | 1066, 1130, 1189, 1231, 1257, 1301, 1330, 1355, 1383, 1411, 1426, 1454, 1482, 1500, 1518, 1528, 1541, 1677, 1697, 1718, 1761, 1779 | HIGH |
| JSON serialization | server.py | 1802 | HIGH |
| Manifest unused | server.py | 1587-1592 | HIGH |
| File size unlimited | server.py | 1200-1213 | MEDIUM |
| Genie no limits | server.py | 1672 | MEDIUM |


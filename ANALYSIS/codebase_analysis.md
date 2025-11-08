# Databricks MCP Server - Comprehensive Codebase Analysis

## 1. Project Structure & Main Entry Points

### Project Layout
```
databricks-mcp/
├── src/
│   └── databricks_mcp/
│       ├── __init__.py          # Version info only (0.1.0)
│       └── server.py            # Entire implementation (1,826 lines)
├── pyproject.toml               # Dependencies & configuration
├── README.md                    # Comprehensive documentation
├── config.example.json          # Config examples
└── .env.example                 # Environment variables
```

### Main Entry Points
- **Script Entry Point**: `python -m databricks_mcp.server` or `databricks-mcp` command
- **Main Function**: `main()` at line 1809 in server.py
  - Initializes async stdio_server for MCP communication
  - Manages read/write streams to Claude Desktop or other MCP clients

### Global State Management
- **_workspace_client**: Global WorkspaceClient (lazily initialized)
- **_account_client**: Global AccountClient (lazily initialized)
- Both clients initialized on first use with OAuth U2M or other auth methods

---

## 2. Result Set Handling - Current Implementation

### Critical Issues with Large Results

#### A. SQL Query Result Limiting (Lines 1584, 1606)
```python
# execute_statement - Line 1584
"data_array": response.result.data_array[:100] if response.result.data_array else None,

# get_statement - Line 1606
"data_array": response.result.data_array[:100] if response.result.data_array else None,
```
**Problem**: Hard-coded limit to first 100 rows ALWAYS, regardless of actual result size
- Response contains `response.result.truncated` flag (included in result)
- Response includes `response.manifest.total_row_count` and `response.manifest.total_chunk_count`
- BUT: Only first 100 rows sent to client, remaining data lost

#### B. List Operations - All Data in Memory
All list operations convert API iterators to Python lists immediately:
```python
# Pattern used in 25+ list operations
clusters = list(w.clusters.list())
jobs = list(w.jobs.list(**kwargs))
catalogs = list(w.catalogs.list())
# ... etc (lines 1066, 1130, 1189, 1231, 1257, 1301, 1330, 1355, 1383, etc.)
```
**Problem**: Loads entire result set into memory before filtering/formatting
- No pagination or cursor support
- No limit on number of items returned
- Large workspaces could load thousands/millions of items

#### C. Response Formatting
All results formatted as single JSON string via `json.dumps(result, indent=2, default=str)` (line 1802)
- Entire response must be serialized before sending
- For large datasets, this becomes a memory problem
- No streaming capability

---

## 3. Where Streaming Support is Needed

### HIGH PRIORITY - Direct Data Retrieval

#### 3.1 SQL Query Execution (Lines 1556-1618)
- **Tools**: `execute_statement`, `get_statement`
- **Issue**: Hardcoded 100-row limit
- **Data Flow**:
  1. User executes SQL query on warehouse
  2. Databricks API returns result with chunking support (total_chunk_count available)
  3. MCP server limits to first 100 rows
  4. Client gets truncated data

#### 3.2 List Operations (25+ tools)
**Affected Tools** (all use `list(api.list())`):
- Clusters (1066)
- Jobs (1130) - supports `limit` param but loads all into memory
- Workspace objects (1189)
- DBFS (1231)
- Repos (1257)
- Warehouses (1301)
- Catalogs (1330)
- Schemas (1355)
- Tables (1383)
- Secret scopes (1411)
- Secrets (1426)
- Pipelines (1454)
- Account workspaces (1482)
- Account users (1500)
- Account groups (1518)
- Account service principals (1528)
- Account metastores (1541)
- Vector search endpoints (1677)
- Vector search indexes (1697)
- Serving endpoints (1718)
- Registered models (1761)
- Model versions (1779)

**Problems**:
- No pagination support
- No cursor/offset implementation
- All results loaded before transformation
- Some list tools have `limit` parameter (jobs) but it's passed to SDK only

#### 3.3 Genie AI/BI Query Results (Lines 1664-1672)
- **Tool**: `get_genie_message_query_result`
- **Issue**: Direct `as_dict()` conversion without size consideration
- **Risk**: Genie query results could be large datasets

### MEDIUM PRIORITY - API Response Streaming

#### 3.4 Workspace Object Export (Lines 1200-1213)
- **Tool**: `export_workspace_object`
- **Content**: Base64-encoded notebook/directory content
- **Issue**: Entire file content loaded into memory and JSON-encoded
- **Large Files**: Could contain megabytes of code

#### 3.5 Serving Endpoint Queries (Lines 1743-1750)
- **Tool**: `query_serving_endpoint`
- **Issue**: Full response formatted to JSON without size limits
- **Risk**: ML model inference could return large arrays/embeddings

---

## 4. MCP Tools/Resources Currently Implemented

### Summary: 100+ Tools Across 16 Categories

#### Category Breakdown:

| Category | Count | Tools |
|----------|-------|-------|
| **Clusters** | 6 | list, get, create, start, terminate, delete |
| **Jobs** | 7 | list, get, create, run, get_run, cancel_run, delete |
| **Workspace** | 5 | list, get_status, export, delete, mkdirs |
| **DBFS** | 3 | list, get_status, delete |
| **Repos** | 5 | list, get, create, update, delete |
| **SQL Warehouses** | 4 | list, get, start, stop |
| **UC Catalogs** | 4 | list, get, create, delete |
| **UC Schemas** | 4 | list, get, create, delete |
| **UC Tables** | 3 | list, get, delete |
| **Secrets** | 6 | list_scopes, create_scope, delete_scope, list, put, delete |
| **Pipelines (DLT)** | 4 | list, get, start_update, stop |
| **SQL Statements** | 3 | execute, get, cancel |
| **Genie (AI/BI)** | 4 | start_conversation, create_message, get_message, get_query_result |
| **Vector Search** | 4 | list_endpoints, get_endpoint, list_indexes, get_index |
| **Serving Endpoints** | 3 | list, get, query |
| **Model Registry** | 4 | list_models, get_model, list_versions, get_version |
| **Account Mgmt** | 9 | workspaces(2), users(2), groups(2), service_principals(1), metastores(2) |

### Tools Distribution
- **List/Query Operations**: ~40 tools
- **Create/Update Operations**: ~20 tools
- **Delete Operations**: ~15 tools
- **Execute/Query Operations**: ~10 tools
- **Status/Get Operations**: ~15 tools

### Resource Types (Implicit)
MCP implements tools only, no explicit resources, but operations are on:
- Compute (clusters, warehouses, pipelines)
- Data (Unity Catalog, DBFS, tables)
- Analytics (SQL warehouses, Genie)
- ML/AI (serving endpoints, model registry, vector search)
- Governance (secrets, account management)

---

## 5. Existing Streaming & Pagination Mechanisms

### What EXISTS
1. **SQL Statement API Chunking Support** (Lines 1587-1592)
   ```python
   if response.manifest:
       result["manifest"] = {
           "schema": response.manifest.schema.as_dict(),
           "total_row_count": response.manifest.total_row_count,
           "total_chunk_count": response.manifest.total_chunk_count,  # KEY!
       }
   ```
   - Databricks SDK returns chunk metadata
   - Server acknowledges chunks exist but doesn't fetch them
   - Only first chunk (limited to 100 rows) returned

2. **Jobs List Limit Parameter** (Lines 1183-1189, 1125-1126)
   ```python
   Tool parameter: "limit" in arguments -> passed to w.jobs.list(**kwargs)
   ```
   - Only jobs tool supports limit parameter
   - Other list operations don't expose limit control

3. **Truncation Flag** (Lines 1585, 1607)
   ```python
   "truncated": response.result.truncated,
   ```
   - Server knows data is truncated
   - Doesn't communicate paging mechanism to client

### What DOESN'T EXIST
1. **Cursor/Pagination Support**: No offset, cursor, or page tokens implemented
2. **Streaming Results**: All results serialized to JSON at once
3. **Chunk Fetching**: `total_chunk_count` from manifest never used to fetch additional chunks
4. **Result Size Control**: No configurable limits per tool
5. **Iterator Preservation**: All iterators converted to lists immediately
6. **Large File Handling**: No size checking or streaming for workspace exports
7. **Result Splitting**: No mechanism to split large results into multiple messages
8. **Progress Indication**: No progress updates for long-running operations

### Databricks SDK Capabilities (Unused)
- **Iterator Pattern**: SDK returns iterators that could be lazy-loaded
  - Currently: `list(sdk_iterator)` forces full materialization
  - Could: Implement generator patterns to stream results

- **Statement Result Chunks**: SDK supports fetching individual chunks
  - Currently: Only first result (100 rows) accessed
  - Could: Implement chunk iterator for SQL results

---

## 6. Specific Files/Functions Handling Result Sets

### Primary File
**File**: `/home/user/databricks-mcp/src/databricks_mcp/server.py` (1,826 lines)

### Key Functions & Sections

#### Result Limiting
- **Lines 1584, 1606**: Hard-coded 100-row limit for SQL results
  - Function: `call_tool()` → `execute_statement` and `get_statement` branches
  - Problem: `response.result.data_array[:100]`

#### List Operations (25+ locations)
- **Line 1066**: `list(w.clusters.list())`
- **Line 1130**: `list(w.jobs.list(**kwargs))`
- **Line 1189**: `list(w.workspace.list(path=path))`
- **Line 1231**: `list(w.dbfs.list(path=arguments["path"]))`
- **Lines 1257-1779**: 19 more list operations
- Problem: All use `list()` to materialize iterators

#### JSON Serialization
- **Line 1802**: Final result formatting
  ```python
  return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
  ```
  - All data converted to JSON string at once
  - No streaming capability

#### Manifest/Chunk Info (Unused)
- **Lines 1587-1592**: Manifest data extraction
  - `response.manifest.total_chunk_count` never used to fetch additional chunks
  - Could implement chunk iterator here

#### Genie Result Handling
- **Lines 1664-1672**: `get_genie_message_query_result`
  - Direct `result = query_result.as_dict()`
  - No size checking or streaming

#### Workspace Export
- **Lines 1200-1213**: `export_workspace_object`
  - `export = w.workspace.export(path=arguments["path"], format=export_format)`
  - Returns `export.content` directly
  - Could be large for big notebooks/files

---

## 7. Authentication & Initialization

### Authentication Methods Supported
1. **OAuth U2M** (User-to-Machine, Recommended)
2. **Personal Access Token (PAT)**
3. **Databricks Config File (~/.databrickscfg)**
4. **OAuth M2M** (Machine-to-Machine, Service Principals)

### Lazy Client Initialization
- **get_workspace_client()** (Lines 32-60)
  - Returns global `_workspace_client`
  - Initializes on first call based on `DATABRICKS_AUTH_TYPE` env var
  
- **get_account_client()** (Lines 63-94)
  - Requires `DATABRICKS_ACCOUNT_ID` environment variable
  - Handles both OAuth U2M and PAT authentication

---

## 8. Current Implementation Summary

### Strengths
- Comprehensive API coverage (100+ tools)
- Proper OAuth U2M authentication support
- Lazy client initialization
- Error handling with try/except and logging
- Async/await support for MCP protocol

### Critical Limitations
1. **Hard-coded 100-row limit** for SQL results despite API supporting chunking
2. **All results loaded into memory** - no streaming
3. **No pagination support** for list operations
4. **No cursor/offset mechanisms** implemented
5. **Large file handling** without size limits
6. **Manifest chunk data ignored** in SQL results
7. **All results JSON serialized at once** - no incremental output

### Compatibility
- **Databricks SDK**: 0.30.0+ required
- **MCP**: 1.0.0+
- **Python**: 3.10+

---

## 9. Recommended Areas for Streaming Implementation

### Phase 1: SQL Query Results (Highest Impact)
1. Fetch chunks beyond first 100 rows using `total_chunk_count`
2. Implement pagination tool for retrieving additional result chunks
3. Add chunked result support to MCP response

### Phase 2: List Operations
1. Add offset/limit parameters to all list tools
2. Preserve SDK iterators or implement generators
3. Implement cursor-based pagination

### Phase 3: Large File Handling
1. Add size checking for workspace exports
2. Implement streaming for large notebook content
3. Support resumable downloads

### Phase 4: Query Result Chunking
1. Implement result chunk fetcher tool
2. Add support for dynamic chunk size configuration
3. Stream results to client as chunks arrive

---

## 10. Dependencies & Configuration

### Required Dependencies
```toml
mcp>=1.0.0
databricks-sdk>=0.30.0
```

### Optional Dependencies
```toml
[dev]
pytest>=7.0.0
black>=23.0.0
ruff>=0.1.0
```

### Environment Variables
- `DATABRICKS_HOST`: Workspace URL
- `DATABRICKS_AUTH_TYPE`: "oauth-u2m" or empty for default
- `DATABRICKS_TOKEN`: PAT token (if not using OAuth)
- `DATABRICKS_ACCOUNT_ID`: Account ID for account-level operations
- `DATABRICKS_ACCOUNT_HOST`: Account URL (defaults to accounts.cloud.databricks.com)
- `DATABRICKS_CLIENT_ID`: Custom OAuth client ID (optional)

# Databricks MCP Server

A comprehensive Model Context Protocol (MCP) server that provides access to all Databricks REST APIs, including both Workspace-level and Account-level operations.

## Overview

This MCP server enables AI assistants like Claude to interact with Databricks through a standardized interface. It exposes Databricks functionality as MCP tools, allowing you to manage clusters, jobs, notebooks, Unity Catalog, and much more through conversational AI.

## Features

### Workspace-Level APIs

#### Compute Management
- **Clusters**: List, create, start, stop, terminate, and delete clusters
- **SQL Warehouses**: List, get details, start, and stop SQL warehouses

#### Jobs & Workflows
- **Jobs**: List, create, update, run, and delete jobs
- **Job Runs**: Get run details, cancel runs, monitor execution
- **Pipelines**: List, get, start, and stop Delta Live Tables pipelines

#### Data & Storage
- **Unity Catalog**: Manage catalogs, schemas, and tables
  - Create/list/delete catalogs
  - Create/list/delete schemas
  - List/get/delete tables
- **DBFS**: List, get status, and delete files in Databricks File System
- **Workspace Objects**: List, export, delete notebooks and directories

#### Development & Collaboration
- **Repos**: List, create, update, and delete Git repositories
- **Secrets**: Manage secret scopes and secrets for secure credential storage

### Account-Level APIs

- **Workspaces**: List and get workspace details across your account
- **Users**: List and get user information
- **Groups**: List and get group information
- **Service Principals**: List service principals
- **Metastores**: List and get Unity Catalog metastore details

## Installation

### Prerequisites

- Python 3.10 or higher
- Databricks workspace access with appropriate permissions
- Databricks authentication credentials (see Authentication section)

### Install from Source

```bash
git clone https://github.com/yourusername/databricks-mcp.git
cd databricks-mcp
pip install -e .
```

### Install from PyPI (once published)

```bash
pip install databricks-mcp-server
```

## Authentication

This MCP server uses the official Databricks SDK, which supports multiple authentication methods:

### Option 1: OAuth User Authentication (개인 사용자 OAuth - Recommended)

**사용자 브라우저를 통한 로그인 방식입니다. 개인 자격증명으로 안전하게 접속할 수 있습니다.**

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_AUTH_TYPE="oauth-u2m"
```

For account operations:
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_AUTH_TYPE="oauth-u2m"
export DATABRICKS_ACCOUNT_ID="your-account-id"
export DATABRICKS_ACCOUNT_HOST="https://accounts.cloud.databricks.com"
```

처음 MCP 서버를 실행하면 브라우저가 열리고 Databricks에 로그인하라는 메시지가 표시됩니다. 로그인 후 토큰이 자동으로 저장되어 다음 실행 시에는 다시 로그인할 필요가 없습니다.

**커스텀 OAuth 앱 사용 (선택사항):**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_AUTH_TYPE="oauth-u2m"
export DATABRICKS_CLIENT_ID="your-custom-oauth-app-client-id"
```

### Option 2: Personal Access Token (PAT)

For workspace operations:
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
```

For account operations (in addition to workspace credentials):
```bash
export DATABRICKS_ACCOUNT_ID="your-account-id"
```

### Option 3: Databricks Configuration File

Create or edit `~/.databrickscfg`:

```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = your-access-token

[ACCOUNT]
host = https://accounts.cloud.databricks.com
account_id = your-account-id
token = your-account-token
```

### Option 4: OAuth M2M (Machine-to-Machine, For Service Principals)

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_CLIENT_ID="your-client-id"
export DATABRICKS_CLIENT_SECRET="your-client-secret"
```

## Configuration

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### OAuth User Authentication (Recommended - 개인 OAuth 사용)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": [
        "-m",
        "databricks_mcp.server"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

Account operations를 포함한 전체 설정:
```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": [
        "-m",
        "databricks_mcp.server"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m",
        "DATABRICKS_ACCOUNT_ID": "your-account-id",
        "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
      }
    }
  }
}
```

#### Personal Access Token (PAT)

```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": [
        "-m",
        "databricks_mcp.server"
      ],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "your-access-token",
        "DATABRICKS_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

### Using with Other MCP Clients

The server can be run as a stdio-based MCP server:

```bash
python -m databricks_mcp.server
```

Or use the installed command:

```bash
databricks-mcp
```

## Usage Examples

Once configured with Claude Desktop or another MCP client, you can use natural language to interact with Databricks:

### Cluster Management

```
"List all clusters in my workspace"
"Create a new cluster named 'analytics-cluster' with Spark 13.3 and 2 workers"
"Start the cluster with ID abc-123-def"
"What's the status of cluster xyz-789?"
```

### Job Operations

```
"Show me all jobs"
"Create a job that runs my notebook at /Users/me/analysis.py"
"Run job ID 12345"
"What's the status of run 67890?"
"Cancel run 67890"
```

### Unity Catalog

```
"List all catalogs"
"Create a new catalog called 'analytics'"
"Show me all schemas in the 'main' catalog"
"Create a schema called 'bronze' in the 'analytics' catalog"
"List all tables in analytics.bronze"
```

### Workspace Management

```
"List all notebooks in /Users/me/"
"Export the notebook at /Users/me/analysis.py as Jupyter format"
"Create a directory at /Shared/team-analytics"
```

### Git Integration

```
"List all repos"
"Create a repo from https://github.com/myorg/myrepo using GitHub"
"Update repo 123 to the 'dev' branch"
```

### Account Operations

```
"List all workspaces in my account"
"Show me all users"
"List all metastores in the account"
"Get details for workspace ID 12345"
```

## Available Tools

The server exposes 70+ tools covering all major Databricks APIs:

### Clusters (6 tools)
- `list_clusters`, `get_cluster`, `create_cluster`, `start_cluster`, `terminate_cluster`, `delete_cluster`

### Jobs (7 tools)
- `list_jobs`, `get_job`, `create_job`, `run_job`, `get_run`, `cancel_run`, `delete_job`

### Workspace (5 tools)
- `list_workspace_objects`, `get_workspace_object_status`, `export_workspace_object`, `delete_workspace_object`, `mkdirs`

### DBFS (3 tools)
- `list_dbfs`, `get_dbfs_status`, `delete_dbfs`

### Repos (5 tools)
- `list_repos`, `get_repo`, `create_repo`, `update_repo`, `delete_repo`

### SQL Warehouses (4 tools)
- `list_warehouses`, `get_warehouse`, `start_warehouse`, `stop_warehouse`

### Unity Catalog - Catalogs (4 tools)
- `list_catalogs`, `get_catalog`, `create_catalog`, `delete_catalog`

### Unity Catalog - Schemas (4 tools)
- `list_schemas`, `get_schema`, `create_schema`, `delete_schema`

### Unity Catalog - Tables (3 tools)
- `list_tables`, `get_table`, `delete_table`

### Secrets (6 tools)
- `list_secret_scopes`, `create_secret_scope`, `delete_secret_scope`, `list_secrets`, `put_secret`, `delete_secret`

### Pipelines (4 tools)
- `list_pipelines`, `get_pipeline`, `start_pipeline_update`, `stop_pipeline`

### Account Management (9 tools)
- `list_account_workspaces`, `get_account_workspace`, `list_account_users`, `get_account_user`, `list_account_groups`, `get_account_group`, `list_account_service_principals`, `list_account_metastores`, `get_account_metastore`

## Development

### Project Structure

```
databricks-mcp/
├── src/
│   └── databricks_mcp/
│       ├── __init__.py
│       └── server.py          # Main MCP server implementation
├── pyproject.toml             # Project configuration
├── README.md                  # This file
└── .gitignore
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## Security Considerations

1. **Credentials**: Never commit credentials to version control. Use environment variables or the Databricks configuration file.
2. **Permissions**: The MCP server operates with the permissions of the authenticated user/service principal. Follow the principle of least privilege.
3. **Secrets**: When using the secrets API, secret values are write-only and cannot be retrieved through the API.
4. **Network**: Ensure your Databricks workspace is accessible from where the MCP server runs.

## Troubleshooting

### OAuth Authentication Issues

OAuth 브라우저 로그인 관련 문제:

1. **브라우저가 자동으로 열리지 않는 경우:**
   - 콘솔에 표시되는 URL을 수동으로 복사하여 브라우저에서 열기
   - 로그인 후 브라우저에서 승인 완료

2. **토큰 저장 위치:**
   - OAuth 토큰은 `~/.databricks/token-cache.json`에 자동 저장됩니다
   - 이 파일은 자동 갱신되며 수동 관리가 필요 없습니다

3. **토큰 초기화가 필요한 경우:**
   ```bash
   rm ~/.databricks/token-cache.json
   # MCP 서버를 다시 시작하면 재인증 진행
   ```

4. **MCP 환경에서 OAuth 사용 시 주의사항:**
   - Claude Desktop이 처음 MCP 서버를 시작할 때 브라우저 창이 열립니다
   - 로그인 후 Claude Desktop을 재시작할 필요가 없습니다
   - 토큰이 만료되면 자동으로 갱신을 시도합니다

### Authentication Errors

If you see authentication errors:
1. Verify your credentials are correctly set
2. Check that your token hasn't expired (PAT의 경우)
3. Ensure your workspace URL is correct (include `https://`)
4. For account operations, verify `DATABRICKS_ACCOUNT_ID` is set
5. OAuth 사용 시: 토큰 캐시를 삭제하고 재인증 시도

### Permission Errors

If operations fail with permission errors:
1. Verify your user/service principal has the necessary permissions
2. For Unity Catalog operations, ensure you have the appropriate grants
3. For account operations, ensure you have account-level access

### Connection Issues

If you can't connect to Databricks:
1. Check your network connectivity
2. Verify the workspace URL is correct
3. Check if there are any firewall rules blocking access

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built using the [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by the [Databricks SDK for Python](https://github.com/databricks/databricks-sdk-py)
- Inspired by the Databricks community

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/databricks-mcp/issues)
- Databricks Documentation: [docs.databricks.com](https://docs.databricks.com/)
- MCP Documentation: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

## Roadmap

Future enhancements planned:
- [ ] Support for more Databricks APIs (MLflow, Feature Store, etc.)
- [ ] Batch operations for efficiency
- [ ] Streaming support for large result sets
- [ ] Custom prompts and resources
- [ ] Enhanced error handling and retry logic
- [ ] Comprehensive test coverage
- [ ] Examples and tutorials
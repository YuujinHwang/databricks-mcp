# Databricks MCP Server

A Model Context Protocol (MCP) server that provides comprehensive access to Databricks REST APIs, enabling AI assistants like Claude to manage and interact with Databricks workspaces.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

The Databricks MCP Server exposes **82 tools** across **16 categories**, providing complete control over:

- **Compute**: Clusters and SQL Warehouses
- **Jobs & Workflows**: Job management and Delta Live Tables pipelines
- **Data**: Unity Catalog, DBFS, and workspace objects
- **SQL & Analytics**: SQL execution and Genie AI/BI
- **ML & AI**: Model serving, vector search, and feature store
- **Development**: Git repos and secrets management
- **Account**: Multi-workspace and user management

## Quick Start

### Installation

Choose one of these installation methods:

**Option 1: Using uvx (Recommended)**
```bash
# No installation needed - runs directly
uvx databricks-mcp
```

**Option 2: Using pip**
```bash
pip install databricks-mcp
```

**Option 3: Using Smithery**
```bash
npx @smithery/cli install databricks-mcp --client claude
```

### Configuration

Add to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

Replace `your-workspace` with your actual Databricks workspace URL.

### First Use

After configuration, restart Claude Desktop. On first use:

1. A browser window will open
2. Log in to Databricks
3. Authorize the connection
4. You're ready to use Databricks through Claude!

## Features

### 🚀 Compute Management
- **Clusters**: Create, start, stop, terminate, and manage compute clusters
- **SQL Warehouses**: Manage SQL warehouse lifecycle and configurations
- **Batch Operations**: Parallel operations on multiple resources

### 📊 Data & Analytics
- **Unity Catalog**: Full three-level namespace management (catalogs, schemas, tables)
- **SQL Execution**: Run queries, retrieve results, and manage statement execution
- **Genie AI/BI**: Natural language queries with Databricks Genie
- **DBFS**: File system operations for Databricks File System

### 🤖 ML & AI
- **Model Serving**: Deploy and query ML models via serving endpoints
- **Model Registry**: Manage registered models and versions in Unity Catalog
- **Vector Search**: Create and manage vector search endpoints and indexes
- **Feature Store**: Build and publish feature tables for ML pipelines

### 💼 Jobs & Workflows
- **Jobs**: Create, run, monitor, and manage Databricks jobs
- **Delta Live Tables**: Manage DLT pipelines for data engineering
- **Job Runs**: Track execution status and cancel running jobs

### 🔐 Security & Management
- **Secrets**: Secure credential storage with secret scopes
- **Git Repos**: Integrate GitHub, GitLab, and Bitbucket repositories
- **Account Management**: Multi-workspace administration and user management
- **Workspace**: Manage notebooks, directories, and workspace objects

### ⚡ Advanced Features
- **Error Handling**: Automatic retry with exponential backoff for transient failures
- **Rate Limiting**: Built-in handling of API rate limits
- **Batch Operations**: Efficient parallel processing of multiple requests
- **Comprehensive Logging**: Detailed error messages with actionable guidance

## Documentation

### 📚 Comprehensive Guides

- **[API Reference](docs/api-reference.md)** - Complete documentation of all 82 tools
- **[Authentication](docs/authentication.md)** - Setup guide for all auth methods
- **[Configuration](docs/configuration.md)** - Advanced configuration options
- **[Examples](docs/examples.md)** - Practical usage examples and workflows
- **[Error Handling](docs/error-handling.md)** - Troubleshooting and error reference

### 🎯 Quick Links

| Need | Document |
|------|----------|
| Get started quickly | [Quick Start](#quick-start) |
| See what tools are available | [API Reference](docs/api-reference.md) |
| Set up authentication | [Authentication](docs/authentication.md) |
| View usage examples | [Examples](docs/examples.md) |
| Troubleshoot errors | [Error Handling](docs/error-handling.md) |
| Configure for production | [Configuration](docs/configuration.md) |

## Usage Examples

Once configured, use natural language with Claude:

### Cluster Operations
```
"Create a new auto-scaling cluster with 2-8 workers"
"Start cluster abc-123 and run my ETL job"
"List all running clusters and their costs"
```

### SQL Analytics
```
"Execute: SELECT * FROM sales.transactions WHERE date >= '2024-01-01'"
"Run this query on my SQL warehouse: SELECT COUNT(*) FROM users"
"What's the status of my running SQL query?"
```

### Unity Catalog
```
"Create a new catalog called 'analytics'"
"List all tables in production.sales schema"
"Show me the schema of table ml_models.production.predictions"
```

### ML Operations
```
"List all serving endpoints"
"Query my-model-endpoint with input data [1.0, 2.0, 3.0]"
"Create a feature table for user demographics"
```

### Job Management
```
"Create a daily ETL job that runs at 2 AM"
"Run job 12345 with parameter date='2024-01-15'"
"Show me the status of all running jobs"
```

### Natural Language Analytics with Genie
```
"Ask Genie: What were the top 10 products by revenue last month?"
"Use Genie to analyze customer churn trends"
"Get query results from my Genie conversation"
```

## Tool Categories

The server provides **82 tools** organized into these categories:

| Category | Tools | Description |
|----------|-------|-------------|
| **Clusters** | 8 | Compute cluster management and batch operations |
| **Jobs** | 8 | Job creation, execution, and monitoring |
| **Workspace** | 5 | Notebook and directory management |
| **DBFS** | 3 | File system operations |
| **Repos** | 5 | Git repository integration |
| **SQL Warehouses** | 5 | SQL warehouse lifecycle management |
| **Unity Catalog** | 12 | Three-level namespace management |
| **Secrets** | 8 | Secure credential storage |
| **Pipelines** | 4 | Delta Live Tables management |
| **Account** | 9 | Multi-workspace administration |
| **SQL Execution** | 4 | Query execution and management |
| **Genie** | 4 | AI-powered natural language analytics |
| **Vector Search** | 4 | Vector search infrastructure |
| **Model Serving** | 3 | ML model deployment and inference |
| **Model Registry** | 4 | Model version management |
| **Feature Store** | 6 | ML feature engineering |

**Total: 82 tools** providing comprehensive Databricks functionality.

See the complete [API Reference](docs/api-reference.md) for detailed tool documentation.

## Authentication

Multiple authentication methods supported:

### OAuth U2M (Recommended)
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE="oauth-u2m"
```
✅ Most secure
✅ Automatic token refresh
✅ Best for development

### Personal Access Token
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi..."
```
✅ Simple setup
✅ Good for CI/CD
⚠️ Requires manual token management

### OAuth M2M (Service Principal)
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_CLIENT_ID="your-client-id"
DATABRICKS_CLIENT_SECRET="your-client-secret"
```
✅ Best for production
✅ Role-based permissions
✅ Automated processes

### Configuration File
```ini
# ~/.databrickscfg
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi...
```
✅ Multiple workspace management
✅ Shared with Databricks CLI

See [Authentication Guide](docs/authentication.md) for complete setup instructions.

## Architecture

The server is built with:

- **MCP SDK**: Implements Model Context Protocol for tool exposure
- **Databricks SDK**: Official Python SDK for Databricks APIs
- **Modular Handlers**: 16 specialized handlers for different API domains
- **Error Handling**: Automatic retry logic with exponential backoff
- **Batch Processing**: Parallel operations using ThreadPoolExecutor

### Project Structure

```
databricks-mcp/
├── src/databricks_mcp/
│   ├── server.py              # Main MCP server
│   └── handlers/              # API handlers
│       ├── clusters.py        # Cluster management
│       ├── jobs.py            # Job operations
│       ├── sql.py             # SQL execution
│       ├── unity_catalog.py   # UC management
│       └── ...                # 12 more handlers
├── docs/                      # Documentation
│   ├── api-reference.md
│   ├── authentication.md
│   ├── configuration.md
│   ├── examples.md
│   └── error-handling.md
├── pyproject.toml
└── README.md
```

## Error Handling

The server implements comprehensive error handling:

- **Automatic Retry**: Transient errors (5xx, 429, network) retry with exponential backoff
- **Clear Messages**: User-friendly error messages with actionable guidance
- **Categorization**: Errors classified as retryable vs. non-retryable
- **Context**: Detailed error context for debugging

See [Error Handling Guide](docs/error-handling.md) for details.

## Requirements

- Python 3.10 or higher
- Databricks workspace access
- Appropriate permissions for desired operations
- Network access to Databricks APIs

## Cloud Support

Works with all Databricks cloud platforms:

- **AWS**: `https://your-workspace.cloud.databricks.com`
- **Azure**: `https://adb-<workspace-id>.<random>.azuredatabricks.net`
- **GCP**: `https://<workspace-id>.gcp.databricks.com`

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See issues for areas needing help.

## Security

- **Credentials**: Never commit credentials to version control
- **Permissions**: Server operates with user/service principal permissions
- **Secrets**: Secret values are write-only via API
- **Network**: Ensure secure network connectivity

## Support

- **Documentation**: [Complete documentation in docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/YuujinHwang/databricks-mcp/issues)
- **Databricks Docs**: [docs.databricks.com](https://docs.databricks.com/)
- **MCP Docs**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [Databricks SDK for Python](https://github.com/databricks/databricks-sdk-py)
- Inspired by the Databricks community

## Roadmap

### ✅ Completed
- [x] 82 tools across 16 categories
- [x] SQL execution with chunked results
- [x] Genie AI/BI integration
- [x] Vector search support
- [x] Model serving and registry
- [x] Feature Store API
- [x] Comprehensive error handling
- [x] Batch operations
- [x] Modular handler architecture
- [x] Complete documentation

### 🚧 Planned
- [ ] Enhanced streaming for large result sets
- [ ] Custom MCP resources
- [ ] Additional batch operations
- [ ] Comprehensive test coverage
- [ ] Performance optimizations

---

**Ready to get started?** Follow the [Quick Start](#quick-start) guide above!

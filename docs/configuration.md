# Configuration

This document describes how to configure the Databricks MCP Server for different use cases.

## Quick Start Configuration

### Minimal Configuration

The minimum required configuration for Claude Desktop:

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

### Complete Configuration

Full configuration with all optional settings:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
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

---

## Installation Methods

### Method 1: Using uvx (Recommended)

No installation required - runs directly:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"]
    }
  }
}
```

### Method 2: Using pip + MCP CLI

Install and run via MCP CLI:

```bash
# Install
pip install databricks-mcp

# Configure
mcp install databricks-mcp
```

### Method 3: Using Smithery

One-command installation:

```bash
npx @smithery/cli install databricks-mcp --client claude
```

---

## Cloud-Specific Configuration

### AWS

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"
      }
    }
  }
}
```

### Azure

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://adb-<workspace-id>.<random>.azuredatabricks.net"
      }
    }
  }
}
```

### GCP

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://<workspace-id>.gcp.databricks.com"
      }
    }
  }
}
```

---

## Authentication Configurations

### OAuth U2M (Interactive)

Best for: Local development, interactive use

```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

### Personal Access Token

Best for: CI/CD, automated scripts

```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_TOKEN": "dapi..."
  }
}
```

### OAuth M2M (Service Principal)

Best for: Production deployments

```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_CLIENT_ID": "service-principal-id",
    "DATABRICKS_CLIENT_SECRET": "service-principal-secret"
  }
}
```

### Configuration File

Best for: Multiple workspace management

```json
{
  "env": {
    "DATABRICKS_CONFIG_PROFILE": "production"
  }
}
```

**Configuration file** (`~/.databrickscfg`):
```ini
[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[staging]
host = https://staging-workspace.cloud.databricks.com
token = dapi...
```

---

## Account-Level Configuration

To use account-level tools (user management, workspace management, etc.):

```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m",
    "DATABRICKS_ACCOUNT_ID": "12345678-90ab-cdef-1234-567890abcdef",
    "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
  }
}
```

**Required:**
- `DATABRICKS_ACCOUNT_ID`: Your Databricks account ID
- `DATABRICKS_ACCOUNT_HOST`: Account console URL (default: https://accounts.cloud.databricks.com)
- Account admin permissions

---

## Multi-Workspace Configuration

### Separate Server Instances

Configure multiple MCP server instances for different workspaces:

```json
{
  "mcpServers": {
    "databricks-production": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://prod.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_prod..."
      }
    },
    "databricks-staging": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://staging.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi_staging..."
      }
    },
    "databricks-dev": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://dev.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m"
      }
    }
  }
}
```

### Using Configuration Profiles

Use a single server with multiple profiles:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_CONFIG_PROFILE": "production"
      }
    }
  }
}
```

Switch profiles by changing `DATABRICKS_CONFIG_PROFILE` value.

---

## Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_HOST` | Workspace URL | `https://your-workspace.cloud.databricks.com` |

### Authentication Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_AUTH_TYPE` | Auth type (oauth-u2m) | `oauth-u2m` |
| `DATABRICKS_TOKEN` | Personal access token | `dapi...` |
| `DATABRICKS_CLIENT_ID` | OAuth client ID | `abc123...` |
| `DATABRICKS_CLIENT_SECRET` | OAuth client secret | `xyz789...` |
| `DATABRICKS_CONFIG_PROFILE` | Config file profile | `production` |

### Account Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_ACCOUNT_ID` | Account ID | `12345678-90ab-cdef...` |
| `DATABRICKS_ACCOUNT_HOST` | Account console URL | `https://accounts.cloud.databricks.com` |

---

## Configuration File Format

The server supports the standard Databricks CLI configuration file format.

**Location:**
- Linux/macOS: `~/.databrickscfg`
- Windows: `%USERPROFILE%\.databrickscfg`

**Format:**
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi...

[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi_prod...
account_id = 12345678-90ab-cdef-1234-567890abcdef

[staging]
host = https://staging-workspace.cloud.databricks.com
token = dapi_staging...

[dev]
host = https://dev-workspace.cloud.databricks.com
auth_type = oauth-u2m
```

**Usage:**
```json
{
  "env": {
    "DATABRICKS_CONFIG_PROFILE": "production"
  }
}
```

If `DATABRICKS_CONFIG_PROFILE` is not set, the `[DEFAULT]` profile is used.

---

## Platform-Specific Configuration

### Claude Desktop (macOS)

**Configuration file location:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Configuration:**
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

### Claude Desktop (Windows)

**Configuration file location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Configuration:**
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

### Other MCP Clients

The server is compatible with any MCP client. Configuration format may vary by client.

---

## Configuration Validation

After configuring the server, you can validate your setup:

### Check Connection
Use the `list_clusters` tool to verify connectivity:
```json
{
  "tool": "list_clusters",
  "arguments": {}
}
```

### Check Permissions
Try listing jobs to verify permissions:
```json
{
  "tool": "list_jobs",
  "arguments": {}
}
```

### Check Account Access
If account-level configured, try:
```json
{
  "tool": "list_account_workspaces",
  "arguments": {}
}
```

---

## Troubleshooting Configuration

### Error: "Could not connect to Databricks"

**Check:**
1. `DATABRICKS_HOST` is correct (no trailing slash)
2. Network connectivity to Databricks
3. Workspace URL is accessible

**Example fix:**
```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"
  }
}
```
❌ **Wrong:** `"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com/"`
✅ **Correct:** `"DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"`

### Error: "Authentication failed"

**Check:**
1. Authentication credentials are valid
2. Token hasn't expired (PAT)
3. Environment variables are correctly set

**Example fix for OAuth:**
```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m"
  }
}
```

### Error: "uvx command not found"

**Solution:** Install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use pip installation method instead:
```json
{
  "mcpServers": {
    "databricks": {
      "command": "python",
      "args": ["-m", "databricks_mcp"]
    }
  }
}
```

### Error: "Account operations not working"

**Check:**
1. `DATABRICKS_ACCOUNT_ID` is set
2. `DATABRICKS_ACCOUNT_HOST` is set (or uses default)
3. You have account admin permissions

**Example fix:**
```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "DATABRICKS_AUTH_TYPE": "oauth-u2m",
    "DATABRICKS_ACCOUNT_ID": "12345678-90ab-cdef-1234-567890abcdef",
    "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
  }
}
```

---

## Configuration Best Practices

### Security
- ✅ Use OAuth U2M for development
- ✅ Use OAuth M2M (service principals) for production
- ✅ Store tokens in environment variables, not config files committed to git
- ✅ Rotate credentials regularly
- ❌ Don't commit tokens to version control
- ❌ Don't share credentials between users

### Organization
- ✅ Use configuration profiles for multiple workspaces
- ✅ Name server instances descriptively (e.g., "databricks-production")
- ✅ Document which workspace each configuration connects to
- ❌ Don't mix production and development credentials

### Maintenance
- ✅ Test configuration after changes
- ✅ Keep documentation of workspace URLs and purposes
- ✅ Monitor token expiration dates
- ❌ Don't leave unused configurations

---

## Advanced Configuration

### Custom Python Environment

If you need to use a specific Python environment:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "databricks_mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com"
      }
    }
  }
}
```

### Proxy Configuration

The server respects standard HTTP proxy environment variables:

```json
{
  "env": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "HTTP_PROXY": "http://proxy.company.com:8080",
    "HTTPS_PROXY": "https://proxy.company.com:8080",
    "NO_PROXY": "localhost,127.0.0.1"
  }
}
```

---

## Next Steps

- See [Authentication](authentication.md) for detailed auth setup
- See [API Reference](api-reference.md) for available tools
- See [Examples](examples.md) for usage examples
- See [Error Handling](error-handling.md) for troubleshooting

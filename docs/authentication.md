# Authentication

The Databricks MCP Server supports multiple authentication methods to connect to your Databricks workspace and account.

## Overview

Authentication is configured through environment variables. The server automatically detects and uses the appropriate authentication method based on the variables you provide.

## Authentication Methods

### 1. OAuth User-to-Machine (U2M) - **Recommended**

OAuth U2M provides the most secure authentication method with automatic token refresh.

**Environment Variables:**
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_AUTH_TYPE="oauth-u2m"
DATABRICKS_CLIENT_ID="optional-custom-client-id"  # Optional
```

**How it works:**
1. On first use, a browser window opens for authentication
2. You log in with your Databricks credentials
3. An access token is obtained and cached
4. Token is automatically refreshed when needed

**Best for:**
- Interactive use in development
- Individual user authentication
- When you want automatic token management

**Example Claude Desktop Configuration:**
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

---

### 2. Personal Access Token (PAT)

Use a personal access token for simple, token-based authentication.

**Environment Variables:**
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_TOKEN="dapi..."
```

**How to generate a PAT:**
1. Go to Databricks workspace
2. Click your username → User Settings
3. Go to Access tokens
4. Click "Generate new token"
5. Copy the token (it will only be shown once)

**Best for:**
- CI/CD pipelines
- Automated scripts
- When OAuth is not available

**Security notes:**
- Store tokens securely (use environment variables, not hardcoded)
- Rotate tokens regularly
- Use token with minimum required permissions

**Example:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_TOKEN": "dapi..."
      }
    }
  }
}
```

---

### 3. Configuration File

Use the standard Databricks CLI configuration file.

**Configuration file location:**
- **Linux/macOS**: `~/.databrickscfg`
- **Windows**: `%USERPROFILE%\.databrickscfg`

**File format:**
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = dapi...

[production]
host = https://prod-workspace.cloud.databricks.com
token = dapi...

[staging]
host = https://staging-workspace.cloud.databricks.com
token = dapi...
```

**Environment Variables:**
```bash
# Use default profile
# No variables needed - automatically detected

# Or use a specific profile
DATABRICKS_CONFIG_PROFILE="production"
```

**Best for:**
- Managing multiple workspace configurations
- Sharing configuration with Databricks CLI
- Local development with multiple environments

**Example:**
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

---

### 4. OAuth Machine-to-Machine (M2M)

Use service principal authentication for automated, non-interactive scenarios.

**Environment Variables:**
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
DATABRICKS_CLIENT_ID="service-principal-client-id"
DATABRICKS_CLIENT_SECRET="service-principal-secret"
```

**How to set up:**
1. Create a service principal in your Databricks account
2. Generate OAuth credentials (client ID and secret)
3. Grant appropriate permissions to the service principal
4. Use the credentials in your configuration

**Best for:**
- Production deployments
- Automated processes
- CI/CD systems
- When you need role-based permissions

**Example:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_CLIENT_ID": "abc123...",
        "DATABRICKS_CLIENT_SECRET": "xyz789..."
      }
    }
  }
}
```

---

## Account-Level Authentication

For account-level operations (user management, workspace management, etc.), additional configuration is required.

**Environment Variables:**
```bash
# Account configuration (in addition to workspace auth)
DATABRICKS_ACCOUNT_ID="your-account-id"
DATABRICKS_ACCOUNT_HOST="https://accounts.cloud.databricks.com"
```

**Complete example with OAuth U2M:**
```json
{
  "mcpServers": {
    "databricks": {
      "command": "uvx",
      "args": ["databricks-mcp"],
      "env": {
        "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
        "DATABRICKS_AUTH_TYPE": "oauth-u2m",
        "DATABRICKS_ACCOUNT_ID": "12345678-90ab-cdef-1234-567890abcdef",
        "DATABRICKS_ACCOUNT_HOST": "https://accounts.cloud.databricks.com"
      }
    }
  }
}
```

**Finding your Account ID:**
1. Log in to Databricks account console
2. Go to Account settings
3. Copy the Account ID from the URL or settings page

**Account-level tools require:**
- Valid account-level authentication
- Account admin permissions
- Both workspace and account credentials configured

---

## Cloud-Specific Considerations

### AWS
```bash
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
```

### Azure
```bash
DATABRICKS_HOST="https://adb-<workspace-id>.<random>.azuredatabricks.net"
```

### GCP
```bash
DATABRICKS_HOST="https://<workspace-id>.gcp.databricks.com"
```

---

## Authentication Priority

When multiple authentication methods are configured, the server uses this priority order:

1. **OAuth M2M** (if `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` are set)
2. **Personal Access Token** (if `DATABRICKS_TOKEN` is set)
3. **OAuth U2M** (if `DATABRICKS_AUTH_TYPE="oauth-u2m"` is set)
4. **Configuration File** (if `~/.databrickscfg` exists)

---

## Testing Authentication

After configuring authentication, you can test it by running a simple tool:

**Example test:**
```json
{
  "tool": "list_clusters",
  "arguments": {}
}
```

If authentication is successful, you'll receive a list of clusters. If it fails, you'll see an authentication error with helpful guidance.

---

## Common Authentication Issues

### Issue: "Authentication failed"

**Causes:**
- Invalid or expired token
- Incorrect workspace URL
- Missing environment variables

**Solutions:**
- Verify `DATABRICKS_HOST` is correct (no trailing slash)
- For PAT: Generate a new token
- For OAuth: Delete cached credentials and re-authenticate
- Check that all required environment variables are set

### Issue: "Permission denied" (403 error)

**Causes:**
- Insufficient permissions
- Token doesn't have required scopes

**Solutions:**
- Verify user/service principal has appropriate permissions
- For workspace operations: Need workspace access
- For account operations: Need account admin permissions
- Generate new token with broader permissions if needed

### Issue: "Account operations not working"

**Causes:**
- Missing account configuration
- Not an account admin

**Solutions:**
- Set `DATABRICKS_ACCOUNT_ID` and `DATABRICKS_ACCOUNT_HOST`
- Verify you have account admin role
- Check account ID is correct

---

## Security Best Practices

### For Development
- ✅ Use OAuth U2M for interactive development
- ✅ Use configuration file for managing multiple workspaces
- ❌ Don't commit tokens to version control
- ❌ Don't share tokens between users

### For Production
- ✅ Use OAuth M2M with service principals
- ✅ Rotate credentials regularly
- ✅ Use environment-specific credentials
- ✅ Store secrets in secure secret managers
- ❌ Don't use personal tokens for shared services
- ❌ Don't grant overly broad permissions

### Token Storage
- Use environment variables
- Use secret management systems (AWS Secrets Manager, Azure Key Vault, etc.)
- Use CI/CD platform secret storage
- Never hardcode tokens in configuration files

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABRICKS_HOST` | Yes | Workspace URL |
| `DATABRICKS_TOKEN` | No | Personal access token |
| `DATABRICKS_AUTH_TYPE` | No | Authentication type (oauth-u2m) |
| `DATABRICKS_CLIENT_ID` | No | OAuth client ID |
| `DATABRICKS_CLIENT_SECRET` | No | OAuth client secret |
| `DATABRICKS_CONFIG_PROFILE` | No | Config file profile name |
| `DATABRICKS_ACCOUNT_ID` | No | Account ID (for account operations) |
| `DATABRICKS_ACCOUNT_HOST` | No | Account console URL |

---

## Next Steps

- See [Configuration](configuration.md) for additional server settings
- See [API Reference](api-reference.md) for available tools
- See [Examples](examples.md) for usage examples

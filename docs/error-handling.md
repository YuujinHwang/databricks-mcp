# Error Handling

The Databricks MCP Server implements comprehensive error handling with automatic retry logic for transient failures.

## Overview

The server categorizes errors into **retryable** and **non-retryable** types, and automatically retries operations that are likely to succeed on subsequent attempts.

## Error Categories

### Retryable Errors (Auto-Retry)

These errors trigger automatic retry with exponential backoff:

#### 1. Transient Server Errors
- **HTTP 500** (Internal Server Error)
- **HTTP 502** (Bad Gateway)
- **HTTP 503** (Service Unavailable)
- **HTTP 504** (Gateway Timeout)

**Why retryable:** Temporary server issues that typically resolve quickly.

**Retry behavior:**
- Max attempts: 4
- Exponential backoff: 1s, 2s, 4s, 8s
- Total max time: ~15 seconds

#### 2. Rate Limiting Errors
- **HTTP 429** (Too Many Requests)

**Why retryable:** Request rate exceeded, but will succeed once rate limit resets.

**Retry behavior:**
- Max attempts: 4
- Exponential backoff with jitter
- Respects `Retry-After` header if present

#### 3. Network Errors
- Connection timeout
- Connection refused
- Connection reset
- DNS resolution failures (temporary)

**Why retryable:** Network issues often resolve quickly.

#### 4. Resource State Errors
- Cluster pending/starting
- Warehouse initializing
- Job starting
- Resource not ready

**Why retryable:** Resource state will change to ready soon.

---

### Non-Retryable Errors (Fail Immediately)

These errors fail immediately without retry:

#### 1. Authentication Errors
- **HTTP 401** (Unauthorized)
- Invalid token
- Expired credentials
- Missing authentication

**Why not retryable:** Requires user action to fix credentials.

**How to fix:**
- Verify `DATABRICKS_HOST` is correct
- Check authentication credentials
- Generate new token if expired
- Re-authenticate for OAuth

**Example error message:**
```
Authentication failed: Invalid or expired token.
Please check your DATABRICKS_TOKEN or re-authenticate with OAuth.
See: https://docs.databricks.com/dev-tools/auth.html
```

#### 2. Permission Errors
- **HTTP 403** (Forbidden)
- Access denied
- Insufficient permissions

**Why not retryable:** Requires permission changes.

**How to fix:**
- Verify user/service principal has required permissions
- Request access from workspace admin
- Use credentials with appropriate permissions

**Example error message:**
```
Permission denied: You don't have access to this resource.
Please verify you have the necessary permissions or contact your workspace administrator.
```

#### 3. Not Found Errors
- **HTTP 404** (Not Found)
- Resource doesn't exist
- Invalid ID

**Why not retryable:** Resource genuinely doesn't exist.

**How to fix:**
- Verify resource ID is correct
- Check resource wasn't deleted
- Use list operation to find valid IDs

**Example error message:**
```
Resource not found: Cluster ID '1234-567890-abc123' does not exist.
Use list_clusters to see available clusters.
```

#### 4. Bad Request Errors
- **HTTP 400** (Bad Request)
- Invalid parameters
- Validation failures
- Malformed requests

**Why not retryable:** Request format or parameters are wrong.

**How to fix:**
- Review parameter requirements in API Reference
- Check data types and formats
- Validate required fields are present

**Example error message:**
```
Bad request: Invalid parameter 'spark_version'.
Expected format: 'X.Y.x-scala2.12' (e.g., '13.3.x-scala2.12')
See API Reference for valid values.
```

---

## Retry Configuration

### Default Behavior

```python
Max retry attempts: 4
Initial delay: 1 second
Max delay: 30 seconds
Backoff multiplier: 2x (exponential)
Jitter: ±20% randomization
```

### Retry Timing Example

| Attempt | Delay Before Retry | Cumulative Time |
|---------|-------------------|-----------------|
| 1 (initial) | 0s | 0s |
| 2 | ~1s | ~1s |
| 3 | ~2s | ~3s |
| 4 | ~4s | ~7s |
| (fail) | - | ~7s total |

### Exponential Backoff

The server uses exponential backoff to avoid overwhelming the API:

```
delay = min(initial_delay * (2 ^ attempt), max_delay) ± jitter
```

**Benefits:**
- Gives temporary issues time to resolve
- Reduces load on Databricks API
- Increases success rate for transient failures

---

## Error Message Format

All error messages follow a consistent, user-friendly format:

```
[Error Category]: Brief description of what went wrong.
Context: Additional details about the operation.
Suggestion: How to fix the issue.
Documentation: Link to relevant docs (when applicable).
```

### Example Error Messages

#### Authentication Error
```
Authentication Error: OAuth token has expired.

Context: Attempting to list clusters in workspace 'prod-workspace'.

Suggestion: Please re-authenticate using OAuth U2M.
Run the operation again and you'll be prompted to authenticate.

Documentation: https://docs.databricks.com/dev-tools/auth.html
```

#### Resource Not Found
```
Resource Not Found: Job ID 12345 does not exist.

Context: Attempting to get job details.

Suggestion: Use the 'list_jobs' tool to see available jobs.
The job may have been deleted or the ID may be incorrect.
```

#### Rate Limit
```
Rate Limit Exceeded: Too many requests.

Context: Attempting batch operation on 100 clusters.

Suggestion: The operation will automatically retry after the rate limit resets.
This error has been encountered 3 times, retrying in 8 seconds...
```

#### Validation Error
```
Validation Error: Invalid cluster configuration.

Context: Creating cluster 'my-cluster'.

Details:
  - 'spark_version' is required
  - 'node_type_id' must be a valid node type
  - Either 'num_workers' or 'autoscale' must be specified

Suggestion: Review the create_cluster tool documentation for required parameters.
```

---

## Common Error Scenarios

### Scenario 1: Cluster Not Ready

**Error:**
```
Resource State Error: Cluster is not ready (current state: PENDING).
```

**What happens:**
1. Initial request fails (cluster not ready)
2. Server waits 1 second
3. Retries automatically
4. Succeeds once cluster reaches RUNNING state

**No user action needed** - automatic retry handles this.

---

### Scenario 2: Rate Limiting During Batch Operations

**Error:**
```
Rate Limit Error: Too many concurrent requests (HTTP 429).
```

**What happens:**
1. Batch operation starts (e.g., get 50 clusters)
2. Rate limit hit after 20 requests
3. Server waits (respects Retry-After header)
4. Resumes remaining requests
5. All 50 requests eventually succeed

**No user action needed** - automatic retry with backoff.

---

### Scenario 3: Invalid Token

**Error:**
```
Authentication Error: Token is invalid or expired.
```

**What happens:**
1. Request fails immediately (no retry)
2. Error message with clear guidance returned
3. User must fix authentication

**User action required:**
- For PAT: Generate new token
- For OAuth: Re-authenticate
- Update configuration

---

### Scenario 4: Insufficient Permissions

**Error:**
```
Permission Error: User does not have permission to list account users.
```

**What happens:**
1. Request fails immediately (no retry)
2. Error message explains permission issue
3. User must get appropriate access

**User action required:**
- Contact workspace/account admin
- Request necessary permissions
- Or use different credentials

---

## Debugging Errors

### Error Context

Every error includes context about what operation was being performed:

```
Error: Resource not found

Context:
  Operation: get_cluster
  Cluster ID: 1234-567890-abc123
  Workspace: https://my-workspace.cloud.databricks.com
  User: user@example.com
```

### Retry History

For retryable errors, the error includes retry history:

```
Rate Limit Error: Too many requests

Retry History:
  Attempt 1: Failed (HTTP 429) - waiting 1s
  Attempt 2: Failed (HTTP 429) - waiting 2s
  Attempt 3: Failed (HTTP 429) - waiting 4s
  Attempt 4: Failed (HTTP 429) - giving up

Total time elapsed: 7 seconds
```

---

## Best Practices

### For Users

#### ✅ Do:
- Read error messages carefully - they include specific guidance
- Use list operations to verify resource IDs before get/delete operations
- Check authentication and permissions for 401/403 errors
- Wait for retryable errors to resolve automatically

#### ❌ Don't:
- Manually retry operations that already auto-retry
- Ignore specific error guidance in messages
- Use invalid or expired credentials
- Assume all errors are transient

### For Batch Operations

#### ✅ Do:
- Use batch tools for multiple operations (they handle rate limiting)
- Allow sufficient time for large batches
- Use appropriate batch sizes (e.g., 10-50 items)

#### ❌ Don't:
- Make hundreds of individual requests sequentially
- Use excessive batch sizes (1000+)
- Expect instant results for large operations

---

## Error Reference Table

| Error Type | HTTP Code | Retryable | Typical Cause | Fix |
|-----------|-----------|-----------|---------------|-----|
| Authentication | 401 | ❌ No | Invalid/expired token | Regenerate token or re-auth |
| Permission | 403 | ❌ No | Insufficient permissions | Request access |
| Not Found | 404 | ❌ No | Resource doesn't exist | Verify ID |
| Bad Request | 400 | ❌ No | Invalid parameters | Check parameters |
| Rate Limit | 429 | ✅ Yes | Too many requests | Wait (auto-retry) |
| Server Error | 500 | ✅ Yes | Databricks server issue | Wait (auto-retry) |
| Bad Gateway | 502 | ✅ Yes | Proxy/gateway issue | Wait (auto-retry) |
| Service Unavailable | 503 | ✅ Yes | Service temporarily down | Wait (auto-retry) |
| Gateway Timeout | 504 | ✅ Yes | Request timeout | Wait (auto-retry) |
| Connection Error | - | ✅ Yes | Network issue | Wait (auto-retry) |

---

## Handling Errors in Client Code

### MCP Protocol

Errors are returned through the MCP protocol with:
- Error code
- Error message (user-friendly)
- Error details (technical context)

### Example Error Response

```json
{
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to access this resource.",
    "details": {
      "operation": "list_account_users",
      "required_permission": "account_admin",
      "documentation": "https://docs.databricks.com/administration-guide/users-groups/index.html"
    }
  }
}
```

---

## Advanced Error Handling

### Custom Retry Logic

The server's retry mechanism is transparent to clients, but aware of:
- Resource state transitions (cluster starting → running)
- Rate limit windows
- Network stability
- API quota limits

### Circuit Breaking

For persistent failures:
- After 4 consecutive failures, operation fails
- Error includes complete retry history
- Clear guidance on what to do next

### Graceful Degradation

For batch operations:
- Partial failures are reported individually
- Successful operations complete even if some fail
- Summary includes both successes and failures

---

## Getting Help

If you encounter an error not covered in this document:

1. **Check error message** - includes specific guidance
2. **Review API Reference** - verify parameters are correct
3. **Check Authentication** - ensure credentials are valid
4. **Verify Permissions** - confirm user has necessary access
5. **Check Databricks Status** - [status.databricks.com](https://status.databricks.com)
6. **Report Issue** - [GitHub Issues](https://github.com/YuujinHwang/databricks-mcp)

---

## Next Steps

- See [API Reference](api-reference.md) for tool parameters
- See [Authentication](authentication.md) for fixing auth errors
- See [Configuration](configuration.md) for setup issues
- See [Examples](examples.md) for correct usage patterns

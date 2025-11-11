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
import time
from typing import Any, Optional
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed

from mcp.server import Server
from mcp.types import Tool, TextContent
from databricks.sdk import WorkspaceClient, AccountClient
from databricks.sdk.core import Config, DatabricksError
from databricks.feature_engineering import FeatureEngineeringClient
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)

# Import handlers
from .handlers import (
    ClustersHandler,
    JobsHandler,
    WorkspaceHandler,
    DBFSHandler,
    ReposHandler,
    WarehousesHandler,
    UnityCatalogHandler,
    SecretsHandler,
    PipelinesHandler,
    SQLHandler,
    GenieHandler,
    VectorSearchHandler,
    ServingHandler,
    ModelsHandler,
    FeatureStoreHandler,
    # Account-level handlers
    IAMHandler,
    BillingHandler,
    ProvisioningHandler,
    SettingsHandler,
    OAuthHandler,
    AccountUnityCatalogHandler,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ Custom Error Classes ============
class DatabricksAPIError(Exception):
    """Base exception for Databricks API errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, retryable: bool = False):
        self.message = message
        self.error_code = error_code
        self.retryable = retryable
        super().__init__(self.message)


class RetryableAPIError(DatabricksAPIError):
    """Exception for retryable API errors (network issues, rate limits, transient errors)."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code, retryable=True)


class NonRetryableAPIError(DatabricksAPIError):
    """Exception for non-retryable API errors (auth, permission, bad request)."""
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message, error_code, retryable=False)


class AuthenticationError(NonRetryableAPIError):
    """Exception for authentication failures."""
    pass


class PermissionError(NonRetryableAPIError):
    """Exception for permission/authorization failures."""
    pass


class ResourceNotFoundError(NonRetryableAPIError):
    """Exception for resource not found errors."""
    pass


class RateLimitError(RetryableAPIError):
    """Exception for rate limit errors."""
    pass


# ============ Error Categorization ============
def categorize_error(error: Exception) -> DatabricksAPIError:
    """
    Categorize errors into retryable vs non-retryable types.

    Args:
        error: The original exception

    Returns:
        A categorized DatabricksAPIError subclass
    """
    error_message = str(error)
    error_lower = error_message.lower()

    # Network and connection errors (retryable)
    if any(keyword in error_lower for keyword in [
        'connection', 'timeout', 'timed out', 'network', 'temporary failure',
        'connection refused', 'connection reset', 'broken pipe'
    ]):
        return RetryableAPIError(f"Network error: {error_message}")

    # Rate limiting (retryable with backoff)
    if any(keyword in error_lower for keyword in ['rate limit', '429', 'too many requests']):
        return RateLimitError(f"Rate limit exceeded: {error_message}")

    # Transient server errors (retryable)
    if any(keyword in error_lower for keyword in [
        '500', '502', '503', '504',
        'internal server error', 'bad gateway', 'service unavailable', 'gateway timeout'
    ]):
        return RetryableAPIError(f"Transient server error: {error_message}")

    # Resource not ready (retryable for long-running operations)
    if any(keyword in error_lower for keyword in [
        'not ready', 'still starting', 'pending', 'initializing'
    ]):
        return RetryableAPIError(f"Resource not ready: {error_message}")

    # Authentication errors (non-retryable)
    if any(keyword in error_lower for keyword in [
        'auth', 'unauthorized', '401', 'invalid token', 'token expired',
        'authentication failed', 'invalid credentials'
    ]):
        return AuthenticationError(f"Authentication failed: {error_message}")

    # Permission errors (non-retryable)
    if any(keyword in error_lower for keyword in [
        'permission', 'forbidden', '403', 'access denied', 'not authorized'
    ]):
        return PermissionError(f"Permission denied: {error_message}")

    # Resource not found (non-retryable)
    if any(keyword in error_lower for keyword in ['404', 'not found', 'does not exist']):
        return ResourceNotFoundError(f"Resource not found: {error_message}")

    # Bad request / validation errors (non-retryable)
    if any(keyword in error_lower for keyword in [
        '400', 'bad request', 'invalid', 'validation', 'malformed'
    ]):
        return NonRetryableAPIError(f"Invalid request: {error_message}")

    # Default: treat unknown errors as non-retryable to be safe
    return NonRetryableAPIError(f"Unexpected error: {error_message}")


def should_retry_error(error: Exception) -> bool:
    """
    Determine if an error should be retried.

    Args:
        error: The exception to check

    Returns:
        True if the error should be retried, False otherwise
    """
    # If it's already categorized, use its retryable flag
    if isinstance(error, DatabricksAPIError):
        return error.retryable

    # Otherwise, categorize it first
    categorized = categorize_error(error)
    return categorized.retryable


def format_error_message(error: Exception, operation: str) -> str:
    """
    Format a user-friendly error message with context and suggestions.

    Args:
        error: The exception that occurred
        operation: The operation that was being performed

    Returns:
        A formatted error message string
    """
    categorized = categorize_error(error) if not isinstance(error, DatabricksAPIError) else error

    message = f"Error during {operation}: {categorized.message}"

    # Add helpful suggestions based on error type
    if isinstance(categorized, AuthenticationError):
        message += "\n\nSuggestions:"
        message += "\n- Verify DATABRICKS_HOST and authentication credentials are set correctly"
        message += "\n- Check if OAuth token has expired (re-authenticate if needed)"
        message += "\n- Ensure you have valid Databricks access credentials"

    elif isinstance(categorized, PermissionError):
        message += "\n\nSuggestions:"
        message += "\n- Verify you have the necessary permissions for this operation"
        message += "\n- Contact your Databricks workspace administrator"
        message += "\n- Check if the resource is in a different workspace or catalog"

    elif isinstance(categorized, RateLimitError):
        message += "\n\nSuggestions:"
        message += "\n- The operation will be retried automatically with exponential backoff"
        message += "\n- If this persists, consider reducing request frequency"

    elif isinstance(categorized, ResourceNotFoundError):
        message += "\n\nSuggestions:"
        message += "\n- Verify the resource ID/name is correct"
        message += "\n- Check if the resource exists in your workspace"
        message += "\n- Ensure you're looking in the correct catalog/schema (for Unity Catalog resources)"

    elif isinstance(categorized, RetryableAPIError):
        message += "\n\nThis appears to be a temporary issue. The operation will be retried automatically."

    return message


# ============ Retry Configuration and Decorators ============
def create_retry_decorator(
    max_attempts: int = 4,
    min_wait: int = 1,
    max_wait: int = 30,
    operation_name: str = "operation"
):
    """
    Create a retry decorator with exponential backoff for API operations.

    Args:
        max_attempts: Maximum number of retry attempts (default: 4)
        min_wait: Minimum wait time in seconds between retries (default: 1)
        max_wait: Maximum wait time in seconds between retries (default: 30)
        operation_name: Name of the operation for logging

    Returns:
        A configured retry decorator
    """
    def before_sleep(retry_state):
        """Log retry attempts."""
        exception = retry_state.outcome.exception()
        attempt = retry_state.attempt_number
        wait_time = retry_state.next_action.sleep
        logger.warning(
            f"Retry attempt {attempt}/{max_attempts} for {operation_name} "
            f"after error: {str(exception)[:100]}. "
            f"Waiting {wait_time:.2f}s before next attempt..."
        )

    return retry(
        retry=retry_if_exception_type((
            RetryableAPIError,
            RateLimitError,
            ConnectionError,
            TimeoutError,
        )),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        before_sleep=before_sleep,
        reraise=True,
    )


def execute_with_retry(func, *args, **kwargs):
    """
    Execute a function with automatic retry logic for retryable errors.

    Args:
        func: The function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        The function result

    Raises:
        The categorized exception if all retries fail
    """
    max_attempts = kwargs.pop('_max_retry_attempts', 4)
    operation_name = kwargs.pop('_operation_name', func.__name__)

    retry_decorator = create_retry_decorator(
        max_attempts=max_attempts,
        operation_name=operation_name
    )

    @retry_decorator
    def _wrapped():
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Categorize the error
            categorized = categorize_error(e)
            # Re-raise categorized error (retry decorator will catch retryable ones)
            raise categorized

    try:
        return _wrapped()
    except RetryError as e:
        # All retries exhausted
        original_error = e.last_attempt.exception()
        logger.error(
            f"All {max_attempts} retry attempts failed for {operation_name}: "
            f"{str(original_error)}"
        )
        raise original_error
    except NonRetryableAPIError as e:
        # Non-retryable error encountered
        logger.error(f"Non-retryable error in {operation_name}: {str(e)}")
        raise


# Initialize MCP server
app = Server("databricks-mcp-server")

# Global clients (will be initialized on first use)
_workspace_client: Optional[WorkspaceClient] = None
_account_client: Optional[AccountClient] = None
_feature_engineering_client: Optional[FeatureEngineeringClient] = None


def get_workspace_client() -> WorkspaceClient:
    """Get or create workspace client with retry logic."""
    global _workspace_client
    if _workspace_client is None:
        def _create_client():
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
                client = WorkspaceClient(**config_kwargs)
            else:
                # Default: Authentication via environment variables or ~/.databrickscfg
                # Supports: PAT tokens, OAuth M2M, Azure CLI, etc.
                client = WorkspaceClient()

            logger.info(f"Initialized WorkspaceClient for {client.config.host}")
            return client

        try:
            # Create client with retry logic for transient network issues
            _workspace_client = execute_with_retry(
                _create_client,
                _max_retry_attempts=3,
                _operation_name="workspace_client_initialization"
            )
        except Exception as e:
            error_msg = format_error_message(e, "workspace client initialization")
            logger.error(error_msg)
            raise

    return _workspace_client


def get_account_client() -> AccountClient:
    """Get or create account client with retry logic."""
    global _account_client
    if _account_client is None:
        account_id = os.getenv("DATABRICKS_ACCOUNT_ID")
        if not account_id:
            raise ValueError(
                "DATABRICKS_ACCOUNT_ID environment variable required for account operations"
            )

        def _create_client():
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
                client = AccountClient(**config_kwargs)
            else:
                # Default authentication
                client = AccountClient(account_id=account_id)

            logger.info(f"Initialized AccountClient for account {account_id}")
            return client

        try:
            # Create client with retry logic for transient network issues
            _account_client = execute_with_retry(
                _create_client,
                _max_retry_attempts=3,
                _operation_name="account_client_initialization"
            )
        except Exception as e:
            error_msg = format_error_message(e, "account client initialization")
            logger.error(error_msg)
            raise

    return _account_client


def get_feature_engineering_client() -> FeatureEngineeringClient:
    """Get or create feature engineering client."""
    global _feature_engineering_client
    if _feature_engineering_client is None:
        # Feature Engineering Client requires a workspace client
        workspace_client = get_workspace_client()
        _feature_engineering_client = FeatureEngineeringClient()
        logger.info("Initialized FeatureEngineeringClient")
    return _feature_engineering_client


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Databricks API tools from all handlers."""
    tools = []

    # Workspace-level handlers
    tools.extend(ClustersHandler.get_tools())
    tools.extend(JobsHandler.get_tools())
    tools.extend(WorkspaceHandler.get_tools())
    tools.extend(DBFSHandler.get_tools())
    tools.extend(ReposHandler.get_tools())
    tools.extend(WarehousesHandler.get_tools())
    tools.extend(UnityCatalogHandler.get_tools())
    tools.extend(SecretsHandler.get_tools())
    tools.extend(PipelinesHandler.get_tools())
    tools.extend(SQLHandler.get_tools())
    tools.extend(GenieHandler.get_tools())
    tools.extend(VectorSearchHandler.get_tools())
    tools.extend(ServingHandler.get_tools())
    tools.extend(ModelsHandler.get_tools())
    tools.extend(FeatureStoreHandler.get_tools())

    # Account-level handlers
    tools.extend(IAMHandler.get_tools())
    tools.extend(BillingHandler.get_tools())
    tools.extend(ProvisioningHandler.get_tools())
    tools.extend(SettingsHandler.get_tools())
    tools.extend(OAuthHandler.get_tools())
    tools.extend(AccountUnityCatalogHandler.get_tools())


    # Account-level handlers
    tools.extend(IAMHandler.get_tools())
    tools.extend(BillingHandler.get_tools())
    tools.extend(ProvisioningHandler.get_tools())
    tools.extend(SettingsHandler.get_tools())
    tools.extend(OAuthHandler.get_tools())
    tools.extend(AccountUnityCatalogHandler.get_tools())
    
    # NEW: Workspace compute additions
    tools.extend(InstancePoolsHandler.get_tools())
    tools.extend(ClusterPoliciesHandler.get_tools())
    
    # NEW: Workspace ML additions
    tools.extend(ExperimentsHandler.get_tools())
    
    # NEW: Workspace admin
    tools.extend(WorkspaceIAMHandler.get_tools())
    tools.extend(WorkspaceSettingsHandler.get_tools())
    tools.extend(WorkspaceOAuthHandler.get_tools())
    
    # NEW: Apps, Dashboards, Sharing
    tools.extend(AppsHandler.get_tools())
    tools.extend(DashboardsHandler.get_tools())
    tools.extend(DeltaSharingHandler.get_tools())
    
    # NEW: Governance
    tools.extend(DataQualityHandler.get_tools())
    tools.extend(AssetTagsHandler.get_tools())
    
    # NEW: Marketplace, CleanRooms, Agents
    tools.extend(MarketplaceHandler.get_tools())
    tools.extend(CleanRoomsHandler.get_tools())
    tools.extend(AgentBricksHandler.get_tools())

    return tools


def _execute_api_operation(operation_func, operation_name: str):
    """
    Execute an API operation with retry logic.

    Args:
        operation_func: The function that performs the API operation
        operation_name: Name of the operation for logging and error messages

    Returns:
        The result of the operation

    Raises:
        DatabricksAPIError: Categorized error if the operation fails
    """
    return execute_with_retry(
        operation_func,
        _max_retry_attempts=4,
        _operation_name=operation_name
    )


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Databricks API operations by routing to appropriate handlers."""
    try:
        result = None

        # Helper function to wrap operations with retry logic
        def _run_operation(func):
            """Wrap operation in retry logic."""
            return _execute_api_operation(func, operation_name=name)

        # Get clients
        w = get_workspace_client()
        a = get_account_client()
        fe = get_feature_engineering_client()

        # Define handler routing map
        handler_map = {
            # Clusters
            "list_clusters": (ClustersHandler, w),
            "get_cluster": (ClustersHandler, w),
            "create_cluster": (ClustersHandler, w),
            "start_cluster": (ClustersHandler, w),
            "terminate_cluster": (ClustersHandler, w),
            "delete_cluster": (ClustersHandler, w),
            "get_clusters_batch": (ClustersHandler, w),
            "delete_clusters_batch": (ClustersHandler, w),

            # Jobs
            "list_jobs": (JobsHandler, w),
            "get_job": (JobsHandler, w),
            "create_job": (JobsHandler, w),
            "run_job": (JobsHandler, w),
            "get_run": (JobsHandler, w),
            "cancel_run": (JobsHandler, w),
            "delete_job": (JobsHandler, w),
            "get_jobs_batch": (JobsHandler, w),
            "delete_jobs_batch": (JobsHandler, w),

            # Workspace
            "list_workspace_objects": (WorkspaceHandler, w),
            "get_workspace_object_status": (WorkspaceHandler, w),
            "export_workspace_object": (WorkspaceHandler, w),
            "delete_workspace_object": (WorkspaceHandler, w),
            "mkdirs": (WorkspaceHandler, w),

            # DBFS
            "list_dbfs": (DBFSHandler, w),
            "get_dbfs_status": (DBFSHandler, w),
            "delete_dbfs": (DBFSHandler, w),

            # Repos
            "list_repos": (ReposHandler, w),
            "get_repo": (ReposHandler, w),
            "create_repo": (ReposHandler, w),
            "update_repo": (ReposHandler, w),
            "delete_repo": (ReposHandler, w),

            # Warehouses
            "list_warehouses": (WarehousesHandler, w),
            "get_warehouse": (WarehousesHandler, w),
            "start_warehouse": (WarehousesHandler, w),
            "stop_warehouse": (WarehousesHandler, w),
            "get_warehouses_batch": (WarehousesHandler, w),

            # Unity Catalog
            "list_catalogs": (UnityCatalogHandler, w),
            "get_catalog": (UnityCatalogHandler, w),
            "create_catalog": (UnityCatalogHandler, w),
            "delete_catalog": (UnityCatalogHandler, w),
            "list_schemas": (UnityCatalogHandler, w),
            "get_schema": (UnityCatalogHandler, w),
            "create_schema": (UnityCatalogHandler, w),
            "delete_schema": (UnityCatalogHandler, w),
            "list_tables": (UnityCatalogHandler, w),
            "get_table": (UnityCatalogHandler, w),
            "delete_table": (UnityCatalogHandler, w),
            "delete_tables_batch": (UnityCatalogHandler, w),

            # Secrets
            "list_secret_scopes": (SecretsHandler, w),
            "create_secret_scope": (SecretsHandler, w),
            "delete_secret_scope": (SecretsHandler, w),
            "list_secrets": (SecretsHandler, w),
            "put_secret": (SecretsHandler, w),
            "delete_secret": (SecretsHandler, w),
            "put_secrets_batch": (SecretsHandler, w),
            "delete_secrets_batch": (SecretsHandler, w),

            # Pipelines
            "list_pipelines": (PipelinesHandler, w),
            "get_pipeline": (PipelinesHandler, w),
            "start_pipeline_update": (PipelinesHandler, w),
            "stop_pipeline": (PipelinesHandler, w),

            # Account - IAM
            "list_account_workspaces": (IAMHandler, a),
            "get_account_workspace": (IAMHandler, a),
            "create_account_workspace": (IAMHandler, a),
            "update_account_workspace": (IAMHandler, a),
            "delete_account_workspace": (IAMHandler, a),
            "list_account_users": (IAMHandler, a),
            "get_account_user": (IAMHandler, a),
            "create_account_user": (IAMHandler, a),
            "update_account_user": (IAMHandler, a),
            "delete_account_user": (IAMHandler, a),
            "list_account_groups": (IAMHandler, a),
            "get_account_group": (IAMHandler, a),
            "create_account_group": (IAMHandler, a),
            "update_account_group": (IAMHandler, a),
            "delete_account_group": (IAMHandler, a),
            "list_account_service_principals": (IAMHandler, a),
            "get_account_service_principal": (IAMHandler, a),
            "create_account_service_principal": (IAMHandler, a),
            "update_account_service_principal": (IAMHandler, a),
            "delete_account_service_principal": (IAMHandler, a),
            "list_workspace_assignments": (IAMHandler, a),
            "get_workspace_assignment": (IAMHandler, a),
            "update_workspace_assignment": (IAMHandler, a),
            "delete_workspace_assignment": (IAMHandler, a),

            # Account - Billing
            "download_billable_usage": (BillingHandler, a),
            "list_budgets": (BillingHandler, a),
            "get_budget": (BillingHandler, a),
            "create_budget": (BillingHandler, a),
            "update_budget": (BillingHandler, a),
            "delete_budget": (BillingHandler, a),
            "list_log_delivery": (BillingHandler, a),
            "get_log_delivery": (BillingHandler, a),
            "create_log_delivery": (BillingHandler, a),
            "update_log_delivery": (BillingHandler, a),
            "list_usage_dashboards": (BillingHandler, a),
            "create_usage_dashboard": (BillingHandler, a),

            # Account - Provisioning
            "list_credentials": (ProvisioningHandler, a),
            "get_credential": (ProvisioningHandler, a),
            "create_credential": (ProvisioningHandler, a),
            "delete_credential": (ProvisioningHandler, a),
            "list_storage_configurations": (ProvisioningHandler, a),
            "get_storage_configuration": (ProvisioningHandler, a),
            "create_storage_configuration": (ProvisioningHandler, a),
            "delete_storage_configuration": (ProvisioningHandler, a),
            "list_networks": (ProvisioningHandler, a),
            "get_network": (ProvisioningHandler, a),
            "create_network": (ProvisioningHandler, a),
            "delete_network": (ProvisioningHandler, a),
            "list_vpc_endpoints": (ProvisioningHandler, a),
            "get_vpc_endpoint": (ProvisioningHandler, a),
            "create_vpc_endpoint": (ProvisioningHandler, a),
            "delete_vpc_endpoint": (ProvisioningHandler, a),
            "list_private_access_settings": (ProvisioningHandler, a),
            "get_private_access_settings": (ProvisioningHandler, a),
            "create_private_access_settings": (ProvisioningHandler, a),
            "replace_private_access_settings": (ProvisioningHandler, a),
            "delete_private_access_settings": (ProvisioningHandler, a),
            "list_encryption_keys": (ProvisioningHandler, a),
            "get_encryption_key": (ProvisioningHandler, a),
            "create_encryption_key": (ProvisioningHandler, a),
            "delete_encryption_key": (ProvisioningHandler, a),

            # Account - Settings
            "list_ip_access_lists": (SettingsHandler, a),
            "get_ip_access_list": (SettingsHandler, a),
            "create_ip_access_list": (SettingsHandler, a),
            "replace_ip_access_list": (SettingsHandler, a),
            "delete_ip_access_list": (SettingsHandler, a),

            # Account - OAuth
            "list_custom_app_integrations": (OAuthHandler, a),
            "get_custom_app_integration": (OAuthHandler, a),
            "create_custom_app_integration": (OAuthHandler, a),
            "update_custom_app_integration": (OAuthHandler, a),
            "delete_custom_app_integration": (OAuthHandler, a),
            "list_published_app_integrations": (OAuthHandler, a),
            "get_published_app_integration": (OAuthHandler, a),
            "create_published_app_integration": (OAuthHandler, a),
            "update_published_app_integration": (OAuthHandler, a),
            "delete_published_app_integration": (OAuthHandler, a),
            "list_service_principal_secrets": (OAuthHandler, a),
            "create_service_principal_secret": (OAuthHandler, a),
            "delete_service_principal_secret": (OAuthHandler, a),

            # Account - Unity Catalog
            "list_account_metastores": (AccountUnityCatalogHandler, a),
            "get_account_metastore": (AccountUnityCatalogHandler, a),
            "create_account_metastore": (AccountUnityCatalogHandler, a),
            "update_account_metastore": (AccountUnityCatalogHandler, a),
            "delete_account_metastore": (AccountUnityCatalogHandler, a),
            "list_metastore_assignments": (AccountUnityCatalogHandler, a),
            "get_metastore_assignment": (AccountUnityCatalogHandler, a),
            "create_metastore_assignment": (AccountUnityCatalogHandler, a),
            "update_metastore_assignment": (AccountUnityCatalogHandler, a),
            "delete_metastore_assignment": (AccountUnityCatalogHandler, a),
            "list_storage_credentials": (AccountUnityCatalogHandler, a),
            "get_storage_credential": (AccountUnityCatalogHandler, a),
            "create_storage_credential": (AccountUnityCatalogHandler, a),
            "update_storage_credential": (AccountUnityCatalogHandler, a),

            # SQL
            "execute_statement": (SQLHandler, w),
            "get_statement": (SQLHandler, w),
            "cancel_statement_execution": (SQLHandler, w),
            "execute_statements_batch": (SQLHandler, w),

            # Genie
            "start_genie_conversation": (GenieHandler, w),
            "create_genie_message": (GenieHandler, w),
            "get_genie_message": (GenieHandler, w),
            "get_genie_message_query_result": (GenieHandler, w),

            # Vector Search
            "list_vector_search_endpoints": (VectorSearchHandler, w),
            "get_vector_search_endpoint": (VectorSearchHandler, w),
            "list_vector_search_indexes": (VectorSearchHandler, w),
            "get_vector_search_index": (VectorSearchHandler, w),

            # Serving
            "list_serving_endpoints": (ServingHandler, w),
            "get_serving_endpoint": (ServingHandler, w),
            "query_serving_endpoint": (ServingHandler, w),

            # Models
            "list_registered_models": (ModelsHandler, w),
            "get_registered_model": (ModelsHandler, w),
            "list_model_versions": (ModelsHandler, w),
            "get_model_version": (ModelsHandler, w),

            # Feature Store
            "create_feature_table": (FeatureStoreHandler, w, fe),
            "get_feature_table": (FeatureStoreHandler, w, fe),
            "delete_feature_table": (FeatureStoreHandler, w, fe),
            "list_feature_tables": (FeatureStoreHandler, w, fe),
            "create_online_store": (FeatureStoreHandler, w, fe),
            "publish_feature_table": (FeatureStoreHandler, w, fe),
        }

        # Route to appropriate handler
        if name in handler_map:
            handler_info = handler_map[name]
            handler_class = handler_info[0]
            client = handler_info[1]

            # Feature Store handler needs both workspace and FE client
            if handler_class == FeatureStoreHandler:
                fe_client = handler_info[2]
                result = handler_class.handle(name, arguments, client, _run_operation, feature_engineering_client=fe_client)
            else:
                result = handler_class.handle(name, arguments, client, _run_operation)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Format and return result
        if result is None:
            return [TextContent(type="text", text=f"No handler found for tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except DatabricksAPIError as e:
        # Already categorized error with helpful message
        error_msg = format_error_message(e, name)
        logger.error(f"Databricks API error in {name}: {e.message}")
        return [TextContent(type="text", text=error_msg)]

    except ValueError as e:
        # Validation errors (e.g., missing required env vars)
        error_msg = format_error_message(e, name)
        logger.error(f"Validation error in {name}: {str(e)}")
        return [TextContent(type="text", text=error_msg)]

    except Exception as e:
        # Unexpected errors - categorize and format
        categorized = categorize_error(e)
        error_msg = format_error_message(categorized, name)
        logger.error(f"Unexpected error executing {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=error_msg)]


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

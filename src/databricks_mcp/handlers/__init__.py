"""
Databricks MCP Handlers
Organized by Databricks API documentation structure (docs.databricks.com/api)
"""

# Account-level handlers (docs.databricks.com/api/account)
from .account import (
    IAMHandler,
    BillingHandler,
    ProvisioningHandler,
    SettingsHandler,
    OAuthHandler,
    AccountUnityCatalogHandler,
)

# Workspace-level handlers (docs.databricks.com/api/workspace)
from .workspace import (
    # Compute
    ClustersHandler,
    # Jobs & Workflows
    JobsHandler,
    PipelinesHandler,
    # Machine Learning
    ModelsHandler,
    FeatureStoreHandler,
    ServingHandler,
    # Data Management
    WorkspaceHandler,
    DBFSHandler,
    ReposHandler,
    UnityCatalogHandler,
    # SQL & Analytics
    SQLHandler,
    WarehousesHandler,
    GenieHandler,
    # Vector Search
    VectorSearchHandler,
    # Secrets
    SecretsHandler,
)

__all__ = [
    # Account-level handlers
    "IAMHandler",
    "BillingHandler",
    "ProvisioningHandler",
    "SettingsHandler",
    "OAuthHandler",
    "AccountUnityCatalogHandler",
    # Workspace-level handlers
    "ClustersHandler",
    "JobsHandler",
    "PipelinesHandler",
    "ModelsHandler",
    "FeatureStoreHandler",
    "ServingHandler",
    "WorkspaceHandler",
    "DBFSHandler",
    "ReposHandler",
    "UnityCatalogHandler",
    "SQLHandler",
    "WarehousesHandler",
    "GenieHandler",
    "VectorSearchHandler",
    "SecretsHandler",
]

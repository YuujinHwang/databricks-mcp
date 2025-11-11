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
    InstancePoolsHandler,
    ClusterPoliciesHandler,
    # Jobs & Workflows
    JobsHandler,
    PipelinesHandler,
    # Machine Learning
    ModelsHandler,
    FeatureStoreHandler,
    ServingHandler,
    ExperimentsHandler,
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
    # Administration
    WorkspaceIAMHandler,
    WorkspaceSettingsHandler,
    WorkspaceOAuthHandler,
    # Apps
    AppsHandler,
    # Dashboards
    DashboardsHandler,
    # Sharing
    DeltaSharingHandler,
    # Governance
    DataQualityHandler,
    AssetTagsHandler,
    # Marketplace
    MarketplaceHandler,
    # Clean Rooms
    CleanRoomsHandler,
    # Agents
    AgentBricksHandler,
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
    "InstancePoolsHandler",
    "ClusterPoliciesHandler",
    "JobsHandler",
    "PipelinesHandler",
    "ModelsHandler",
    "FeatureStoreHandler",
    "ServingHandler",
    "ExperimentsHandler",
    "WorkspaceHandler",
    "DBFSHandler",
    "ReposHandler",
    "UnityCatalogHandler",
    "SQLHandler",
    "WarehousesHandler",
    "GenieHandler",
    "VectorSearchHandler",
    "SecretsHandler",
    "WorkspaceIAMHandler",
    "WorkspaceSettingsHandler",
    "WorkspaceOAuthHandler",
    "AppsHandler",
    "DashboardsHandler",
    "DeltaSharingHandler",
    "DataQualityHandler",
    "AssetTagsHandler",
    "MarketplaceHandler",
    "CleanRoomsHandler",
    "AgentBricksHandler",
]

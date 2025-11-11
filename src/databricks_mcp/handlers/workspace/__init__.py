"""
Workspace-level API Handlers
Organized according to docs.databricks.com/api/workspace structure
"""
from .compute import ClustersHandler, InstancePoolsHandler, ClusterPoliciesHandler
from .jobs import JobsHandler, PipelinesHandler
from .ml import ModelsHandler, FeatureStoreHandler, ServingHandler, ExperimentsHandler
from .data import WorkspaceHandler, DBFSHandler, ReposHandler, UnityCatalogHandler
from .sql import SQLHandler, WarehousesHandler, GenieHandler
from .vector_search import VectorSearchHandler
from .secrets import SecretsHandler
from .admin import WorkspaceIAMHandler, WorkspaceSettingsHandler, WorkspaceOAuthHandler
from .apps import AppsHandler
from .dashboards import DashboardsHandler
from .sharing import DeltaSharingHandler
from .governance import DataQualityHandler, AssetTagsHandler
from .marketplace import MarketplaceHandler
from .cleanrooms import CleanRoomsHandler
from .agents import AgentBricksHandler

__all__ = [
    # Compute
    "ClustersHandler",
    "InstancePoolsHandler",
    "ClusterPoliciesHandler",
    # Jobs & Workflows
    "JobsHandler",
    "PipelinesHandler",
    # Machine Learning
    "ModelsHandler",
    "FeatureStoreHandler",
    "ServingHandler",
    "ExperimentsHandler",
    # Data Management
    "WorkspaceHandler",
    "DBFSHandler",
    "ReposHandler",
    "UnityCatalogHandler",
    # SQL & Analytics
    "SQLHandler",
    "WarehousesHandler",
    "GenieHandler",
    # Vector Search
    "VectorSearchHandler",
    # Secrets
    "SecretsHandler",
    # Administration
    "WorkspaceIAMHandler",
    "WorkspaceSettingsHandler",
    "WorkspaceOAuthHandler",
    # Apps
    "AppsHandler",
    # Dashboards
    "DashboardsHandler",
    # Sharing
    "DeltaSharingHandler",
    # Governance
    "DataQualityHandler",
    "AssetTagsHandler",
    # Marketplace
    "MarketplaceHandler",
    # Clean Rooms
    "CleanRoomsHandler",
    # Agents
    "AgentBricksHandler",
]

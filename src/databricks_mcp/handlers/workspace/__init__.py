"""
Workspace-level API Handlers
Organized according to docs.databricks.com/api/workspace structure
"""
from .compute import ClustersHandler
from .jobs import JobsHandler, PipelinesHandler
from .ml import ModelsHandler, FeatureStoreHandler, ServingHandler
from .data import WorkspaceHandler, DBFSHandler, ReposHandler, UnityCatalogHandler
from .sql import SQLHandler, WarehousesHandler, GenieHandler
from .vector_search import VectorSearchHandler
from .secrets import SecretsHandler

__all__ = [
    # Compute
    "ClustersHandler",
    # Jobs & Workflows
    "JobsHandler",
    "PipelinesHandler",
    # Machine Learning
    "ModelsHandler",
    "FeatureStoreHandler",
    "ServingHandler",
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
]

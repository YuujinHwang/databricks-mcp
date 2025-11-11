"""
Databricks MCP Handlers
Organized by Databricks API documentation structure
"""
from .clusters import ClustersHandler
from .jobs import JobsHandler
from .workspace import WorkspaceHandler
from .dbfs import DBFSHandler
from .repos import ReposHandler
from .warehouses import WarehousesHandler
from .unity_catalog import UnityCatalogHandler
from .secrets import SecretsHandler
from .pipelines import PipelinesHandler
from .sql import SQLHandler
from .genie import GenieHandler
from .vector_search import VectorSearchHandler
from .serving import ServingHandler
from .models import ModelsHandler
from .feature_store import FeatureStoreHandler

# Account-level handlers
from .account import (
    IAMHandler,
    BillingHandler,
    ProvisioningHandler,
    SettingsHandler,
    OAuthHandler,
    AccountUnityCatalogHandler,
)

__all__ = [
    "ClustersHandler",
    "JobsHandler",
    "WorkspaceHandler",
    "DBFSHandler",
    "ReposHandler",
    "WarehousesHandler",
    "UnityCatalogHandler",
    "SecretsHandler",
    "PipelinesHandler",
    "SQLHandler",
    "GenieHandler",
    "VectorSearchHandler",
    "ServingHandler",
    "ModelsHandler",
    "FeatureStoreHandler",
    # Account-level handlers
    "IAMHandler",
    "BillingHandler",
    "ProvisioningHandler",
    "SettingsHandler",
    "OAuthHandler",
    "AccountUnityCatalogHandler",
]

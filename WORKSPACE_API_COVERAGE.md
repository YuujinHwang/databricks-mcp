# Workspace API Coverage Analysis

Based on Databricks SDK workspace API categories from:
https://github.com/databricks/databricks-sdk-py/tree/main/docs/workspace

## Current Coverage: 12/27 categories (44%)

### ✅ Implemented (12 categories)

1. **catalog** → `workspace/data/unity_catalog.py` (13 tools)
2. **compute** → `workspace/compute/clusters.py` (8 tools) - PARTIAL
3. **files** → `workspace/data/workspace.py, dbfs.py, repos.py` (13 tools)
4. **jobs** → `workspace/jobs/jobs.py` (9 tools)
5. **ml** → `workspace/ml/models.py, feature_store.py, serving.py` (13 tools) - PARTIAL
6. **pipelines** → `workspace/jobs/pipelines.py` (4 tools)
7. **serving** → `workspace/ml/serving.py` (3 tools)
8. **sql** → `workspace/sql/sql.py, warehouses.py, genie.py` (13 tools)
9. **vectorsearch** → `workspace/vector_search/vector_search.py` (4 tools)
10. **workspace** → `workspace/data/workspace.py` (5 tools)
11. **aibuilder** → `workspace/sql/genie.py` (4 tools) - Genie/AI-BI
12. **secrets** → `workspace/secrets/secrets.py` (8 tools) - Not in SDK docs but implemented

**Total: 96 tools**

---

### ❌ Missing (15 categories) - 0 tools

#### High Priority (User-facing features)

1. **apps** - Databricks Apps management
   - Create, deploy, manage Databricks Apps
   - APIs: create, delete, deploy, get, list, start, stop, update

2. **iam** - Workspace-level Identity & Access Management
   - Permissions, groups, users, service principals, current user
   - APIs: permissions CRUD, group/user management, workspace assignment

3. **settings** / **settingsv2** - Workspace configuration
   - IP access lists, tokens, global init scripts, workspace config
   - APIs: token management, IP lists, workspace settings, compliance security

4. **dashboards** - Lakeview Dashboards (different from legacy dashboards)
   - Create, manage Lakeview dashboards
   - APIs: create, delete, get, get_published, list, publish, unpublish, update

5. **sharing** - Delta Sharing (workspace-level)
   - Recipient management, share management
   - APIs: recipients (create, delete, get, list, rotate_token, share_permissions, update)
   - APIs: shares (create, delete, get, list, update, share_permissions)

6. **marketplace** - Databricks Marketplace
   - Consumer fulfillments, installations, listings, providers
   - APIs: list, get, batch_get fulfillments/installations/listings

#### Medium Priority (Governance & Quality)

7. **dataquality** / **qualitymonitorv2** - Data Quality Monitoring
   - Monitor data quality for Unity Catalog tables/schemas
   - APIs: create, delete, get, list, run, update monitors
   - APIs: refresh schedules, inspection results

8. **tags** - Asset tagging (Unity Catalog entity tags)
   - Tag management for governance
   - APIs: create, delete, list, update tags

9. **cleanrooms** - Clean Rooms for data collaboration
   - Secure data collaboration APIs
   - APIs: create, delete, get, list, update clean rooms
   - Output catalogs management

10. **oauth2** - Workspace-level OAuth
    - Custom app integration at workspace level
    - Different from account-level OAuth

#### Low Priority (Advanced/Specialized)

11. **agentbricks** - Agent framework (new)
    - AI agent orchestration
    - APIs: TBD (new feature)

12. **database** - Database-related APIs
    - May overlap with catalog APIs
    - Need further investigation

13. **iamv2** - IAM v2 APIs
    - Next-generation IAM APIs
    - May supersede iam APIs

14. **provisioning** - Workspace-level provisioning
    - Different from account-level provisioning
    - Need further investigation

15. **compute** - INCOMPLETE (only clusters implemented)
    - **Missing**: Instance Pools, Cluster Policies, Policy Families
    - Instance Pools: create, delete, edit, get, list
    - Cluster Policies: create, delete, edit, get, list
    - Policy Families: get, list

---

## Detailed Gap Analysis

### Compute Category - INCOMPLETE
**Current**: 8 tools (clusters only)
**Missing**: ~15 tools
- Instance Pools (5 tools): create, delete, edit, get, list
- Cluster Policies (5 tools): create, delete, edit, get, list
- Policy Families (2 tools): get, list
- Libraries (3 tools): all_cluster_statuses, cluster_status, install

### ML Category - INCOMPLETE
**Current**: 13 tools (models, feature_store, serving)
**Missing**: ~25 tools
- MLflow Experiments (7 tools): create, delete, get, list, restore, search, update
- MLflow Runs (8 tools): create, delete, get, list, log_batch, log_metric, search, update
- Model Registry v2 (5 tools): Additional registry APIs
- Online Tables (5 tools): create, delete, get, list, sync

### Settings Category - MISSING
**Estimated**: ~30 tools
- Tokens (5 tools): create, delete, get, list
- IP Access Lists (5 tools): create, delete, get, list, replace, update
- Global Init Scripts (5 tools): create, delete, get, list, update
- Workspace Config (5 tools): get, set, delete various settings
- Automatic Cluster Update (3 tools): get, set
- ESM Enablement (3 tools): get, set
- Compliance Security Profile (4 tools): get, set

### IAM Category - MISSING
**Estimated**: ~35 tools
- Permissions (8 tools): get, set, update for various object types
- Groups (5 tools): create, delete, get, list, update
- Users (5 tools): create, delete, get, list, update
- Service Principals (5 tools): create, delete, get, list, update
- Current User (2 tools): get (me)
- Workspace Assignment (5 tools): delete, get, list, update
- Account Access Control Proxy (5 tools)

### Dashboards Category - MISSING
**Estimated**: ~8 tools
- create, delete, get, get_published, list, publish, unpublish, update

### Delta Sharing Category - MISSING
**Estimated**: ~15 tools
- Recipients (7 tools): create, delete, get, list, rotate_token, share_permissions, update
- Shares (8 tools): create, delete, get, list, update, share_permissions

### Apps Category - MISSING
**Estimated**: ~10 tools
- create, delete, deploy, get, get_deployment, get_environment, list, start, stop, update

### Data Quality Category - MISSING
**Estimated**: ~12 tools
- Monitors (6 tools): create, delete, get, list, run, update
- Refresh Schedules (3 tools): get, list, update
- Inspection Results (3 tools): list

### Marketplace Category - MISSING
**Estimated**: ~12 tools
- Fulfillments (4 tools): batch_get, get, list
- Installations (4 tools): create, delete, list, update
- Listings (4 tools): batch_get, get, list

### Tags Category - MISSING
**Estimated**: ~5 tools
- create, delete, list, update

### Clean Rooms Category - MISSING
**Estimated**: ~8 tools
- create, delete, get, list, update
- Output catalogs (3 tools)

---

## Total Estimated Tools

| Status | Categories | Estimated Tools |
|--------|-----------|-----------------|
| ✅ Implemented | 12 | **96** |
| 🟡 Incomplete | 2 (compute, ml) | 40 missing |
| ❌ Missing | 15 | ~180 missing |
| **TOTAL** | **27** | **~316 tools** |

## Current Coverage: **30%** (96/316 tools)

---

## Recommended Implementation Priority

### Phase 1 (High Impact) - ~80 tools
1. **iam** - Workspace permissions & identity (35 tools)
2. **settings** - Tokens, IP lists, workspace config (30 tools)
3. **compute** - Complete with instance pools & policies (15 tools)

### Phase 2 (Data Collaboration) - ~45 tools
4. **apps** - Databricks Apps (10 tools)
5. **dashboards** - Lakeview dashboards (8 tools)
6. **sharing** - Delta Sharing (15 tools)
7. **ml** - Complete MLflow (12 tools)

### Phase 3 (Governance) - ~37 tools
8. **dataquality** - Data quality monitoring (12 tools)
9. **tags** - Asset tagging (5 tools)
10. **marketplace** - Marketplace integration (12 tools)
11. **oauth2** - Workspace OAuth (8 tools)

### Phase 4 (Advanced) - ~18 tools
12. **cleanrooms** - Clean rooms (8 tools)
13. **agentbricks** - Agent framework (5 tools)
14. **database** - Database APIs (3 tools)
15. **iamv2** - IAM v2 (2 tools)

---

## Next Steps

1. ✅ Complete directory structure reorganization
2. ⏭️ Create handlers for Phase 1 (iam, settings, compute completion)
3. ⏭️ Add Phase 2 handlers (apps, dashboards, sharing, ml completion)
4. ⏭️ Add Phase 3 handlers (governance & quality)
5. ⏭️ Add Phase 4 handlers (advanced features)

**Target**: 90%+ coverage (~285/316 tools)

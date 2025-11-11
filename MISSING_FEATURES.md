# Missing Features Analysis

## Account API - Missing Categories

### 1. **Identity and Access Management** (부분 구현)
#### ✅ Implemented:
- Account Groups (list, get)
- Account Service Principals (list)
- Account Users (list, get)

#### ❌ Missing:
- **Account Access Control** (Public preview)
  - Manage account-level access control lists
- **Workspace Assignment**
  - Assign workspaces to users/groups
  - Manage workspace permissions
- **IAM V2 Beta**
  - New IAM features
- **Service Principal enhancements**
  - create_account_service_principal
  - update_account_service_principal
  - delete_account_service_principal
- **User enhancements**
  - create_account_user
  - update_account_user
  - delete_account_user
- **Group enhancements**
  - create_account_group
  - update_account_group
  - delete_account_group

### 2. **Unity Catalog** (부분 구현)
#### ✅ Implemented:
- Account Metastores (list, get)

#### ❌ Missing:
- **Account Metastore Assignments**
  - Assign metastores to workspaces
  - Manage metastore workspace assignments
- **Account Storage Credentials**
  - Manage storage credentials at account level
  - Create/update/delete storage credentials
- **Metastore enhancements**
  - create_account_metastore
  - update_account_metastore
  - delete_account_metastore

### 3. **Settings** (전체 누락)
❌ **Account IP Access Lists**
  - Manage account-level IP allowlists
  - Create/update/delete IP access lists

❌ **Account Settings**
  - Manage account-wide settings
  - Configure default settings

❌ **Network Connectivity**
  - Manage network connectivity configurations
  - Private link settings

❌ **Network Policies**
  - Create/manage network policies
  - Configure network security

❌ **Settings API V2 Beta**
  - New settings API features

❌ **Workspace Network Option**
  - Configure workspace network options

### 4. **Provisioning** (부분 구현)
#### ✅ Implemented:
- Workspaces (list, get)

#### ❌ Missing:
- **Credential configurations**
  - Manage cloud credentials
  - AWS/Azure/GCP credential setup

- **Key configurations**
  - Manage encryption keys
  - Customer-managed keys (CMK)

- **Network configurations**
  - VPC/VNet configurations
  - Network setup for workspaces

- **Private Access Settings**
  - Configure private endpoint settings
  - Private Link configurations

- **Storage configurations**
  - Root storage bucket/container setup
  - DBFS root configuration

- **VPC Endpoint Configurations**
  - Manage VPC endpoints
  - Private connectivity setup

- **Workspace enhancements**
  - create_account_workspace
  - update_account_workspace
  - delete_account_workspace

### 5. **Billing** (전체 누락) 🔥 HIGH PRIORITY
❌ **Billable usage download**
  - Download billable usage data
  - Query usage by date range

❌ **Return billable usage logs**
  - Get detailed usage logs
  - Analyze consumption patterns

❌ **Budget Policy** (Public preview)
  - Create budget policies
  - Set spending limits

❌ **Log delivery configurations**
  - Configure usage log delivery
  - Set up log destinations

❌ **Usage Dashboards** (Public preview)
  - Manage usage dashboards
  - Visualize spending

❌ **Budgets** (Public preview)
  - Create/manage budgets
  - Budget alerts and notifications

### 6. **OAuth** (전체 누락)
❌ **Account Federation Policies**
  - Manage SSO/SAML configurations
  - Identity provider setup

❌ **OAuth Custom App Integration**
  - Custom OAuth applications
  - Third-party integrations

❌ **OAuth Published App**
  - Manage published OAuth apps
  - App marketplace

❌ **OAuth Published App Integration**
  - Integration with published apps

❌ **Service Principal Federation Policies**
  - Federation for service principals
  - SP identity configurations

❌ **Service Principal Secrets**
  - Manage SP secrets and credentials
  - Secret rotation

---

## Workspace API - Missing Features

### Current Implementation (5 tools)
- list_workspace_objects
- get_workspace_object_status
- export_workspace_object
- delete_workspace_object
- mkdirs

### Need to Research:
- Import workspace objects
- Update workspace objects
- Workspace ACL management
- Workspace-level settings
- Token management (if applicable)

---

## Summary Statistics

### Account API Coverage
- **Implemented**: 9 tools across 3 categories
- **Missing**: ~50+ tools across 6 major categories
- **Coverage**: ~15% (estimated)

### Priority Recommendations

#### 🔴 **HIGH PRIORITY** (Most Requested)
1. **Billing APIs** - Usage and cost tracking
2. **Workspace Management** - Create/update/delete workspaces
3. **User Management** - CRUD operations for users/groups/SPs

#### 🟡 **MEDIUM PRIORITY** (Infrastructure)
4. **Network Configurations** - VPC, private link setup
5. **Storage Configurations** - Root storage management
6. **IP Access Lists** - Security controls

#### 🟢 **LOW PRIORITY** (Advanced/Preview)
7. **OAuth & Federation** - Advanced identity features
8. **Settings API V2** - Beta features
9. **Account Access Control** - Preview features

---

## Next Steps

1. **Immediate**: Implement Billing APIs (most requested by user)
2. **Phase 2**: Complete CRUD operations for Users/Groups/SPs
3. **Phase 3**: Workspace provisioning (create/update/delete)
4. **Phase 4**: Network and security configurations
5. **Phase 5**: Advanced OAuth and federation features

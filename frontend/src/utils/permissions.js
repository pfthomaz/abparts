// frontend/src/utils/permissions.js

/**
 * User roles enum
 */
export const USER_ROLES = {
  USER: 'user',
  ADMIN: 'admin',
  SUPER_ADMIN: 'super_admin'
};

/**
 * Organization types enum
 */
export const ORGANIZATION_TYPES = {
  ORASEAS_EE: 'oraseas_ee',
  BOSSAQUA: 'bossaqua',
  CUSTOMER: 'customer',
  SUPPLIER: 'supplier'
};

/**
 * Permission definitions based on user roles and organization context
 */
export const PERMISSIONS = {
  // Organization management
  VIEW_ALL_ORGANIZATIONS: 'view_all_organizations',
  MANAGE_ORGANIZATIONS: 'manage_organizations',
  VIEW_OWN_ORGANIZATION: 'view_own_organization',

  // User management
  MANAGE_ALL_USERS: 'manage_all_users',
  MANAGE_ORG_USERS: 'manage_org_users',
  INVITE_USERS: 'invite_users',
  VIEW_USER_AUDIT_LOGS: 'view_user_audit_logs',

  // Warehouse management
  MANAGE_WAREHOUSES: 'manage_warehouses',
  VIEW_WAREHOUSES: 'view_warehouses',

  // Inventory management
  ADJUST_INVENTORY: 'adjust_inventory',
  VIEW_INVENTORY: 'view_inventory',
  TRANSFER_INVENTORY: 'transfer_inventory',

  // Parts management
  MANAGE_PARTS: 'manage_parts',
  VIEW_PARTS: 'view_parts',
  ORDER_PARTS: 'order_parts',
  RECEIVE_PARTS: 'receive_parts',
  RECORD_PART_USAGE: 'record_part_usage',

  // Machine management
  REGISTER_MACHINES: 'register_machines',
  VIEW_ALL_MACHINES: 'view_all_machines',
  VIEW_ORG_MACHINES: 'view_org_machines',

  // Transaction management
  VIEW_ALL_TRANSACTIONS: 'view_all_transactions',
  VIEW_ORG_TRANSACTIONS: 'view_org_transactions',

  // Supplier management
  MANAGE_SUPPLIERS: 'manage_suppliers',
  VIEW_SUPPLIERS: 'view_suppliers',

  // Reporting and analytics
  VIEW_GLOBAL_REPORTS: 'view_global_reports',
  VIEW_ORG_REPORTS: 'view_org_reports',

  // System administration
  VIEW_SYSTEM_LOGS: 'view_system_logs',
  MANAGE_SYSTEM_SETTINGS: 'manage_system_settings'
};

/**
 * Role-based permission mapping
 */
const ROLE_PERMISSIONS = {
  [USER_ROLES.SUPER_ADMIN]: [
    // Super admin has all permissions
    ...Object.values(PERMISSIONS)
  ],

  [USER_ROLES.ADMIN]: [
    // Admin permissions within their organization
    PERMISSIONS.VIEW_OWN_ORGANIZATION,
    PERMISSIONS.MANAGE_ORG_USERS,
    PERMISSIONS.INVITE_USERS,
    PERMISSIONS.VIEW_USER_AUDIT_LOGS,
    PERMISSIONS.MANAGE_WAREHOUSES,
    PERMISSIONS.VIEW_WAREHOUSES,
    PERMISSIONS.ADJUST_INVENTORY,
    PERMISSIONS.VIEW_INVENTORY,
    PERMISSIONS.TRANSFER_INVENTORY,
    PERMISSIONS.MANAGE_PARTS,
    PERMISSIONS.VIEW_PARTS,
    PERMISSIONS.ORDER_PARTS,
    PERMISSIONS.RECEIVE_PARTS,
    PERMISSIONS.RECORD_PART_USAGE,
    PERMISSIONS.VIEW_ORG_MACHINES,
    PERMISSIONS.VIEW_ORG_TRANSACTIONS,
    PERMISSIONS.MANAGE_SUPPLIERS,
    PERMISSIONS.VIEW_SUPPLIERS,
    PERMISSIONS.VIEW_ORG_REPORTS
  ],

  [USER_ROLES.USER]: [
    // Basic user permissions
    PERMISSIONS.VIEW_OWN_ORGANIZATION,
    PERMISSIONS.VIEW_WAREHOUSES,
    PERMISSIONS.VIEW_INVENTORY,
    PERMISSIONS.VIEW_PARTS,
    PERMISSIONS.ORDER_PARTS,
    PERMISSIONS.RECEIVE_PARTS,
    PERMISSIONS.RECORD_PART_USAGE,
    PERMISSIONS.VIEW_ORG_MACHINES,
    PERMISSIONS.VIEW_ORG_TRANSACTIONS,
    PERMISSIONS.VIEW_SUPPLIERS,
    PERMISSIONS.VIEW_ORG_REPORTS
  ]
};

/**
 * Check if user has a specific permission
 * @param {Object} user - User object with role and organization info
 * @param {string} permission - Permission to check
 * @returns {boolean} - Whether user has the permission
 */
export const hasPermission = (user, permission) => {
  if (!user || !user.role) {
    return false;
  }

  const userPermissions = ROLE_PERMISSIONS[user.role] || [];
  return userPermissions.includes(permission);
};

/**
 * Check if user has any of the specified permissions
 * @param {Object} user - User object with role and organization info
 * @param {string[]} permissions - Array of permissions to check
 * @returns {boolean} - Whether user has any of the permissions
 */
export const hasAnyPermission = (user, permissions) => {
  return permissions.some(permission => hasPermission(user, permission));
};

/**
 * Check if user has all of the specified permissions
 * @param {Object} user - User object with role and organization info
 * @param {string[]} permissions - Array of permissions to check
 * @returns {boolean} - Whether user has all of the permissions
 */
export const hasAllPermissions = (user, permissions) => {
  return permissions.every(permission => hasPermission(user, permission));
};

/**
 * Get all permissions for a user role
 * @param {string} role - User role
 * @returns {string[]} - Array of permissions
 */
export const getPermissionsForRole = (role) => {
  return ROLE_PERMISSIONS[role] || [];
};

/**
 * Check if user is super admin
 * @param {Object} user - User object
 * @returns {boolean} - Whether user is super admin
 */
export const isSuperAdmin = (user) => {
  return user && user.role === USER_ROLES.SUPER_ADMIN;
};

/**
 * Check if user is admin (including super admin)
 * @param {Object} user - User object
 * @returns {boolean} - Whether user is admin or super admin
 */
export const isAdmin = (user) => {
  return user && (user.role === USER_ROLES.ADMIN || user.role === USER_ROLES.SUPER_ADMIN);
};

/**
 * Check if user can access cross-organization data
 * @param {Object} user - User object
 * @returns {boolean} - Whether user can access cross-organization data
 */
export const canAccessCrossOrganization = (user) => {
  return isSuperAdmin(user);
};

/**
 * Check if user can manage other users
 * @param {Object} user - User object
 * @param {Object} targetUser - Target user to manage (optional)
 * @returns {boolean} - Whether user can manage the target user
 */
export const canManageUser = (user, targetUser = null) => {
  if (isSuperAdmin(user)) {
    return true;
  }

  if (isAdmin(user)) {
    // Admin can manage users in their organization
    if (!targetUser) return true;
    return user.organization_id === targetUser.organization_id;
  }

  return false;
};

/**
 * Check if user can view specific organization data
 * @param {Object} user - User object
 * @param {string} organizationId - Organization ID to check access for
 * @returns {boolean} - Whether user can view the organization data
 */
export const canViewOrganization = (user, organizationId) => {
  if (isSuperAdmin(user)) {
    return true;
  }

  return user && user.organization_id === organizationId;
};

/**
 * Get navigation items based on user permissions
 * @param {Object} user - User object
 * @returns {Array} - Array of navigation items the user can access
 */
export const getNavigationItems = (user) => {
  const items = [];

  // Return empty array for null/undefined users
  if (!user) {
    return items;
  }

  // Dashboard - available to all authenticated users
  items.push({
    name: 'dashboard',
    path: '/',
    label: 'Dashboard',
    icon: 'dashboard',
    permission: null,
    description: 'Overview of system metrics and status',
    category: 'core'
  });

  // Organizations - super admin only
  if (hasPermission(user, PERMISSIONS.VIEW_ALL_ORGANIZATIONS)) {
    items.push({
      name: 'organizations',
      path: '/organizations',
      label: 'Organizations',
      icon: 'organizations',
      permission: PERMISSIONS.VIEW_ALL_ORGANIZATIONS,
      description: 'Manage organization hierarchy and relationships',
      adminOnly: true,
      category: 'administration',
      accessScope: 'global'
    });
  }

  // Organization Management - admin and above
  if (hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.VIEW_ALL_ORGANIZATIONS)) {
    items.push({
      name: 'organizationManagement',
      path: '/organization-management',
      label: 'Organization Management',
      icon: 'organization-management',
      permission: PERMISSIONS.MANAGE_ORG_USERS,
      description: 'Enhanced organization, supplier, and warehouse management',
      adminOnly: true,
      category: 'administration',
      accessScope: hasPermission(user, PERMISSIONS.VIEW_ALL_ORGANIZATIONS) ? 'global' : 'organization'
    });
  }

  // Parts - all users can view
  if (hasPermission(user, PERMISSIONS.VIEW_PARTS)) {
    items.push({
      name: 'parts',
      path: '/parts',
      label: 'Parts',
      icon: 'parts',
      permission: PERMISSIONS.VIEW_PARTS,
      description: 'Browse and manage parts catalog',
      category: 'core',
      accessScope: isSuperAdmin(user) ? 'global' : 'organization'
    });
  }

  // Inventory menu removed - functionality consolidated into Warehouses page

  // Orders - all users can view/create
  if (hasPermission(user, PERMISSIONS.ORDER_PARTS)) {
    items.push({
      name: 'orders',
      path: '/orders',
      label: 'Orders',
      icon: 'orders',
      permission: PERMISSIONS.ORDER_PARTS,
      description: 'Create and track part orders',
      category: 'core',
      accessScope: isSuperAdmin(user) ? 'global' : 'organization'
    });
  }

  // Stocktake - admin and above
  if (hasPermission(user, PERMISSIONS.ADJUST_INVENTORY)) {
    items.push({
      name: 'stocktake',
      path: '/stocktake',
      label: 'Stocktake',
      icon: 'stocktake',
      permission: PERMISSIONS.ADJUST_INVENTORY,
      description: 'Perform inventory adjustments and stocktakes',
      adminOnly: true,
      category: 'inventory',
      accessScope: isSuperAdmin(user) ? 'global' : 'organization'
    });
  }

  // Stock Adjustments - admin and above
  if (hasPermission(user, PERMISSIONS.ADJUST_INVENTORY)) {
    items.push({
      name: 'stockAdjustments',
      path: '/stock-adjustments',
      label: 'Stock Adjustments',
      icon: 'stock-adjustments',
      permission: PERMISSIONS.ADJUST_INVENTORY,
      description: 'Record and track inventory adjustments',
      adminOnly: true,
      category: 'inventory',
      accessScope: isSuperAdmin(user) ? 'global' : 'organization'
    });
  }

  // Maintenance Protocols - super admin only
  if (isSuperAdmin(user)) {
    items.push({
      name: 'maintenanceProtocols',
      path: '/maintenance-protocols',
      label: 'Maintenance Protocols',
      icon: 'maintenance',
      permission: null,
      description: 'Manage maintenance protocol templates',
      adminOnly: true,
      superAdminOnly: true,
      category: 'administration',
      accessScope: 'global'
    });
  }

  // Maintenance Executions - all users can execute maintenance
  items.push({
    name: 'maintenance',
    path: '/maintenance-executions',
    label: 'Maintenance',
    icon: 'maintenance',
    permission: null,
    description: 'Perform and track maintenance',
    category: 'operations',
    accessScope: 'organization'
  });

  // Machines - all users can view their org's machines
  if (hasPermission(user, PERMISSIONS.VIEW_ORG_MACHINES) || hasPermission(user, PERMISSIONS.VIEW_ALL_MACHINES)) {
    items.push({
      name: 'machines',
      path: '/machines',
      label: 'Machines',
      icon: 'machines',
      permission: PERMISSIONS.VIEW_ORG_MACHINES,
      description: 'View and manage AutoBoss machines',
      category: 'operations',
      accessScope: hasPermission(user, PERMISSIONS.VIEW_ALL_MACHINES) ? 'global' : 'organization'
    });
  }

  // Users - admin and above
  if (hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS)) {
    items.push({
      name: 'users',
      path: '/users',
      label: 'Users',
      icon: 'users',
      permission: PERMISSIONS.MANAGE_ORG_USERS,
      description: 'Manage users and permissions',
      adminOnly: true,
      category: 'administration',
      accessScope: hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS) ? 'global' : 'organization'
    });
  }

  // Warehouses - admin and above (if they have warehouse management permissions)
  if (hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES)) {
    items.push({
      name: 'warehouses',
      path: '/warehouses',
      label: 'Warehouses',
      icon: 'warehouses',
      permission: PERMISSIONS.MANAGE_WAREHOUSES,
      description: 'Manage warehouse locations and settings',
      adminOnly: true,
      category: 'core',
      accessScope: isSuperAdmin(user) ? 'global' : 'organization'
    });
  }

  // Transactions - all users can view their org's transactions
  if (hasPermission(user, PERMISSIONS.VIEW_ORG_TRANSACTIONS)) {
    items.push({
      name: 'transactions',
      path: '/transactions',
      label: 'Transactions',
      icon: 'transactions',
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS,
      description: 'View and manage transaction history',
      category: 'operations',
      accessScope: hasPermission(user, PERMISSIONS.VIEW_ALL_TRANSACTIONS) ? 'global' : 'organization'
    });
  }

  // Configuration - admin and above
  if (user.role === USER_ROLES.ADMIN || user.role === USER_ROLES.SUPER_ADMIN) {
    items.push({
      name: 'configuration',
      path: '/configuration',
      label: 'Configuration',
      icon: 'configuration',
      permission: null, // Role-based access handled in component
      description: 'Administrative configuration panel',
      adminOnly: true,
      category: 'administration',
      accessScope: user.role === USER_ROLES.SUPER_ADMIN ? 'global' : 'organization'
    });
  }

  return items;
};

/**
 * Feature flags based on user permissions
 * @param {Object} user - User object
 * @returns {Object} - Object with feature flags
 */
export const getFeatureFlags = (user) => {
  return {
    canCreateOrganizations: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
    canEditOrganizations: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
    canDeleteOrganizations: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),

    canInviteUsers: hasPermission(user, PERMISSIONS.INVITE_USERS),
    canManageUsers: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
    canViewUserAuditLogs: hasPermission(user, PERMISSIONS.VIEW_USER_AUDIT_LOGS),

    canCreateWarehouses: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
    canEditWarehouses: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
    canDeleteWarehouses: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),

    canAdjustInventory: hasPermission(user, PERMISSIONS.ADJUST_INVENTORY),
    canTransferInventory: hasPermission(user, PERMISSIONS.TRANSFER_INVENTORY),

    canCreateParts: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
    canEditParts: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
    canDeleteParts: hasPermission(user, PERMISSIONS.MANAGE_PARTS),

    canRegisterMachines: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
    canViewAllMachines: hasPermission(user, PERMISSIONS.VIEW_ALL_MACHINES),

    canViewAllTransactions: hasPermission(user, PERMISSIONS.VIEW_ALL_TRANSACTIONS),
    canViewGlobalReports: hasPermission(user, PERMISSIONS.VIEW_GLOBAL_REPORTS),

    canManageSuppliers: hasPermission(user, PERMISSIONS.MANAGE_SUPPLIERS),

    canViewSystemLogs: hasPermission(user, PERMISSIONS.VIEW_SYSTEM_LOGS),
    canManageSystemSettings: hasPermission(user, PERMISSIONS.MANAGE_SYSTEM_SETTINGS)
  };
};

/**
 * Get user's data access scope information
 * @param {Object} user - User object
 * @returns {Object} - Object with access scope details
 */
export const getAccessScope = (user) => {
  const isSuper = isSuperAdmin(user);

  return {
    canAccessAllOrganizations: isSuper,
    canAccessOwnOrganization: true,
    canAccessCrossOrganizationData: isSuper,
    organizationId: user?.organization_id,
    organizationName: user?.organization?.name,
    accessLevel: isSuper ? 'global' : 'organization',
    canViewGlobalReports: hasPermission(user, PERMISSIONS.VIEW_GLOBAL_REPORTS),
    canViewOrgReports: hasPermission(user, PERMISSIONS.VIEW_ORG_REPORTS),
    canManageAllUsers: hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
    canManageOrgUsers: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS),
    restrictions: {
      dataFiltering: !isSuper ? 'organization-scoped' : 'none',
      userManagement: isSuper ? 'all-organizations' : 'own-organization',
      reporting: isSuper ? 'global' : 'organization-only'
    }
  };
};

/**
 * Get contextual permissions for a specific feature/page
 * @param {Object} user - User object
 * @param {string} feature - Feature name (e.g., 'inventory', 'users', 'machines')
 * @returns {Object} - Object with contextual permissions
 */
export const getContextualPermissions = (user, feature) => {
  const basePermissions = {
    canView: false,
    canCreate: false,
    canEdit: false,
    canDelete: false,
    canManage: false,
    accessScope: 'none'
  };

  const accessScope = getAccessScope(user);

  switch (feature) {
    case 'organizations':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_ALL_ORGANIZATIONS),
        canCreate: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
        canEdit: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
        canDelete: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
        canManage: hasPermission(user, PERMISSIONS.MANAGE_ORGANIZATIONS),
        accessScope: 'global'
      };

    case 'users':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
        canCreate: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
        canEdit: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
        canDelete: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
        canManage: hasPermission(user, PERMISSIONS.MANAGE_ORG_USERS) || hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS),
        canInvite: hasPermission(user, PERMISSIONS.INVITE_USERS),
        canViewAuditLogs: hasPermission(user, PERMISSIONS.VIEW_USER_AUDIT_LOGS),
        accessScope: hasPermission(user, PERMISSIONS.MANAGE_ALL_USERS) ? 'global' : 'organization'
      };

    case 'inventory':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_INVENTORY),
        canCreate: hasPermission(user, PERMISSIONS.ADJUST_INVENTORY),
        canEdit: hasPermission(user, PERMISSIONS.ADJUST_INVENTORY),
        canDelete: hasPermission(user, PERMISSIONS.ADJUST_INVENTORY),
        canManage: hasPermission(user, PERMISSIONS.ADJUST_INVENTORY),
        canTransfer: hasPermission(user, PERMISSIONS.TRANSFER_INVENTORY),
        accessScope: accessScope.accessLevel
      };

    case 'parts':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_PARTS),
        canCreate: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
        canEdit: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
        canDelete: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
        canManage: hasPermission(user, PERMISSIONS.MANAGE_PARTS),
        canOrder: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canReceive: hasPermission(user, PERMISSIONS.RECEIVE_PARTS),
        canRecordUsage: hasPermission(user, PERMISSIONS.RECORD_PART_USAGE),
        accessScope: accessScope.accessLevel
      };

    case 'machines':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_ORG_MACHINES) || hasPermission(user, PERMISSIONS.VIEW_ALL_MACHINES),
        canCreate: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
        canEdit: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
        canDelete: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
        canManage: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
        canRegister: hasPermission(user, PERMISSIONS.REGISTER_MACHINES),
        accessScope: hasPermission(user, PERMISSIONS.VIEW_ALL_MACHINES) ? 'global' : 'organization'
      };

    case 'warehouses':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_WAREHOUSES),
        canCreate: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
        canEdit: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
        canDelete: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
        canManage: hasPermission(user, PERMISSIONS.MANAGE_WAREHOUSES),
        accessScope: accessScope.accessLevel
      };

    case 'orders':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canCreate: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canEdit: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canDelete: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canManage: hasPermission(user, PERMISSIONS.ORDER_PARTS),
        canReceive: hasPermission(user, PERMISSIONS.RECEIVE_PARTS),
        accessScope: accessScope.accessLevel
      };

    case 'suppliers':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_SUPPLIERS),
        canCreate: hasPermission(user, PERMISSIONS.MANAGE_SUPPLIERS),
        canEdit: hasPermission(user, PERMISSIONS.MANAGE_SUPPLIERS),
        canDelete: hasPermission(user, PERMISSIONS.MANAGE_SUPPLIERS),
        canManage: hasPermission(user, PERMISSIONS.MANAGE_SUPPLIERS),
        accessScope: accessScope.accessLevel
      };

    case 'transactions':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_ORG_TRANSACTIONS) || hasPermission(user, PERMISSIONS.VIEW_ALL_TRANSACTIONS),
        accessScope: hasPermission(user, PERMISSIONS.VIEW_ALL_TRANSACTIONS) ? 'global' : 'organization'
      };

    case 'reports':
      return {
        ...basePermissions,
        canView: hasPermission(user, PERMISSIONS.VIEW_ORG_REPORTS) || hasPermission(user, PERMISSIONS.VIEW_GLOBAL_REPORTS),
        canViewGlobal: hasPermission(user, PERMISSIONS.VIEW_GLOBAL_REPORTS),
        canViewOrganization: hasPermission(user, PERMISSIONS.VIEW_ORG_REPORTS),
        accessScope: hasPermission(user, PERMISSIONS.VIEW_GLOBAL_REPORTS) ? 'global' : 'organization'
      };

    default:
      return basePermissions;
  }
};

/**
 * Check if user can perform a specific action on a resource
 * @param {Object} user - User object
 * @param {string} action - Action to perform (view, create, edit, delete)
 * @param {string} resource - Resource type
 * @param {Object} resourceData - Optional resource data for context
 * @returns {boolean} - Whether user can perform the action
 */
export const canPerformAction = (user, action, resource, resourceData = null) => {
  const permissions = getContextualPermissions(user, resource);

  switch (action) {
    case 'view':
      return permissions.canView;
    case 'create':
      return permissions.canCreate;
    case 'edit':
      return permissions.canEdit;
    case 'delete':
      return permissions.canDelete;
    case 'manage':
      return permissions.canManage;
    default:
      return false;
  }
};

/**
 * Get UI configuration based on user permissions
 * @param {Object} user - User object
 * @returns {Object} - UI configuration object
 */
export const getUIConfiguration = (user) => {
  const accessScope = getAccessScope(user);
  const featureFlags = getFeatureFlags(user);

  return {
    showGlobalFilters: accessScope.canAccessAllOrganizations,
    showOrganizationSelector: accessScope.canAccessAllOrganizations,
    showAdvancedFeatures: isAdmin(user),
    showSystemAdminFeatures: isSuperAdmin(user),
    defaultDataScope: accessScope.accessLevel,
    availableActions: {
      canCreateOrganizations: featureFlags.canCreateOrganizations,
      canInviteUsers: featureFlags.canInviteUsers,
      canManageWarehouses: featureFlags.canCreateWarehouses,
      canAdjustInventory: featureFlags.canAdjustInventory,
      canRegisterMachines: featureFlags.canRegisterMachines,
      canViewSystemLogs: featureFlags.canViewSystemLogs
    },
    navigationCategories: {
      core: true,
      inventory: hasPermission(user, PERMISSIONS.VIEW_INVENTORY),
      operations: hasPermission(user, PERMISSIONS.ORDER_PARTS) || hasPermission(user, PERMISSIONS.VIEW_ORG_MACHINES),
      administration: isAdmin(user)
    }
  };
};
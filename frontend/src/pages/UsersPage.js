import React, { useEffect, useState } from 'react';
import UserForm from '../components/UserForm';
import UserInvitationForm from '../components/UserInvitationForm';
import PendingInvitations from '../components/PendingInvitations';
import PermissionDashboard from '../components/PermissionDashboard';
import PermissionGuard from '../components/PermissionGuard';
import { userService } from '../services/userService';
import { organizationsService } from '../services/organizationsService';
import { PERMISSIONS } from '../utils/permissions';
import { useTranslation } from '../hooks/useTranslation';

// New role system aligned with business model
const USER_ROLES = {
  user: 'user',
  admin: 'admin',
  super_admin: 'super_admin'
};

const USER_STATUS = {
  active: 'active',
  inactive: 'inactive',
  pending_invitation: 'pending_invitation',
  locked: 'locked'
};

function UsersPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [showInvitationForm, setShowInvitationForm] = useState(false);
  const [showPendingInvitations, setShowPendingInvitations] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [bulkSelection, setBulkSelection] = useState([]);

  // Fetch users and organizations on mount
  useEffect(() => {
    fetchUsers();
    fetchOrganizations();
  }, []);

  async function fetchUsers() {
    setLoading(true);
    setActionError(null);
    try {
      const data = await userService.getUsers();
      setUsers(data);
    } catch (err) {
      setActionError(t('users.failedToLoadUsers'));
    } finally {
      setLoading(false);
    }
  }

  async function fetchOrganizations() {
    // Implement this API call if not present
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch {
      setOrganizations([]);
    }
  }

  function handleCreate() {
    setEditingUser(null);
    setShowForm(true);
  }

  function handleEdit(user) {
    setEditingUser(user);
    setShowForm(true);
  }

  async function handleDeactivate(userId) {
    setLoading(true);
    setActionError(null);
    try {
      await userService.deactivateUser(userId);
      fetchUsers();
    } catch {
      setActionError(t('users.failedToDeactivateUser'));
    } finally {
      setLoading(false);
    }
  }

  async function handleReactivate(userId) {
    setLoading(true);
    setActionError(null);
    try {
      await userService.reactivateUser(userId);
      fetchUsers();
    } catch {
      setActionError(t('users.failedToReactivateUser'));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(formData) {
    setLoading(true);
    setActionError(null);
    try {
      if (editingUser) {
        await userService.updateUser(editingUser.id, formData);
      } else {
        await userService.createUser(formData);
      }
      setShowForm(false);
      fetchUsers();
    } catch (err) {
      setActionError(err.message || t('users.failedToSaveUser'));
    } finally {
      setLoading(false);
    }
  }

  // Invitation handlers
  async function handleInviteUser(invitationData) {
    setLoading(true);
    setActionError(null);
    setSuccessMessage(null);
    try {
      await userService.inviteUser(invitationData);
      setSuccessMessage(t('users.invitationSentSuccess', { email: invitationData.email }));
      setShowInvitationForm(false);
      fetchUsers(); // Refresh to show pending invitations
    } catch (err) {
      setActionError(err.message || t('users.failedToSendInvitation'));
    } finally {
      setLoading(false);
    }
  }

  function handleShowInvitations() {
    setShowPendingInvitations(true);
  }

  function handleResendInvitation() {
    setSuccessMessage(t('users.invitationResentSuccess'));
    fetchUsers(); // Refresh user list
  }

  // Bulk operations handlers
  const handleBulkSelect = (userId) => {
    setBulkSelection(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    if (bulkSelection.length === filteredUsers.length) {
      setBulkSelection([]);
    } else {
      setBulkSelection(filteredUsers.map(u => u.id));
    }
  };

  const handleBulkActivate = async () => {
    setLoading(true);
    setActionError(null);
    try {
      await Promise.all(bulkSelection.map(userId => userService.reactivateUser(userId)));
      setBulkSelection([]);
      fetchUsers();
    } catch {
      setActionError(t('users.failedToActivateUsers'));
    } finally {
      setLoading(false);
    }
  };

  const handleBulkDeactivate = async () => {
    setLoading(true);
    setActionError(null);
    try {
      await Promise.all(bulkSelection.map(userId => userService.deactivateUser(userId)));
      setBulkSelection([]);
      fetchUsers();
    } catch {
      setActionError(t('users.failedToDeactivateUsers'));
    } finally {
      setLoading(false);
    }
  };

  // Enhanced filtering logic with user_status support
  const filteredUsers = users
    .filter(u => {
      const matchesSearch = !search ||
        u.name?.toLowerCase().includes(search.toLowerCase()) ||
        u.email?.toLowerCase().includes(search.toLowerCase()) ||
        u.username?.toLowerCase().includes(search.toLowerCase());

      const matchesRole = !filterRole || u.role === filterRole;

      const matchesStatus = !filterStatus ||
        (filterStatus === 'active' ? u.is_active && u.user_status === 'active' :
          filterStatus === 'inactive' ? !u.is_active || u.user_status === 'inactive' :
            u.user_status === filterStatus);

      return matchesSearch && matchesRole && matchesStatus;
    });

  // Helper function to get user status display
  const getUserStatusDisplay = (user) => {
    if (!user.is_active) {
      return { text: t('users.inactiveStatus'), class: 'bg-gray-200 text-gray-600' };
    }

    switch (user.user_status) {
      case USER_STATUS.active:
        return { text: t('users.activeStatus'), class: 'bg-green-100 text-green-800' };
      case USER_STATUS.pending_invitation:
        return { text: t('users.pendingInvitationStatus'), class: 'bg-yellow-100 text-yellow-800' };
      case USER_STATUS.locked:
        return { text: t('users.lockedStatus'), class: 'bg-red-100 text-red-800' };
      case USER_STATUS.inactive:
        return { text: t('users.inactiveStatus'), class: 'bg-gray-200 text-gray-600' };
      default:
        return { text: t('users.unknownStatus'), class: 'bg-gray-200 text-gray-600' };
    }
  };

  // Helper function to get role display
  const getRoleDisplay = (role) => {
    switch (role) {
      case USER_ROLES.super_admin:
        return t('users.superAdminRole');
      case USER_ROLES.admin:
        return t('users.adminRole');
      case USER_ROLES.user:
        return t('users.userRole');
      default:
        return role; // Fallback for legacy roles
    }
  };

  const tabs = [
    { id: 'users', label: t('users.userManagement'), icon: 'users' },
    { id: 'permissions', label: t('users.permissions'), icon: 'shield', permission: PERMISSIONS.VIEW_USER_AUDIT_LOGS }
  ];

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">{t('users.title')}</h1>
        {activeTab === 'users' && (
          <div className="flex gap-2">
            <button
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition"
              onClick={() => setShowInvitationForm(true)}
            >
              📧 {t('users.inviteUser')}
            </button>
            <button
              className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition"
              onClick={handleShowInvitations}
            >
              📋 {t('users.pendingInvitations')}
            </button>
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
              onClick={handleCreate}
            >
              + {t('users.addUser')}
            </button>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <PermissionGuard
                key={tab.id}
                permission={tab.permission}
                hideIfNoPermission={tab.permission ? true : false}
              >
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  <div className="flex items-center space-x-2">
                    {tab.icon === 'users' && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                      </svg>
                    )}
                    {tab.icon === 'shield' && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                    )}
                    <span>{tab.label}</span>
                  </div>
                </button>
              </PermissionGuard>
            ))}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && (
        <>
          <div className="flex flex-wrap gap-2 mb-4">
            <input
              type="text"
              placeholder={t('users.searchPlaceholder')}
              className="border px-3 py-2 rounded-md"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <select
              className="border px-3 py-2 rounded-md"
              value={filterRole}
              onChange={e => setFilterRole(e.target.value)}
            >
              <option value="">{t('users.allRoles')}</option>
              <option value={USER_ROLES.user}>{t('users.userRole')}</option>
              <option value={USER_ROLES.admin}>{t('users.adminRole')}</option>
              <option value={USER_ROLES.super_admin}>{t('users.superAdminRole')}</option>
            </select>
            <select
              className="border px-3 py-2 rounded-md"
              value={filterStatus}
              onChange={e => setFilterStatus(e.target.value)}
            >
              <option value="">{t('users.allStatuses')}</option>
              <option value={USER_STATUS.active}>{t('users.activeStatus')}</option>
              <option value={USER_STATUS.inactive}>{t('users.inactiveStatus')}</option>
              <option value={USER_STATUS.pending_invitation}>{t('users.pendingInvitationStatus')}</option>
              <option value={USER_STATUS.locked}>{t('users.lockedStatus')}</option>
            </select>
          </div>
          {actionError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
              {actionError}
            </div>
          )}
          {successMessage && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded mb-4">
              {successMessage}
            </div>
          )}
          {/* Bulk Actions Bar */}
          {bulkSelection.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-blue-700">
                  {t('users.usersSelected', { count: bulkSelection.length })}
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={handleBulkActivate}
                    className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                    disabled={loading}
                  >
                    {t('users.activateSelected')}
                  </button>
                  <button
                    onClick={handleBulkDeactivate}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                    disabled={loading}
                  >
                    {t('users.deactivateSelected')}
                  </button>
                  <button
                    onClick={() => setBulkSelection([])}
                    className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    {t('users.clearSelection')}
                  </button>
                </div>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="min-w-full bg-white rounded shadow">
              <thead>
                <tr>
                  <th className="px-4 py-2 text-left">
                    <input
                      type="checkbox"
                      checked={bulkSelection.length === filteredUsers.length && filteredUsers.length > 0}
                      onChange={handleSelectAll}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                  </th>
                  <th className="px-4 py-2 text-left">{t('users.name')}</th>
                  <th className="px-4 py-2 text-left">{t('users.email')}</th>
                  <th className="px-4 py-2 text-left">{t('users.role')}</th>
                  <th className="px-4 py-2 text-left">{t('users.organization')}</th>
                  <th className="px-4 py-2 text-left">{t('users.status')}</th>
                  <th className="px-4 py-2 text-left">{t('users.lastLogin')}</th>
                  <th className="px-4 py-2 text-left">{t('users.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map(u => {
                  const statusDisplay = getUserStatusDisplay(u);
                  return (
                    <tr key={u.id} className="border-t hover:bg-gray-50">
                      <td className="px-4 py-2">
                        <input
                          type="checkbox"
                          checked={bulkSelection.includes(u.id)}
                          onChange={() => handleBulkSelect(u.id)}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-4 py-2">
                        <div>
                          <div className="font-medium text-gray-900">{u.name || u.username}</div>
                          <div className="text-sm text-gray-500">@{u.username}</div>
                        </div>
                      </td>
                      <td className="px-4 py-2">{u.email}</td>
                      <td className="px-4 py-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {getRoleDisplay(u.role)}
                        </span>
                      </td>
                      <td className="px-4 py-2">{organizations.find(org => org.id === u.organization_id)?.name || '-'}</td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusDisplay.class}`}>
                          {statusDisplay.text}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : t('users.never')}
                      </td>
                      <td className="px-4 py-2">
                        <div className="flex gap-2">
                          <button
                            className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                            onClick={() => handleEdit(u)}
                            disabled={loading}
                          >
                            {t('users.edit')}
                          </button>
                          {u.is_active && u.user_status === 'active' ? (
                            <button
                              className="text-red-600 hover:text-red-900 text-sm font-medium"
                              onClick={() => handleDeactivate(u.id)}
                              disabled={loading}
                            >
                              {t('users.deactivate')}
                            </button>
                          ) : (
                            <button
                              className="text-green-600 hover:text-green-900 text-sm font-medium"
                              onClick={() => handleReactivate(u.id)}
                              disabled={loading}
                            >
                              {t('users.reactivate')}
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {filteredUsers.length === 0 && (
                  <tr>
                    <td colSpan={8} className="text-center py-8 text-gray-500">
                      <div className="flex flex-col items-center">
                        <svg className="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                        </svg>
                        <p className="text-lg font-medium">{t('users.noUsersFound')}</p>
                        <p className="text-sm">{t('users.adjustSearchCriteria')}</p>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {showForm && (
            <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg relative">
                <button
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-700"
                  onClick={() => setShowForm(false)}
                  aria-label="Close"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <UserForm
                  organizations={organizations}
                  initialData={editingUser || {}}
                  onSubmit={handleSubmit}
                  onClose={() => setShowForm(false)}
                  editingSelf={false}
                />
              </div>
            </div>
          )}

          {/* User Invitation Modal */}
          {showInvitationForm && (
            <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-lg relative">
                <button
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-700"
                  onClick={() => setShowInvitationForm(false)}
                  aria-label="Close"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <UserInvitationForm
                  organizations={organizations}
                  onSubmit={handleInviteUser}
                  onClose={() => setShowInvitationForm(false)}
                />
              </div>
            </div>
          )}

          {/* Pending Invitations Modal */}
          {showPendingInvitations && (
            <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-4xl relative max-h-[80vh] overflow-y-auto">
                <button
                  className="absolute top-2 right-2 text-gray-400 hover:text-gray-700"
                  onClick={() => setShowPendingInvitations(false)}
                  aria-label="Close"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <PendingInvitations onResendInvitation={handleResendInvitation} />
              </div>
            </div>
          )}
        </>
      )}

      {/* Permissions Tab Content */}
      {activeTab === 'permissions' && (
        <PermissionDashboard />
      )}
    </div>
  );
}

export default UsersPage;
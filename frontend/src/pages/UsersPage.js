import React, { useEffect, useState } from 'react';
import { useAuth } from '../AuthContext';
import UserForm from '../components/UserForm';
import { userService } from '../services/userService';

function UsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');
  const [filterRole, setFilterRole] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionError, setActionError] = useState(null);

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
      setActionError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  }

  async function fetchOrganizations() {
    // Implement this API call if not present
    try {
      const res = await fetch('/api/organizations');
      const data = await res.json();
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
      setActionError('Failed to deactivate user.');
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
      setActionError('Failed to reactivate user.');
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
      setActionError(err.message || 'Failed to save user.');
    } finally {
      setLoading(false);
    }
  }

  // Filtering logic
  const filteredUsers = users
    .filter(u =>
      (!search || u.name?.toLowerCase().includes(search.toLowerCase()) || u.email?.toLowerCase().includes(search.toLowerCase()))
      && (!filterRole || u.role === filterRole)
      && (!filterStatus || (filterStatus === 'active' ? u.active : !u.active))
    );

  return (
    <div>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <h1 className="text-2xl font-bold text-gray-800">User Management</h1>
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
          onClick={handleCreate}
        >
          + Add User
        </button>
      </div>
      <div className="flex flex-wrap gap-2 mb-4">
        <input
          type="text"
          placeholder="Search by name or email"
          className="border px-3 py-2 rounded-md"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select
          className="border px-3 py-2 rounded-md"
          value={filterRole}
          onChange={e => setFilterRole(e.target.value)}
        >
          <option value="">All Roles</option>
          <option value="Oraseas Admin">Oraseas Admin</option>
          <option value="Oraseas Inventory Manager">Oraseas Inventory Manager</option>
          <option value="Customer Admin">Customer Admin</option>
          <option value="Customer User">Customer User</option>
          <option value="Supplier User">Supplier User</option>
        </select>
        <select
          className="border px-3 py-2 rounded-md"
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      {actionError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4">
          {actionError}
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded shadow">
          <thead>
            <tr>
              <th className="px-4 py-2 text-left">Name</th>
              <th className="px-4 py-2 text-left">Email</th>
              <th className="px-4 py-2 text-left">Role</th>
              <th className="px-4 py-2 text-left">Organization</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map(u => (
              <tr key={u.id} className="border-t">
                <td className="px-4 py-2">{u.name || u.username}</td>
                <td className="px-4 py-2">{u.email}</td>
                <td className="px-4 py-2">{u.role}</td>
                <td className="px-4 py-2">{organizations.find(org => org.id === u.organization_id)?.name || '-'}</td>
                <td className="px-4 py-2">
                  {u.active ? (
                    <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded">Active</span>
                  ) : (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded">Inactive</span>
                  )}
                </td>
                <td className="px-4 py-2 flex gap-2">
                  <button
                    className="text-blue-600 hover:underline"
                    onClick={() => handleEdit(u)}
                    disabled={loading}
                  >
                    Edit
                  </button>
                  {u.active ? (
                    <button
                      className="text-red-600 hover:underline"
                      onClick={() => handleDeactivate(u.id)}
                      disabled={loading}
                    >
                      Deactivate
                    </button>
                  ) : (
                    <button
                      className="text-green-600 hover:underline"
                      onClick={() => handleReactivate(u.id)}
                      disabled={loading}
                    >
                      Reactivate
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {filteredUsers.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-6 text-gray-500">No users found.</td>
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
    </div>
  );
}

export default UsersPage;
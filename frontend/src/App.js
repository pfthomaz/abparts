// frontend/src/App.js

import React, { useState, useEffect, useCallback } from 'react';
import './index.css'; // Import Tailwind CSS base styles
import { useAuth } from './AuthContext'; // Import useAuth hook
import LoginForm from './components/LoginForm'; // Import LoginForm component
import Modal from './components/Modal'; // Import Modal component
import OrganizationForm from './components/OrganizationForm'; // Import OrganizationForm component
import UserForm from './components/UserForm'; // Import UserForm component
import PartForm from './components/PartForm'; // Import PartForm component

function App() {
    const { token, user, logout, loadingUser } = useAuth();
    
    const [organizations, setOrganizations] = useState([]);
    const [users, setUsers] = useState([]);
    const [parts, setParts] = useState([]);
    const [inventoryItems, setInventoryItems] = useState([]);
    const [supplierOrders, setSupplierOrders] = useState([]);
    const [supplierOrderItems, setSupplierOrderItems] = useState([]);
    const [customerOrders, setCustomerOrders] = useState([]);
    const [customerOrderItems, setCustomerOrderItems] = useState([]);
    const [partUsages, setPartUsages] = useState([]);
    
    const [loadingData, setLoadingData] = useState(false);
    const [error, setError] = useState(null);

    // Modal control states
    const [showOrganizationModal, setShowOrganizationModal] = useState(false);
    const [editingOrganization, setEditingOrganization] = useState(null);
    const [showUserModal, setShowUserModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [showPartModal, setShowPartModal] = useState(false);
    const [editingPart, setEditingPart] = useState(null);


    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

    // Effect to fetch data when token or user changes
    const fetchData = useCallback(async () => { // Wrapped with useCallback
        if (!token) {
        setOrganizations([]);
        setUsers([]);
        setParts([]);
        setInventoryItems([]);
        setSupplierOrders([]);
        setSupplierOrderItems([]);
        setCustomerOrders([]);
        setCustomerOrderItems([]);
        setPartUsages([]);
        setLoadingData(false);
        return;
        }

        setLoadingData(true);
        setError(null); // Clear previous errors

        try {
        // --- Fetch Organizations ---
        const orgsResponse = await fetch(`${API_BASE_URL}/organizations`);
        if (!orgsResponse.ok) {
            throw new Error(`Failed to fetch organizations: ${orgsResponse.status}`);
        }
        const orgsData = await orgsResponse.json();
        setOrganizations(orgsData);

        // --- Fetch Users ---
        const usersResponse = await fetch(`${API_BASE_URL}/users`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!usersResponse.ok) {
            throw new Error(`Failed to fetch users: ${usersResponse.status}`);
        }
        const usersData = await usersResponse.json();
        setUsers(usersData);

        // --- Fetch Parts ---
        const partsResponse = await fetch(`${API_BASE_URL}/parts`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!partsResponse.ok) {
            throw new Error(`Failed to fetch parts: ${partsResponse.status}`);
        }
        const partsData = await partsResponse.json();
        setParts(partsData);

        // --- Fetch Inventory Items ---
        const inventoryResponse = await fetch(`${API_BASE_URL}/inventory`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!inventoryResponse.ok) {
            throw new Error(`Failed to fetch inventory items: ${inventoryResponse.status}`);
        }
        const inventoryData = await inventoryResponse.json();
        setInventoryItems(inventoryData);

        // --- Fetch Supplier Orders ---
        const supplierOrdersResponse = await fetch(`${API_BASE_URL}/supplier_orders`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!supplierOrdersResponse.ok) {
            throw new Error(`Failed to fetch supplier orders: ${supplierOrdersResponse.status}`);
        }
        const supplierOrdersData = await supplierOrdersResponse.json();
        setSupplierOrders(supplierOrdersData);

        // --- Fetch Supplier Order Items ---
        const supplierOrderItemsResponse = await fetch(`${API_BASE_URL}/supplier_order_items`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!supplierOrderItemsResponse.ok) {
            throw new Error(`Failed to fetch supplier order items: ${supplierOrderItemsResponse.status}`);
        }
        const supplierOrderItemsData = await supplierOrderItemsResponse.json();
        setSupplierOrderItems(supplierOrderItemsData);

        // --- Fetch Customer Orders ---
        const customerOrdersResponse = await fetch(`${API_BASE_URL}/customer_orders`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!customerOrdersResponse.ok) {
            throw new Error(`Failed to fetch customer orders: ${customerOrdersResponse.status}`);
        }
        const customerOrdersData = await customerOrdersResponse.json();
        setCustomerOrders(customerOrdersData);

        // --- Fetch Customer Order Items ---
        const customerOrderItemsResponse = await fetch(`${API_BASE_URL}/customer_order_items`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!customerOrderItemsResponse.ok) {
            throw new Error(`Failed to fetch customer order items: ${customerOrderItemsResponse.status}`);
        }
        const customerOrderItemsData = await customerOrderItemsResponse.json();
        setCustomerOrderItems(customerOrderItemsData);

        // --- Fetch Part Usages ---
        const partUsagesResponse = await fetch(`${API_BASE_URL}/part_usage`, {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
        });
        if (!partUsagesResponse.ok) {
            throw new Error(`Failed to fetch part usages: ${partUsagesResponse.status}`);
        }
        const partUsagesData = await partUsagesResponse.json();
        setPartUsages(partUsagesData);


        } catch (err) {
        setError(err.message);
        console.error("Error fetching data:", err);
        } finally {
        setLoadingData(false);
        }
    }, [token, API_BASE_URL]); // Dependencies for useCallback

    useEffect(() => {
        if (!loadingUser) { // Only fetch data once user loading is complete
            fetchData();
        }
    }, [token, API_BASE_URL, loadingUser, fetchData]);

    // Handler for creating a new organization
    const handleCreateOrganization = async (orgData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/organizations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(orgData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData(); // Re-fetch all data to update the list
            setShowOrganizationModal(false); // Close the modal
        } catch (err) {
            console.error("Error creating organization:", err);
            throw err; // Re-throw to be caught by the form
        }
    };

    // Handler for creating a new user
    const handleCreateUser = async (userData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(userData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData(); // Re-fetch all data to update the list
            setShowUserModal(false); // Close the modal
        } catch (err) {
            console.error("Error creating user:", err);
            throw err; // Re-throw to be caught by the form
        }
    };

    // Handler for creating a new part
    const handleCreatePart = async (partData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/parts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(partData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData(); // Re-fetch all data to update the list
            setShowPartModal(false); // Close the modal
        } catch (err) {
            console.error("Error creating part:", err);
            throw err; // Re-throw to be caught by the form
        }
    };


    // --- Conditional Rendering based on Authentication State ---
    if (loadingUser) {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <p className="text-xl text-gray-700">Checking authentication...</p>
        </div>
    );
    }

    if (!token || !user) {
    return <LoginForm />;
    }

    // Helper to find organization name
    const getOrganizationName = (orgId) => {
        const org = organizations.find(o => o.id === orgId);
        return org ? org.name : 'Unknown Organization';
    };

    // Helper to find part name
    const getPartName = (partId) => {
        const part = parts.find(p => p.id === partId);
        return part ? part.name : 'Unknown Part';
    };

    // Helper to find username
    const getUserName = (userId) => {
        const userFound = users.find(u => u.id === userId);
        return userFound ? (userFound.name || userFound.username) : 'Unknown User';
    };

    // --- Authenticated User View ---
    return (
    <div className="min-h-screen bg-gray-100 py-10">
        <div className="container mx-auto p-4 bg-white shadow-lg rounded-lg">
        <div className="flex justify-between items-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800">ABParts Dashboard</h1>
            <div className="flex items-center space-x-4">
            <span className="text-gray-700">Welcome, <span className="font-semibold">{user.name || user.username}</span> ({user.role})</span>
            <button
                onClick={logout}
                className="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
            >
                Logout
            </button>
            </div>
        </div>

        {loadingData ? (
            <div className="text-center text-gray-600 text-lg my-8">Loading data...</div>
        ) : error ? (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-8" role="alert">
            <strong className="font-bold">Error:</strong>
            <span className="block sm:inline ml-2">{error}</span>
            </div>
        ) : (
            <>
            {/* Organizations Section */}
            <div className="flex justify-between items-center mb-6 mt-10 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Organizations</h2>
                {user.role === "Oraseas Admin" && (
                    <button
                        onClick={() => {
                            setEditingOrganization(null); // Ensure we're creating, not editing
                            setShowOrganizationModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Organization
                    </button>
                )}
            </div>
            {organizations.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No organizations found.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {organizations.map((org) => (
                    <div key={org.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-blue-700 mb-2">{org.name}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Type:</span> {org.type}</p>
                    {org.address && <p className="text-gray-600 mb-1"><span className="font-medium">Address:</span> {org.address}</p>}
                    {org.contact_info && <p className="text-gray-600 mb-1"><span className="font-medium">Contact:</span> {org.contact_info}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {org.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Organization Form */}
            <Modal
                show={showOrganizationModal}
                onClose={() => setShowOrganizationModal(false)}
                title={editingOrganization ? "Edit Organization" : "Add New Organization"}
            >
                <OrganizationForm
                    initialData={editingOrganization || {}}
                    onSubmit={handleCreateOrganization} // Will be handleUpdateOrganization when editing
                    onClose={() => setShowOrganizationModal(false)}
                />
            </Modal>


            {/* Users Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Users</h2>
                {(user.role === "Oraseas Admin" || user.role === "Customer Admin") && (
                    <button
                        onClick={() => {
                            setEditingUser(null); // Ensure we're creating, not editing
                            setShowUserModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add User
                    </button>
                )}
            </div>
            {users.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No users found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {users.map((userItem) => ( // Renamed to userItem to avoid conflict with 'user' from useAuth
                    <div key={userItem.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-green-700 mb-2">{userItem.name || userItem.username}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Role:</span> {userItem.role}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Email:</span> {userItem.email}</p>
                    <p className="text-sm text-gray-400 mt-3">Org ID: {userItem.organization_id}</p>
                    <p className="text-sm text-gray-400">User ID: {userItem.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for User Form */}
            <Modal
                show={showUserModal}
                onClose={() => setShowUserModal(false)}
                title={editingUser ? "Edit User" : "Add New User"}
            >
                <UserForm
                    initialData={editingUser || {}}
                    organizations={organizations} // Pass organizations for dropdown
                    onSubmit={handleCreateUser} // Will be handleUpdateUser when editing
                    onClose={() => setShowUserModal(false)}
                />
            </Modal>

            {/* Parts Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Parts</h2>
                {user.role === "Oraseas Admin" && ( // Only Oraseas Admin can create parts
                    <button
                        onClick={() => {
                            setEditingPart(null); // Ensure we're creating, not editing
                            setShowPartModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Part
                    </button>
                )}
            </div>
            {parts.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No parts found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {parts.map((part) => (
                    <div key={part.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-purple-700 mb-2">{part.name}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Part #:</span> {part.part_number}</p>
                    {part.description && <p className="text-gray-600 mb-1"><span className="font-medium">Description:</span> {part.description}</p>}
                    <p className="text-gray-600 mb-1">
                        <span className="font-medium">Proprietary:</span> {part.is_proprietary ? 'Yes' : 'No'}
                    </p>
                    <p className="text-gray-600 mb-1">
                        <span className="font-medium">Consumable:</span> {part.is_consumable ? 'Yes' : 'No'}
                    </p>
                    {/* New: Display Images for Parts */}
                    {part.image_urls && part.image_urls.length > 0 && (
                        <div className="mt-3">
                            <span className="font-medium text-gray-600">Images:</span>
                            <div className="grid grid-cols-2 gap-2 mt-1">
                                {part.image_urls.map((imageUrl, imgIndex) => (
                                    <img
                                        key={imgIndex}
                                        src={`${API_BASE_URL}${imageUrl}`} // Prepend base URL for correct path
                                        alt={`Part Image ${imgIndex + 1}`}
                                        className="w-full h-24 object-cover rounded-md shadow-sm"
                                        onError={(e) => {
                                            e.target.onerror = null; // Prevent infinite loop
                                            e.target.src = "https://placehold.co/100x100?text=Image+Error"; // Placeholder for broken images
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                    <p className="text-sm text-gray-400 mt-3">ID: {part.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Part Form */}
            <Modal
                show={showPartModal}
                onClose={() => setShowPartModal(false)}
                title={editingPart ? "Edit Part" : "Add New Part"}
            >
                <PartForm
                    initialData={editingPart || {}}
                    onSubmit={handleCreatePart} // Will be handleUpdatePart when editing
                    onClose={() => setShowPartModal(false)}
                />
            </Modal>

            {/* Inventory Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Inventory</h2>
            {inventoryItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No inventory items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {inventoryItems.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-orange-700 mb-2">
                        {getPartName(item.part_id)} (in {getOrganizationName(item.organization_id)})
                    </h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Current Stock:</span> {item.current_stock}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Min Stock Rec:</span> {item.minimum_stock_recommendation}</p>
                    {item.reorder_threshold_set_by && <p className="text-gray-600 mb-1"><span className="font-medium">Set By:</span> {item.reorder_threshold_set_by}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Supplier Orders Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Supplier Orders</h2>
            {supplierOrders.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No supplier orders found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {supplierOrders.map((order) => (
                    <div key={order.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-red-700 mb-2">Order from {order.supplier_name}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Status:</span> {order.status}</p>
                    {order.expected_delivery_date && <p className="text-gray-600 mb-1"><span className="font-medium">Expected Delivery:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>}
                    {order.actual_delivery_date && <p className="text-gray-600 mb-1"><span className="font-medium">Actual Delivery:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {order.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Supplier Order Items Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Supplier Order Items</h2>
            {supplierOrderItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No supplier order items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {supplierOrderItems.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-pink-700 mb-2">{getPartName(item.part_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity:</span> {item.quantity}</p>
                    {item.unit_price && <p className="text-gray-600 mb-1"><span className="font-medium">Unit Price:</span> ${item.unit_price}</p>}
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order ID:</span> {item.supplier_order_id}</p>
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Customer Orders Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Customer Orders</h2>
            {customerOrders.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No customer orders found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {customerOrders.map((order) => (
                    <div key={order.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-indigo-700 mb-2">Order for {getOrganizationName(order.customer_organization_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order Date:</span> {new Date(order.order_date).toLocaleDateString()}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Status:</span> {order.status}</p>
                    {order.expected_delivery_date && <p className="text-gray-600 mb-1"><span className="font-medium">Expected Delivery:</span> {new Date(order.expected_delivery_date).toLocaleDateString()}</p>}
                    {order.actual_delivery_date && <p className="text-gray-600 mb-1"><span className="font-medium">Actual Delivery:</span> {new Date(order.actual_delivery_date).toLocaleDateString()}</p>}
                    {order.ordered_by_user_id && <p className="text-gray-600 mb-1"><span className="font-medium">Ordered By:</span> {getUserName(order.ordered_by_user_id)}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {order.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Customer Order Items Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Customer Order Items</h2>
            {customerOrderItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No customer order items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {customerOrderItems.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-teal-700 mb-2">{getPartName(item.part_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity:</span> {item.quantity}</p>
                    {item.unit_price && <p className="text-gray-600 mb-1"><span className="font-medium">Unit Price:</span> ${item.unit_price}</p>}
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order ID:</span> {item.customer_order_id}</p>
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Part Usage Section */}
            <h2 className="text-3xl font-bold text-gray-700 mb-6 border-b-2 pb-2">Part Usage</h2>
            {partUsages.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No part usage records found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {partUsages.map((usage) => (
                    <div key={usage.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-fuchsia-700 mb-2">{getPartName(usage.part_id)} used by {getOrganizationName(usage.customer_organization_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity Used:</span> {usage.quantity_used}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Usage Date:</span> {new Date(usage.usage_date).toLocaleDateString()}</p>
                    {usage.machine_id && <p className="text-gray-600 mb-1"><span className="font-medium">Machine ID:</span> {usage.machine_id}</p>}
                    {usage.recorded_by_user_id && <p className="text-gray-600 mb-1"><span className="font-medium">Recorded By:</span> {getUserName(usage.recorded_by_user_id)}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {usage.id}</p>
                    </div>
                ))}
                </div>
            )}
            </>
        )}
        </div>
    </div>
    );
}

export default App;

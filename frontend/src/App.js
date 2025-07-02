// frontend/src/App.js

import React, { useState, useEffect, useCallback } from 'react';
import './index.css'; // Import Tailwind CSS base styles
import { useAuth } from './AuthContext'; // Import useAuth hook
import LoginForm from './components/LoginForm'; // Import LoginForm component
import Modal from './components/Modal'; // Import Modal component
import OrganizationForm from './components/OrganizationForm'; // Import OrganizationForm component
import UserForm from './components/UserForm'; // Import UserForm component
import PartForm from './components/PartForm'; // Import PartForm component
import InventoryForm from './components/InventoryForm'; // Import InventoryForm component
import SupplierOrderForm from './components/SupplierOrderForm'; // Import SupplierOrderForm component
import SupplierOrderItemForm from './components/SupplierOrderItemForm'; // Import SupplierOrderItemForm component
import CustomerOrderForm from './components/CustomerOrderForm'; // Import CustomerOrderForm component
import CustomerOrderItemForm from './components/CustomerOrderItemForm'; // Import CustomerOrderItemForm component
import PartUsageForm from './components/PartUsageForm'; // New: Import PartUsageForm component
import MachineForm from './components/MachineForm'; // Import MachineForm component
import StockAdjustmentForm from './components/StockAdjustmentForm'; // New: Import StockAdjustmentForm
import StocktakeWorksheetGenerator from './components/StocktakeWorksheetGenerator'; // New: Import StocktakeWorksheetGenerator

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
    const [machines, setMachines] = useState([]); // State for machines
    
    const [loadingData, setLoadingData] = useState(false);
    const [error, setError] = useState(null);

    // Modal control states
    const [showOrganizationModal, setShowOrganizationModal] = useState(false);
    const [editingOrganization, setEditingOrganization] = useState(null);
    const [showUserModal, setShowUserModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [showPartModal, setShowPartModal] = useState(false);
    const [editingPart, setEditingPart] = useState(null);
    const [showInventoryModal, setShowInventoryModal] = useState(false);
    const [editingInventory, setEditingInventory] = useState(null);
    const [showSupplierOrderModal, setShowSupplierOrderModal] = useState(false);
    const [editingSupplierOrder, setEditingSupplierOrder] = useState(null);
    const [showSupplierOrderItemModal, setShowSupplierOrderItemModal] = useState(false);
    const [editingSupplierOrderItem, setEditingSupplierOrderItem] = useState(null);
    const [showCustomerOrderModal, setShowCustomerOrderModal] = useState(false);
    const [editingCustomerOrder, setEditingCustomerOrder] = useState(null);
    const [showCustomerOrderItemModal, setShowCustomerOrderItemModal] = useState(false);
    const [editingCustomerOrderItem, setEditingCustomerOrderItem] = useState(null);
    const [showPartUsageModal, setShowPartUsageModal] = useState(false); // New: for Part Usage Form
    const [editingPartUsage, setEditingPartUsage] = useState(null); // New: for Part Usage editing
    const [showMachineModal, setShowMachineModal] = useState(false); // For Machine Form
    const [editingMachine, setEditingMachine] = useState(null); // For Machine editing
    const [showStockAdjustmentModal, setShowStockAdjustmentModal] = useState(false); // New: for Stock Adjustment Form
    const [selectedInventoryItemForAdjustment, setSelectedInventoryItemForAdjustment] = useState(null); // New: for Stock Adjustment
    const [selectedInventoryOrgFilter, setSelectedInventoryOrgFilter] = useState(''); // New: for inventory org filter
    const [showStocktakeSheetGenerator, setShowStocktakeSheetGenerator] = useState(false); // New: for stocktake worksheet
    const [stocktakeWorksheetData, setStocktakeWorksheetData] = useState([]); // New: to hold worksheet data
    const [loadingStocktakeWorksheet, setLoadingStocktakeWorksheet] = useState(false); // New: loading state for worksheet

    const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

    // --- Modal Openers ---
    const openEditPartModal = (partToEdit) => {
        setEditingPart(partToEdit);
        setShowPartModal(true);
    };

    // Effect to fetch data when token or user changes
    const fetchData = useCallback(async () => {
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
        setMachines([]); // Reset machines
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

        // --- Fetch Machines ---
        const machinesResponse = await fetch(`${API_BASE_URL}/machines`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });
        if (!machinesResponse.ok) {
            throw new Error(`Failed to fetch machines: ${machinesResponse.status}`);
        }
        const machinesData = await machinesResponse.json();
        setMachines(machinesData);


        } catch (err) {
        setError(err.message);
        console.error("Error fetching data:", err);
        } finally {
        setLoadingData(false);
        }
    }, [token, API_BASE_URL]);

    useEffect(() => {
        if (!loadingUser) {
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

            await fetchData();
            setShowOrganizationModal(false);
        } catch (err) {
            console.error("Error creating organization:", err);
            throw err;
        }
    };

    // Handler for deleting a part
    const handleDeletePart = async (partId) => {
        if (!window.confirm("Are you sure you want to delete this part? This action cannot be undone.")) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/parts/${partId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok && response.status !== 204) { // 204 is also a success for DELETE
                const errorData = await response.json().catch(() => ({ detail: "Failed to delete part and parse error response." }));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData(); // Refresh data
        } catch (err) {
            console.error("Error deleting part:", err);
            setError(err.message || "Failed to delete part. Please try again."); // Set error for display
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

            await fetchData();
            setShowUserModal(false);
        } catch (err) {
            console.error("Error creating user:", err);
            throw err;
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

            await fetchData(); // Refresh data
            setShowPartModal(false); // Close modal
        } catch (err) {
            console.error("Error creating part:", err);
            throw err; // Re-throw to be caught by PartForm
        }
    };

    // Handler for updating an existing part
    const handleUpdatePart = async (partDataFromForm) => {
        if (!editingPart || !editingPart.id) {
            console.error("No part selected for editing or missing ID.");
            throw new Error("No part selected for editing or missing ID.");
        }
        try {
            // The partDataFromForm contains all form fields, including image_urls
            // which PartForm prepares (existing + new uploads).
            const response = await fetch(`${API_BASE_URL}/parts/${editingPart.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(partDataFromForm), // Send data from the form
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            setShowPartModal(false);
            setEditingPart(null);
            await fetchData(); // Refresh data
        } catch (err) {
            console.error("Error updating part:", err);
            throw err; // Re-throw to be caught by PartForm
        }
    };

    // Handler for creating a new inventory item
    const handleCreateInventory = async (inventoryData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/inventory`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(inventoryData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowInventoryModal(false);
        } catch (err) {
            console.error("Error creating inventory item:", err);
            throw err;
        }
    };

    // Handler for creating a new supplier order
    const handleCreateSupplierOrder = async (orderData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/supplier_orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(orderData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowSupplierOrderModal(false);
        } catch (err) {
            console.error("Error creating supplier order:", err);
            throw err;
        }
    };

    // Handler for creating a new supplier order item
    const handleCreateSupplierOrderItem = async (itemData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/supplier_order_items`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(itemData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowSupplierOrderItemModal(false);
        } catch (err) {
            console.error("Error creating supplier order item:", err);
            throw err;
        }
    };

    // Handler for creating a new customer order
    const handleCreateCustomerOrder = async (orderData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/customer_orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(orderData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowCustomerOrderModal(false);
        } catch (err) {
            console.error("Error creating customer order:", err);
            throw err;
        }
    };

    // Handler for creating a new customer order item
    const handleCreateCustomerOrderItem = async (itemData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/customer_order_items`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(itemData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowCustomerOrderItemModal(false);
        } catch (err) {
            console.error("Error creating customer order item:", err);
            throw err;
        }
    };

    // New: Handler for creating a new part usage record
    const handleCreatePartUsage = async (usageData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/part_usage`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(usageData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData();
            setShowPartUsageModal(false);
        } catch (err) {
            console.error("Error creating part usage:", err);
            throw err;
        }
    };

    // Handler for creating a new machine
    const handleCreateMachine = async (machineData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/machines`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(machineData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            await fetchData(); // Refresh all data, including machines
            setShowMachineModal(false); // Close the machine modal
        } catch (err) {
            console.error("Error creating machine:", err);
            throw err; // Re-throw to be caught by the form's error handling
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

    // Helper to find supplier order by ID
    const getSupplierOrderDetails = (orderId) => {
        const order = supplierOrders.find(o => o.id === orderId);
        if (order) {
            return `Order ${order.id.substring(0, 8)} - ${order.supplier_name} (${new Date(order.order_date).toLocaleDateString()})`;
        }
        return 'Unknown Order';
    };

    // Helper to find customer order by ID
    const getCustomerOrderDetails = (orderId) => {
        const order = customerOrders.find(o => o.id === orderId);
        if (order) {
            const customerOrgName = getOrganizationName(order.customer_organization_id);
            return `Order ${order.id.substring(0, 8)} - for ${customerOrgName} (${new Date(order.order_date).toLocaleDateString()})`;
        }
        return 'Unknown Order';
    };

    // Helper to find customer organization by ID for Part Usage display
    const getCustomerOrganizationDetails = (orgId) => {
        const org = organizations.find(o => o.id === orgId);
        return org ? org.name : 'Unknown Customer Organization';
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
                            setEditingOrganization(null);
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
                    onSubmit={handleCreateOrganization}
                    onClose={() => setShowOrganizationModal(false)}
                />
            </Modal>


            {/* Users Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Users</h2>
                {(user.role === "Oraseas Admin" || user.role === "Customer Admin") && (
                    <button
                        onClick={() => {
                            setEditingUser(null);
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
                {users.map((userItem) => (
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
                    organizations={organizations}
                    onSubmit={handleCreateUser}
                    onClose={() => setShowUserModal(false)}
                />
            </Modal>

            {/* Parts Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Parts</h2>
                {user.role === "Oraseas Admin" && (
                    <button
                        onClick={() => {
                            setEditingPart(null);
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
                    {part.image_urls && part.image_urls.length > 0 && (
                        <div className="mt-3">
                            <span className="font-medium text-gray-600">Images:</span>
                            <div className="grid grid-cols-2 gap-2 mt-1">
                                {part.image_urls.map((imageUrl, imgIndex) => (
                                    <img
                                        key={imgIndex}
                                        src={`${API_BASE_URL}${imageUrl}`}
                                        alt={`Part Image ${imgIndex + 1}`}
                                        className="w-full h-24 object-cover rounded-md shadow-sm"
                                        onError={(e) => {
                                            e.target.onerror = null;
                                            e.target.src = "https://placehold.co/100x100?text=Image+Error";
                                        }}
                                    />
                                ))}
                            </div>
                        </div>
                    )}
                    <p className="text-sm text-gray-400 mt-3">ID: {part.id}</p>
                    {user.role === "Oraseas Admin" && (
                        <div className="mt-4 flex space-x-2">
                            <button
                                onClick={() => openEditPartModal(part)}
                                className="bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm"
                            >
                                Edit
                            </button>
                            <button
                                onClick={() => handleDeletePart(part.id)}
                                className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 text-sm"
                            >
                                Delete
                            </button>
                        </div>
                    )}
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
                    onSubmit={editingPart ? handleUpdatePart : handleCreatePart}
                    onClose={() => {
                        setShowPartModal(false);
                        setEditingPart(null); // Clear editing state on close
                    }}
                />
            </Modal>

            {/* Inventory Section */}
            <div className="flex justify-between items-center mb-2 border-b-2 pb-2"> {/* Reduced mb for filter */}
                <h2 className="text-3xl font-bold text-gray-700">Inventory</h2>
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager") && (
                    <button
                        onClick={() => {
                            setEditingInventory(null);
                            setShowInventoryModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Inventory Item
                    </button>
                )}
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager") && (
                    <button
                        onClick={() => {
                            setStocktakeWorksheetData([]); // Clear previous data
                            setShowStocktakeSheetGenerator(true);
                        }}
                        className="ml-4 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Generate Stocktake Worksheet
                    </button>
                )}
            </div>
            {/* Filter for Inventory by Organization */}
            <div className="mb-6">
                <label htmlFor="inventoryOrgFilter" className="block text-sm font-medium text-gray-700">
                    Filter by Organization/Location:
                </label>
                <select
                    id="inventoryOrgFilter"
                    name="inventoryOrgFilter"
                    value={selectedInventoryOrgFilter}
                    onChange={(e) => setSelectedInventoryOrgFilter(e.target.value)}
                    className="mt-1 block w-full md:w-1/3 pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                    <option value="">All Organizations</option>
                    {organizations.map((org) => (
                        <option key={org.id} value={org.id}>
                            {org.name} ({org.type})
                        </option>
                    ))}
                </select>
            </div>

            {inventoryItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No inventory items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {inventoryItems
                    .filter(item => !selectedInventoryOrgFilter || item.organization_id === selectedInventoryOrgFilter)
                    .map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-orange-700 mb-2">
                        {getPartName(item.part_id)}
                    </h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Location:</span> {getOrganizationName(item.organization_id)}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Current Stock:</span> {item.current_stock}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Min Stock Rec:</span> {item.minimum_stock_recommendation}</p>
                    {item.reorder_threshold_set_by && <p className="text-gray-600 mb-1"><span className="font-medium">Set By:</span> {item.reorder_threshold_set_by}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    {/* Adjust Stock Button Logic:
                        - Oraseas Admin: Can adjust any stock.
                        - Oraseas Inventory Manager: Can adjust stock for "Oraseas EE" organization.
                    */}
                    { (user.role === "Oraseas Admin" ||
                       (user.role === "Oraseas Inventory Manager" && organizations.find(o => o.id === item.organization_id)?.name === "Oraseas EE")
                      ) && (
                        <button
                            onClick={() => {
                                setSelectedInventoryItemForAdjustment(item);
                                setShowStockAdjustmentModal(true);
                            }}
                            className="mt-3 bg-yellow-500 text-white py-1 px-3 rounded-md hover:bg-yellow-600 text-sm focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                        >
                            Adjust Stock
                        </button>
                    )}
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Inventory Form */}
            <Modal
                show={showInventoryModal}
                onClose={() => setShowInventoryModal(false)}
                title={editingInventory ? "Edit Inventory Item" : "Add New Inventory Item"}
            >
                <InventoryForm
                    initialData={editingInventory || {}}
                    organizations={organizations}
                    parts={parts}
                    onSubmit={handleCreateInventory}
                    onClose={() => setShowInventoryModal(false)}
                />
            </Modal>

            {/* Modal for Stock Adjustment Form */}
            {selectedInventoryItemForAdjustment && (
                <Modal
                    show={showStockAdjustmentModal}
                    onClose={() => {
                        setShowStockAdjustmentModal(false);
                        setSelectedInventoryItemForAdjustment(null);
                    }}
                    title={`Adjust Stock for ${selectedInventoryItemForAdjustment.part?.name || getPartName(selectedInventoryItemForAdjustment.part_id)}`}
                >
                    <StockAdjustmentForm
                        inventoryItem={selectedInventoryItemForAdjustment}
                        onSuccess={() => {
                            setShowStockAdjustmentModal(false);
                            setSelectedInventoryItemForAdjustment(null);
                            fetchData(); // Refresh inventory data
                        }}
                        onCancel={() => {
                            setShowStockAdjustmentModal(false);
                            setSelectedInventoryItemForAdjustment(null);
                        }}
                        API_BASE_URL={API_BASE_URL}
                        parts={parts} // Pass parts list
                        organizations={organizations} // Pass organizations list
                    />
                </Modal>
            )}

            {/* Supplier Orders Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Supplier Orders</h2>
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager") && (
                    <button
                        onClick={() => {
                            setEditingSupplierOrder(null);
                            setShowSupplierOrderModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Supplier Order
                    </button>
                )}
            </div>
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

            {/* Modal for Supplier Order Form */}
            <Modal
                show={showSupplierOrderModal}
                onClose={() => setShowSupplierOrderModal(false)}
                title={editingSupplierOrder ? "Edit Supplier Order" : "Add New Supplier Order"}
            >
                <SupplierOrderForm
                    initialData={editingSupplierOrder || {}}
                    organizations={organizations}
                    onSubmit={handleCreateSupplierOrder}
                    onClose={() => setShowSupplierOrderModal(false)}
                />
            </Modal>

            {/* Supplier Order Items Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Supplier Order Items</h2>
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager") && (
                    <button
                        onClick={() => {
                            setEditingSupplierOrderItem(null);
                            setShowSupplierOrderItemModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Item to Order
                    </button>
                )}
            </div>
            {supplierOrderItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No supplier order items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {supplierOrderItems.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-pink-700 mb-2">{getPartName(item.part_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity:</span> {item.quantity}</p>
                    {item.unit_price && <p className="text-gray-600 mb-1"><span className="font-medium">Unit Price:</span> ${item.unit_price}</p>}
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order:</span> {getSupplierOrderDetails(item.supplier_order_id)}</p>
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Supplier Order Item Form */}
            <Modal
                show={showSupplierOrderItemModal}
                onClose={() => setShowSupplierOrderItemModal(false)}
                title={editingSupplierOrderItem ? "Edit Supplier Order Item" : "Add New Supplier Order Item"}
            >
                <SupplierOrderItemForm
                    initialData={editingSupplierOrderItem || {}}
                    supplierOrders={supplierOrders}
                    parts={parts}
                    onSubmit={handleCreateSupplierOrderItem}
                    onClose={() => setShowSupplierOrderItemModal(false)}
                />
            </Modal>


            {/* Customer Orders Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Customer Orders</h2>
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager" || user.role === "Customer Admin" || user.role === "Customer User") && (
                    <button
                        onClick={() => {
                            setEditingCustomerOrder(null);
                            setShowCustomerOrderModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Customer Order
                    </button>
                )}
            </div>
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

            {/* Modal for Customer Order Form */}
            <Modal
                show={showCustomerOrderModal}
                onClose={() => setShowCustomerOrderModal(false)}
                title={editingCustomerOrder ? "Edit Customer Order" : "Add New Customer Order"}
            >
                <CustomerOrderForm
                    initialData={editingCustomerOrder || {}}
                    organizations={organizations}
                    users={users}
                    onSubmit={handleCreateCustomerOrder}
                    onClose={() => setShowCustomerOrderModal(false)}
                />
            </Modal>

            {/* Customer Order Items Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Customer Order Items</h2>
                {(user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager" || user.role === "Customer Admin" || user.role === "Customer User") && (
                    <button
                        onClick={() => {
                            setEditingCustomerOrderItem(null);
                            setShowCustomerOrderItemModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Item to Customer Order
                    </button>
                )}
            </div>
            {customerOrderItems.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No customer order items found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {customerOrderItems.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-teal-700 mb-2">{getPartName(item.part_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity:</span> {item.quantity}</p>
                    {item.unit_price && <p className="text-gray-600 mb-1"><span className="font-medium">Unit Price:</span> ${item.unit_price}</p>}
                    <p className="text-gray-600 mb-1"><span className="font-medium">Order:</span> {getCustomerOrderDetails(item.customer_order_id)}</p>
                    <p className="text-sm text-gray-400 mt-3">ID: {item.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Customer Order Item Form */}
            <Modal
                show={showCustomerOrderItemModal}
                onClose={() => setShowCustomerOrderItemModal(false)}
                title={editingCustomerOrderItem ? "Edit Customer Order Item" : "Add New Customer Order Item"}
            >
                <CustomerOrderItemForm
                    initialData={editingCustomerOrderItem || {}}
                    customerOrders={customerOrders}
                    parts={parts}
                    onSubmit={handleCreateCustomerOrderItem}
                    onClose={() => setShowCustomerOrderItemModal(false)}
                />
            </Modal>

            {/* Part Usage Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Part Usage</h2>
                {(user.role === "Oraseas Admin" || user.role === "Customer Admin" || user.role === "Customer User") && (
                    <button
                        onClick={() => {
                            setEditingPartUsage(null);
                            setShowPartUsageModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Record Part Usage
                    </button>
                )}
            </div>
            {partUsages.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No part usage records found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {partUsages.map((usage) => (
                    <div key={usage.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-fuchsia-700 mb-2">{getPartName(usage.part_id)} used by {getCustomerOrganizationDetails(usage.customer_organization_id)}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Quantity Used:</span> {usage.quantity_used}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Usage Date:</span> {new Date(usage.usage_date).toLocaleDateString()}</p>
                    {usage.machine_id && <p className="text-gray-600 mb-1"><span className="font-medium">Machine ID:</span> {usage.machine_id}</p>}
                    {usage.recorded_by_user_id && <p className="text-gray-600 mb-1"><span className="font-medium">Recorded By:</span> {getUserName(usage.recorded_by_user_id)}</p>}
                    <p className="text-sm text-gray-400 mt-3">ID: {usage.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Part Usage Form */}
            <Modal
                show={showPartUsageModal}
                onClose={() => setShowPartUsageModal(false)}
                title={editingPartUsage ? "Edit Part Usage" : "Record New Part Usage"}
            >
                <PartUsageForm
                    initialData={editingPartUsage || {}}
                    organizations={organizations} // Pass organizations for dropdowns
                    parts={parts} // Pass parts for dropdown
                    users={users} // Pass users for dropdown
                    onSubmit={handleCreatePartUsage}
                    onClose={() => setShowPartUsageModal(false)}
                />
            </Modal>

            {/* Modal for Stocktake Worksheet Generator */}
            <Modal
                show={showStocktakeSheetGenerator}
                onClose={() => setShowStocktakeSheetGenerator(false)}
                title="Generate Stocktake Worksheet"
                isLarge={stocktakeWorksheetData && stocktakeWorksheetData.length > 0} // Make modal larger if data is shown
            >
                <div className="p-4">
                    <StocktakeWorksheetGenerator
                        organizations={organizations}
                        API_BASE_URL={API_BASE_URL}
                        onWorksheetGenerated={setStocktakeWorksheetData}
                        onLoadingChange={setLoadingStocktakeWorksheet}
                    />

                    {loadingStocktakeWorksheet && <p className="mt-4 text-center">Loading worksheet...</p>}

                    {!loadingStocktakeWorksheet && stocktakeWorksheetData && stocktakeWorksheetData.length > 0 && (
                        <div className="mt-6">
                            <div className="flex justify-between items-center mb-3">
                                <h4 className="text-xl font-semibold">Generated Worksheet</h4>
                                <button
                                    onClick={() => {
                                        // Simpler filename for now, will use selectedInventoryOrgFilter if available and matches current data context
                                        // This assumes stocktakeWorksheetData is generated for the currently selected filter,
                                        // or we need a more robust way to track which org the data is for.
                                        // For US-INV003, the worksheet is generated for a specific org chosen in its own UI.
                                        // We need to retrieve that specific org ID.
                                        // For now, let's use a generic name or find it if possible.
                                        // The StocktakeWorksheetGenerator component holds selectedOrgId. We'd need to lift state or pass it back.

                                        // To make this work without major refactor NOW, we'll use a generic name.
                                        // A better solution would be to have selectedOrgId for the worksheet available in App.js state.
                                        const orgName = "Stocktake"; // Generic name
                                        const date = new Date().toISOString().split('T')[0];

                                        let csvContent = "data:text/csv;charset=utf-8,";
                                        csvContent += "Part Number,Part Name,System Quantity,Counted Quantity\r\n"; // Headers

                                        stocktakeWorksheetData.forEach(item => {
                                            csvContent += `${item.part_number},"${item.part_name.replace(/"/g, '""')}",${item.system_quantity},\r\n`; // Last column empty for "Counted Quantity"
                                        });

                                        const encodedUri = encodeURI(csvContent);
                                        const link = document.createElement("a");
                                        link.setAttribute("href", encodedUri);
                                        link.setAttribute("download", `stocktake_worksheet_${orgName}_${date}.csv`);
                                        document.body.appendChild(link); // Required for FF
                                        link.click();
                                        document.body.removeChild(link);
                                    }}
                                    className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2 px-4 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 transition duration-150 ease-in-out"
                                >
                                    Export to CSV
                                </button>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200 border border-gray-300">
                                    <thead className="bg-gray-100">
                                        <tr>
                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Part #</th>
                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Part Name</th>
                                            <th className="px-4 py-2 text-right text-xs font-medium text-gray-600 uppercase tracking-wider">System Qty</th>
                                            <th className="px-4 py-2 text-left text-xs font-medium text-gray-600 uppercase tracking-wider border-l-2 border-gray-300 bg-gray-200">Counted Qty</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {stocktakeWorksheetData.map((item) => (
                                            <tr key={item.part_id}>
                                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{item.part_number}</td>
                                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700">{item.part_name}</td>
                                                <td className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 text-right">{item.system_quantity}</td>
                                                <td className="px-4 py-2 whitespace-nowrap border-l-2 border-gray-300 bg-gray-50"> {/* Empty cell for manual entry */} </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                    {!loadingStocktakeWorksheet && stocktakeWorksheetData && stocktakeWorksheetData.length === 0 && (
                        <p className="mt-4 text-center text-gray-600">No inventory items found for the selected organization, or worksheet not yet generated.</p>
                    )}
                </div>
            </Modal>


            {/* Machines Section */}
            <div className="flex justify-between items-center mb-6 border-b-2 pb-2">
                <h2 className="text-3xl font-bold text-gray-700">Machines</h2>
                {(user.role === "Oraseas Admin" || user.role === "Customer Admin") && ( // Oraseas Admin or Customer Admin can add machines
                    <button
                        onClick={() => {
                            setEditingMachine(null);
                            setShowMachineModal(true);
                        }}
                        className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-150 ease-in-out font-semibold"
                    >
                        Add Machine
                    </button>
                )}
            </div>
            {machines.length === 0 ? (
                <p className="text-center text-gray-600 text-lg">No machines found or unauthorized to view.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {machines.map((machine) => (
                    <div key={machine.id} className="bg-gray-50 p-6 rounded-lg shadow-md border border-gray-200">
                    <h3 className="text-2xl font-semibold text-cyan-700 mb-2">{machine.name}</h3>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Model:</span> {machine.model_type}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Serial #:</span> {machine.serial_number}</p>
                    <p className="text-gray-600 mb-1"><span className="font-medium">Organization:</span> {getOrganizationName(machine.organization_id)}</p>
                    <p className="text-sm text-gray-400 mt-3">ID: {machine.id}</p>
                    </div>
                ))}
                </div>
            )}

            {/* Modal for Machine Form */}
            <Modal
                show={showMachineModal}
                onClose={() => setShowMachineModal(false)}
                title={editingMachine ? "Edit Machine" : "Add New Machine"}
            >
                <MachineForm
                    initialData={editingMachine || {}}
                    organizations={organizations}
                    onSubmit={handleCreateMachine}
                    onClose={() => setShowMachineModal(false)}
                />
            </Modal>
            </>
        )}
        </div>
    </div>
    );
}

export default App;

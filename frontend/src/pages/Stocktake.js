import React, { useState, useEffect, useCallback } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';
import { warehouseService } from '../services/warehouseService';
import { useAuth } from '../AuthContext';
import Modal from '../components/Modal';
import StocktakeForm from '../components/StocktakeForm';
import StocktakeDetails from '../components/StocktakeDetails';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';

const Stocktake = () => {
    const { user } = useAuth();
    const [stocktakes, setStocktakes] = useState([]);
    const [warehouses, setWarehouses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [selectedStocktake, setSelectedStocktake] = useState(null);
    const [filters, setFilters] = useState({
        warehouse_id: '',
        status: '',
    });

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const [stocktakesData, warehousesData] = await Promise.all([
                inventoryWorkflowService.getStocktakes(filters),
                warehouseService.getWarehouses()
            ]);

            setStocktakes(Array.isArray(stocktakesData) ? stocktakesData : []);
            setWarehouses(Array.isArray(warehousesData) ? warehousesData : []);
        } catch (err) {
            console.error('Failed to fetch stocktake data:', err);
            setError(err.message || 'Failed to fetch stocktake data.');
            setStocktakes([]);
            setWarehouses([]);
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleCreateStocktake = async (stocktakeData) => {
        try {
            await inventoryWorkflowService.createStocktake(stocktakeData);
            setShowCreateModal(false);
            fetchData(); // Refresh the list
        } catch (err) {
            throw err; // Let the form handle the error
        }
    };

    const handleViewStocktake = (stocktake) => {
        setSelectedStocktake(stocktake);
        setShowDetailsModal(true);
    };

    const handleDeleteStocktake = async (stocktakeId) => {
        if (!window.confirm('Are you sure you want to delete this stocktake?')) {
            return;
        }

        try {
            await inventoryWorkflowService.deleteStocktake(stocktakeId);
            fetchData(); // Refresh the list
        } catch (err) {
            setError(err.message || 'Failed to delete stocktake.');
        }
    };

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'planned': return 'bg-blue-100 text-blue-800';
            case 'in_progress': return 'bg-yellow-100 text-yellow-800';
            case 'completed': return 'bg-green-100 text-green-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const canCreateStocktake = user && (user.role === 'admin' || user.role === 'super_admin');
    const canDeleteStocktake = user && (user.role === 'admin' || user.role === 'super_admin');

    return (
        <PermissionGuard permission={PERMISSIONS.ADJUST_INVENTORY}>
            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">Stocktake Management</h1>
                        <p className="text-gray-600 mt-1">Plan, execute, and manage inventory stocktakes</p>
                    </div>
                    {canCreateStocktake && (
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 font-semibold"
                        >
                            Create Stocktake
                        </button>
                    )}
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                        <strong className="font-bold">Error: </strong>
                        <span className="block sm:inline">{error}</span>
                    </div>
                )}

                {/* Filters */}
                <div className="bg-white p-4 rounded-lg shadow-md">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Filters</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label htmlFor="warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
                                Warehouse
                            </label>
                            <select
                                id="warehouse_id"
                                name="warehouse_id"
                                value={filters.warehouse_id}
                                onChange={handleFilterChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="">All Warehouses</option>
                                {Array.isArray(warehouses) && warehouses.map(warehouse => (
                                    <option key={warehouse.id} value={warehouse.id}>
                                        {warehouse.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
                                Status
                            </label>
                            <select
                                id="status"
                                name="status"
                                value={filters.status}
                                onChange={handleFilterChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="">All Statuses</option>
                                <option value="planned">Planned</option>
                                <option value="in_progress">In Progress</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Stocktakes List */}
                <div className="bg-white rounded-lg shadow-md overflow-hidden">
                    {loading ? (
                        <div className="p-6 text-center text-gray-500">Loading stocktakes...</div>
                    ) : stocktakes.length === 0 ? (
                        <div className="p-6 text-center text-gray-500">
                            No stocktakes found. {canCreateStocktake && 'Create your first stocktake to get started.'}
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Warehouse
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Scheduled Date
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Progress
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Scheduled By
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {stocktakes.map((stocktake) => (
                                        <tr key={stocktake.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                <div>
                                                    <div className="font-medium">{stocktake.warehouse_name}</div>
                                                    <div className="text-gray-500">{stocktake.organization_name}</div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {formatDate(stocktake.scheduled_date)}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(stocktake.status)}`}>
                                                    {stocktake.status.replace('_', ' ').toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {stocktake.items_counted || 0} / {stocktake.total_items || 0} items
                                                {stocktake.discrepancy_count > 0 && (
                                                    <div className="text-red-600 text-xs">
                                                        {stocktake.discrepancy_count} discrepancies
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {stocktake.scheduled_by_username}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                                                <button
                                                    onClick={() => handleViewStocktake(stocktake)}
                                                    className="text-blue-600 hover:text-blue-900"
                                                >
                                                    View
                                                </button>
                                                {canDeleteStocktake && stocktake.status === 'planned' && (
                                                    <button
                                                        onClick={() => handleDeleteStocktake(stocktake.id)}
                                                        className="text-red-600 hover:text-red-900"
                                                    >
                                                        Delete
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Create Stocktake Modal */}
                <Modal
                    isOpen={showCreateModal}
                    onClose={() => setShowCreateModal(false)}
                    title="Create New Stocktake"
                    size="lg"
                >
                    <StocktakeForm
                        warehouses={warehouses}
                        onSubmit={handleCreateStocktake}
                        onClose={() => setShowCreateModal(false)}
                    />
                </Modal>

                {/* Stocktake Details Modal */}
                <Modal
                    isOpen={showDetailsModal}
                    onClose={() => setShowDetailsModal(false)}
                    title="Stocktake Details"
                    size="xl"
                >
                    {selectedStocktake && (
                        <StocktakeDetails
                            stocktake={selectedStocktake}
                            onClose={() => setShowDetailsModal(false)}
                            onUpdate={fetchData}
                        />
                    )}
                </Modal>
            </div>
        </PermissionGuard>
    );
};

export default Stocktake;
// frontend/src/components/MachineDetails.js

import React, { useState, useEffect, useCallback } from 'react';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';
import { getContextualPermissions } from '../utils/permissions';
import Modal from './Modal';
import MaintenanceForm from './MaintenanceForm';
import PartUsageChart from './PartUsageChart';
import MaintenanceSchedule from './MaintenanceSchedule';

const MachineDetails = ({ machineId, onClose }) => {
  const [machine, setMachine] = useState(null);
  const [maintenanceHistory, setMaintenanceHistory] = useState([]);
  const [usageHistory, setUsageHistory] = useState([]);
  const [compatibleParts, setCompatibleParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);

  const { user } = useAuth();
  const permissions = getContextualPermissions(user, 'machines');

  const fetchMachineData = useCallback(async () => {
    if (!machineId) return;

    setLoading(true);
    setError(null);

    try {
      const [machineData, maintenanceData, usageData, partsData] = await Promise.all([
        machinesService.getMachine(machineId),
        machinesService.getMaintenanceHistory(machineId),
        machinesService.getUsageHistory(machineId),
        machinesService.getCompatibleParts(machineId)
      ]);

      setMachine(machineData);
      setMaintenanceHistory(maintenanceData);
      setUsageHistory(usageData);
      setCompatibleParts(partsData);
    } catch (err) {
      setError(err.message || 'Failed to fetch machine data');
    } finally {
      setLoading(false);
    }
  }, [machineId]);

  useEffect(() => {
    fetchMachineData();
  }, [fetchMachineData]);

  const handleMaintenanceSubmit = async (maintenanceData) => {
    try {
      await machinesService.createMaintenanceRecord(machineId, maintenanceData);
      await fetchMachineData(); // Refresh data
      setShowMaintenanceModal(false);
    } catch (err) {
      throw err; // Re-throw for form error handling
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-yellow-100 text-yellow-800';
      case 'maintenance': return 'bg-blue-100 text-blue-800';
      case 'decommissioned': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (!machine) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Machine not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">{machine.name}</h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span><strong>Model:</strong> {machine.model_type}</span>
              <span><strong>Serial:</strong> {machine.serial_number}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(machine.status)}`}>
                {machine.status || 'Active'}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            {permissions.canManage && (
              <button
                onClick={() => setShowMaintenanceModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
              >
                Add Maintenance
              </button>
            )}
            <button
              onClick={onClose}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'maintenance', label: 'Maintenance History' },
              { id: 'usage', label: 'Parts Usage' },
              { id: 'performance', label: 'Performance' },
              { id: 'schedule', label: 'Maintenance Schedule' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Machine Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Purchase Date:</span>
                    <span className="font-medium">{formatDate(machine.purchase_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Warranty Expiry:</span>
                    <span className="font-medium">{formatDate(machine.warranty_expiry_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last Maintenance:</span>
                    <span className="font-medium">{formatDate(machine.last_maintenance_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Next Maintenance:</span>
                    <span className="font-medium">{formatDate(machine.next_maintenance_date)}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Quick Stats</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{maintenanceHistory.length}</div>
                    <div className="text-sm text-gray-600">Maintenance Records</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{usageHistory.length}</div>
                    <div className="text-sm text-gray-600">Parts Used</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{compatibleParts.length}</div>
                    <div className="text-sm text-gray-600">Compatible Parts</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {machine.warranty_expiry_date && new Date(machine.warranty_expiry_date) > new Date() ? 'Active' : 'Expired'}
                    </div>
                    <div className="text-sm text-gray-600">Warranty Status</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Maintenance History Tab */}
          {activeTab === 'maintenance' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Maintenance History</h3>
                {permissions.canManage && (
                  <button
                    onClick={() => setShowMaintenanceModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                  >
                    Add Maintenance Record
                  </button>
                )}
              </div>

              {maintenanceHistory.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No maintenance records found
                </div>
              ) : (
                <div className="space-y-4">
                  {maintenanceHistory.map((record) => (
                    <div key={record.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-semibold text-gray-800">{record.maintenance_type}</h4>
                          <p className="text-sm text-gray-600">{formatDate(record.maintenance_date)}</p>
                        </div>
                        <span className="text-sm text-gray-500">
                          Duration: {record.duration_hours || 'N/A'} hours
                        </span>
                      </div>
                      {record.description && (
                        <p className="text-gray-700 mb-2">{record.description}</p>
                      )}
                      {record.cost && (
                        <p className="text-sm text-gray-600">Cost: ${record.cost}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Parts Usage Tab */}
          {activeTab === 'usage' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Parts Usage History</h3>
              {usageHistory.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No parts usage records found
                </div>
              ) : (
                <>
                  <PartUsageChart usageData={usageHistory} />
                  <div className="mt-6 space-y-4">
                    {usageHistory.map((usage) => (
                      <div key={usage.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-semibold text-gray-800">{usage.part_name}</h4>
                            <p className="text-sm text-gray-600">{formatDate(usage.usage_date)}</p>
                          </div>
                          <div className="text-right">
                            <span className="font-medium">{usage.quantity} {usage.unit_of_measure}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Machine Performance Analytics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Maintenance Frequency</h4>
                  <p className="text-2xl font-bold text-blue-600">
                    {maintenanceHistory.length > 0 ?
                      Math.round(365 / (maintenanceHistory.length || 1)) : 0} days
                  </p>
                  <p className="text-sm text-gray-600">Average between maintenance</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Parts Consumption</h4>
                  <p className="text-2xl font-bold text-green-600">
                    {usageHistory.reduce((sum, usage) => sum + parseFloat(usage.quantity || 0), 0).toFixed(1)}
                  </p>
                  <p className="text-sm text-gray-600">Total parts consumed</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Maintenance Cost</h4>
                  <p className="text-2xl font-bold text-purple-600">
                    ${maintenanceHistory.reduce((sum, record) => sum + parseFloat(record.cost || 0), 0).toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-600">Total maintenance cost</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Uptime</h4>
                  <p className="text-2xl font-bold text-yellow-600">
                    {machine.status === 'active' ? '98.5%' : '0%'}
                  </p>
                  <p className="text-sm text-gray-600">Estimated uptime</p>
                </div>
              </div>
            </div>
          )}

          {/* Maintenance Schedule Tab */}
          {activeTab === 'schedule' && (
            <MaintenanceSchedule
              machine={machine}
              maintenanceHistory={maintenanceHistory}
              onScheduleUpdate={fetchMachineData}
            />
          )}
        </div>
      </div>

      {/* Maintenance Modal */}
      <Modal
        isOpen={showMaintenanceModal}
        onClose={() => setShowMaintenanceModal(false)}
        title="Add Maintenance Record"
      >
        <MaintenanceForm
          machineId={machineId}
          onSubmit={handleMaintenanceSubmit}
          onClose={() => setShowMaintenanceModal(false)}
        />
      </Modal>
    </div>
  );
};

export default MachineDetails;
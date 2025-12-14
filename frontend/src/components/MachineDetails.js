// frontend/src/components/MachineDetails.js

import React, { useState, useEffect, useCallback } from 'react';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { getContextualPermissions } from '../utils/permissions';
import Modal from './Modal';
import MaintenanceForm from './MaintenanceForm';
import PartUsageChart from './PartUsageChart';
import MaintenanceSchedule from './MaintenanceSchedule';
import PartUsageHistory from './PartUsageHistory';

const MachineDetails = ({ machineId, onClose }) => {
  const [machine, setMachine] = useState(null);
  const [maintenanceHistory, setMaintenanceHistory] = useState([]);
  const [usageHistory, setUsageHistory] = useState([]);
  const [compatibleParts, setCompatibleParts] = useState([]);
  const [machineHours, setMachineHours] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showMaintenanceModal, setShowMaintenanceModal] = useState(false);

  const { user } = useAuth();
  const { t } = useTranslation();
  const permissions = getContextualPermissions(user, 'machines');

  const fetchMachineData = useCallback(async () => {
    if (!machineId) return;

    setLoading(true);
    setError(null);

    try {
      const [machineData, maintenanceData, usageData, partsData, hoursData] = await Promise.all([
        machinesService.getMachine(machineId),
        machinesService.getMaintenanceHistory(machineId),
        machinesService.getUsageHistory(machineId),
        machinesService.getCompatibleParts(machineId),
        machinesService.getMachineHours(machineId)
      ]);

      setMachine(machineData);
      setMaintenanceHistory(maintenanceData);
      setUsageHistory(usageData);
      setCompatibleParts(partsData);
      setMachineHours(hoursData);
    } catch (err) {
      setError(err.message || t('machineDetails.failedToFetchData'));
    } finally {
      setLoading(false);
    }
  }, [machineId, t]);

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
    if (!dateString) return t('common.na');
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
        <strong className="font-bold">{t('common.error')}: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (!machine) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">{t('machineDetails.machineNotFound')}</p>
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
              <span><strong>{t('machines.model')}:</strong> {machine.model_type}</span>
              <span><strong>{t('machines.serial')}:</strong> {machine.serial_number}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(machine.status)}`}>
                {t(`machines.status.${machine.status || 'active'}`)}
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            {permissions.canManage && (
              <button
                onClick={() => setShowMaintenanceModal(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
              >
                {t('machineDetails.addMaintenance')}
              </button>
            )}
            <button
              onClick={onClose}
              className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 text-sm"
            >
              {t('common.close')}
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-md mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'overview', label: t('machineDetails.tabs.overview') },
              { id: 'hours', label: t('machineDetails.tabs.machineHours') },
              { id: 'maintenance', label: t('machineDetails.tabs.maintenanceHistory') },
              { id: 'usage', label: t('machineDetails.tabs.partsUsage') },
              { id: 'performance', label: t('machineDetails.tabs.performance') },
              { id: 'schedule', label: t('machineDetails.tabs.maintenanceSchedule') }
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
                <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('machineDetails.machineInformation')}</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('machineDetails.purchaseDate')}:</span>
                    <span className="font-medium">{formatDate(machine.purchase_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('machineDetails.warrantyExpiry')}:</span>
                    <span className="font-medium">{formatDate(machine.warranty_expiry_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('machines.lastMaintenance')}:</span>
                    <span className="font-medium">{formatDate(machine.last_maintenance_date)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{t('machineDetails.nextMaintenance')}:</span>
                    <span className="font-medium">{formatDate(machine.next_maintenance_date)}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('machineDetails.quickStats')}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{maintenanceHistory.length}</div>
                    <div className="text-sm text-gray-600">{t('machineDetails.maintenanceRecords')}</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{usageHistory.length}</div>
                    <div className="text-sm text-gray-600">{t('machineDetails.partsUsed')}</div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{compatibleParts.length}</div>
                    <div className="text-sm text-gray-600">{t('machineDetails.compatibleParts')}</div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {machine.warranty_expiry_date && new Date(machine.warranty_expiry_date) > new Date() ? t('machineDetails.warrantyActive') : t('machineDetails.warrantyExpired')}
                    </div>
                    <div className="text-sm text-gray-600">{t('machineDetails.warrantyStatus')}</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Machine Hours Tab */}
          {activeTab === 'hours' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('machineDetails.machineHoursLog')}</h3>
              
              {machineHours.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  {t('machines.noHoursRecorded')}
                </div>
              ) : (
                <div>
                  {/* Summary Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {machineHours[0]?.hours_value?.toLocaleString() || 0} {t('machines.hrs')}
                      </div>
                      <div className="text-sm text-gray-600">{t('machines.latestHours')}</div>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {machineHours.length}
                      </div>
                      <div className="text-sm text-gray-600">{t('machineDetails.totalRecords')}</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {machineHours.length > 1 
                          ? (machineHours[0]?.hours_value - machineHours[machineHours.length - 1]?.hours_value).toLocaleString()
                          : 0} {t('machines.hrs')}
                      </div>
                      <div className="text-sm text-gray-600">{t('machineDetails.totalAccumulated')}</div>
                    </div>
                  </div>

                  {/* Hours History Table */}
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {t('machineDetails.dateTime')}
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {t('machineDetails.hoursValue')}
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {t('maintenance.performedBy')}
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            {t('maintenance.notes')}
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {machineHours.map((record, index) => (
                          <tr key={record.id} className={index === 0 ? 'bg-blue-50' : ''}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {new Date(record.recorded_date).toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className="text-lg font-semibold text-gray-900">
                                {record.hours_value?.toLocaleString()} {t('machines.hrs')}
                              </span>
                              {index > 0 && (
                                <span className="ml-2 text-xs text-gray-500">
                                  (+{(record.hours_value - machineHours[index - 1]?.hours_value).toLocaleString()})
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {record.recorded_by_username || t('common.unknown')}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {record.notes || '-'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Maintenance History Tab */}
          {activeTab === 'maintenance' && (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">{t('machineDetails.tabs.maintenanceHistory')}</h3>
                {permissions.canManage && (
                  <button
                    onClick={() => setShowMaintenanceModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                  >
                    {t('machineDetails.addMaintenanceRecord')}
                  </button>
                )}
              </div>

              {maintenanceHistory.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  {t('machineDetails.noMaintenanceRecords')}
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
                          {t('machineDetails.duration')}: {record.duration_hours || 'N/A'} {t('maintenance.hours')}
                        </span>
                      </div>
                      {record.description && (
                        <p className="text-gray-700 mb-2">{record.description}</p>
                      )}
                      {record.cost && (
                        <p className="text-sm text-gray-600">{t('machineDetails.cost')}: ${record.cost}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Parts Usage Tab */}
          {activeTab === 'usage' && (
            <div className="space-y-6">
              {/* Chart */}
              {usageHistory.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('machineDetails.usageChart')}</h3>
                  <PartUsageChart usageData={usageHistory} />
                </div>
              )}
              
              {/* Detailed History with Delete */}
              <PartUsageHistory 
                machineId={machineId} 
                onUsageDeleted={fetchMachineData}
              />
            </div>
          )}

          {/* Performance Tab */}
          {activeTab === 'performance' && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">{t('machineDetails.performanceAnalytics')}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">{t('machineDetails.maintenanceFrequency')}</h4>
                  <p className="text-2xl font-bold text-blue-600">
                    {maintenanceHistory.length > 0 ?
                      Math.round(365 / (maintenanceHistory.length || 1)) : 0} {t('machineDetails.days')}
                  </p>
                  <p className="text-sm text-gray-600">{t('machineDetails.averageBetweenMaintenance')}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">{t('machineDetails.partsConsumption')}</h4>
                  <p className="text-2xl font-bold text-green-600">
                    {usageHistory.reduce((sum, usage) => sum + parseFloat(usage.quantity || 0), 0).toFixed(1)}
                  </p>
                  <p className="text-sm text-gray-600">{t('machineDetails.totalPartsConsumed')}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">{t('machineDetails.maintenanceCost')}</h4>
                  <p className="text-2xl font-bold text-purple-600">
                    ${maintenanceHistory.reduce((sum, record) => sum + parseFloat(record.cost || 0), 0).toFixed(2)}
                  </p>
                  <p className="text-sm text-gray-600">{t('machineDetails.totalMaintenanceCost')}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">{t('machineDetails.uptime')}</h4>
                  <p className="text-2xl font-bold text-yellow-600">
                    {machine.status === 'active' ? '98.5%' : '0%'}
                  </p>
                  <p className="text-sm text-gray-600">{t('machineDetails.estimatedUptime')}</p>
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
        title={t('machineDetails.addMaintenanceRecord')}
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
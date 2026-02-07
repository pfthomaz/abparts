import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { useOffline } from '../contexts/OfflineContext';
import { machinesService } from '../services/machinesService';
import { getLocalizedProtocols, createExecution, getExecutions } from '../services/maintenanceProtocolsService';
import { getUnsyncedMaintenanceExecutions } from '../db/indexedDB';
import ExecutionForm from '../components/ExecutionForm';
import ExecutionHistory from '../components/ExecutionHistory';


const MaintenanceExecutions = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const { isOnline, pendingCount } = useOffline();
  const location = useLocation();
  const navigate = useNavigate();
  const [machines, setMachines] = useState([]);
  const [protocols, setProtocols] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [offlineExecutions, setOfflineExecutions] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [showExecutionForm, setShowExecutionForm] = useState(false);
  const [resumingExecution, setResumingExecution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('new'); // 'new' or 'history'

  // Define loadData function first
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load data with individual error handling to prevent one failure from blocking everything
      let machinesData = [];
      let protocolsData = [];
      let executionsData = [];
      
      try {
        machinesData = await machinesService.getMachines();
        // console.log('[MaintenanceExecutions] Loaded machines:', machinesData.length);
      } catch (err) {
        console.error('[MaintenanceExecutions] Failed to load machines:', err);
        setError('Failed to load machines. Please refresh the page.');
      }
      
      try {
        protocolsData = await getLocalizedProtocols({}, user.preferred_language);
        // console.log('[MaintenanceExecutions] Loaded protocols:', protocolsData.length);
      } catch (err) {
        console.error('[MaintenanceExecutions] Failed to load protocols:', err);
        // Don't set error here - protocols might be cached
        if (!error) {
          setError('Failed to load protocols. Using cached data if available.');
        }
      }
      
      try {
        executionsData = await getExecutions();
        // console.log('[MaintenanceExecutions] Loaded executions:', executionsData.length);
      } catch (err) {
        console.error('[MaintenanceExecutions] Failed to load executions:', err);
        // Don't block the page if executions fail to load
      }
      
      setMachines(machinesData);
      setProtocols(protocolsData.filter(p => p.is_active));
      setExecutions(executionsData);
      
      // Load offline executions
      try {
        const unsyncedExecutions = await getUnsyncedMaintenanceExecutions();
        setOfflineExecutions(unsyncedExecutions);
        // console.log('[MaintenanceExecutions] Loaded offline executions:', unsyncedExecutions.length);
      } catch (err) {
        console.error('[MaintenanceExecutions] Failed to load offline executions:', err);
      }
      
      // Auto-select machine if there's only one
      if (machinesData.length === 1 && !selectedMachine) {
        setSelectedMachine(machinesData[0]);
      }
      
    } catch (err) {
      console.error('[MaintenanceExecutions] Error loading data:', err);
      setError(err.message || 'Failed to load data. Please refresh the page.');
    } finally {
      setLoading(false);
    }
  }, [user.preferred_language, selectedMachine]);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Listen for sync completion to refresh executions
  useEffect(() => {
    const handleSyncComplete = (event) => {
      // console.log('[MaintenanceExecutions] Sync completed, reloading executions...', event.detail);
      // Force reload after a short delay to ensure backend has processed
      setTimeout(() => {
        loadData();
      }, 500);
    };
    
    window.addEventListener('offline-sync-complete', handleSyncComplete);
    
    return () => {
      window.removeEventListener('offline-sync-complete', handleSyncComplete);
    };
  }, [loadData]);

  // Load offline executions when pendingCount changes
  useEffect(() => {
    const loadOfflineExecutions = async () => {
      const unsynced = await getUnsyncedMaintenanceExecutions();
      setOfflineExecutions(unsynced);
      // console.log('[MaintenanceExecutions] Loaded offline executions:', unsynced.length);
    };
    loadOfflineExecutions();
  }, [pendingCount]);

  // Handle preselected machine/protocol from navigation state
  useEffect(() => {
    if (location.state?.resumeExecution) {
      // Resume an ongoing execution
      const execution = location.state.resumeExecution;
      setSelectedMachine(execution.machine);
      setSelectedProtocol(execution.protocol);
      setResumingExecution(execution);
      setShowExecutionForm(true);
    } else if (location.state?.preselectedMachine && location.state?.preselectedProtocol) {
      // Start new execution
      setSelectedMachine(location.state.preselectedMachine);
      setSelectedProtocol(location.state.preselectedProtocol);
      setShowExecutionForm(true);
    }
  }, [location.state]);

  const handleStartExecution = () => {
    if (!selectedMachine) {
      alert(t('maintenance.pleaseSelectMachine'));
      return;
    }
    if (!selectedProtocol) {
      alert(t('maintenance.pleaseSelectProtocol'));
      return;
    }
    setShowExecutionForm(true);
  };

  const handleResumeExecution = (execution) => {
    // console.log('Resuming execution:', execution);
    setSelectedMachine(execution.machine);
    setSelectedProtocol(execution.protocol);
    setResumingExecution(execution);
    setShowExecutionForm(true);
  };

  const handleExecutionComplete = () => {
    // If we came from DailyOperations, navigate back with the machine selected
    if (location.state?.sessionType) {
      navigate('/daily-operations', {
        state: {
          selectedMachineId: selectedMachine?.id
        }
      });
    } else {
      setShowExecutionForm(false);
      setSelectedMachine(null);
      setSelectedProtocol(null);
      setResumingExecution(null);
      loadData();
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (showExecutionForm) {
    return (
      <ExecutionForm
        machine={selectedMachine}
        protocol={selectedProtocol}
        existingExecution={resumingExecution}
        onComplete={handleExecutionComplete}
        onCancel={() => {
          setShowExecutionForm(false);
          setSelectedMachine(null);
          setSelectedProtocol(null);
          setResumingExecution(null);
        }}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">{t('maintenance.title')}</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Pending Offline Executions Banner */}
      {offlineExecutions.length > 0 && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-md shadow-sm">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-blue-800">
                {t('maintenance.pendingSync', { count: offlineExecutions.length })}
              </h3>
              <p className="mt-1 text-sm text-blue-700">
                {t('maintenance.pendingSyncMessage') || 'These maintenance executions were recorded offline and will sync when connection is restored.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Incomplete Daily Protocols Banner */}
      {[...executions, ...offlineExecutions].filter(e => 
        e.status === 'in_progress' && 
        e.protocol?.protocol_type === 'daily'
      ).length > 0 && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded-md shadow-sm">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-orange-800">
                {t('maintenance.incompleteDailyProtocols')}
              </h3>
              <div className="mt-2 text-sm text-orange-700">
                <p>{t('maintenance.incompleteDailyProtocolsMessage')}</p>
                <div className="mt-3 space-y-2">
                  {[...executions, ...offlineExecutions]
                    .filter(e => e.status === 'in_progress' && e.protocol?.protocol_type === 'daily')
                    .map(execution => (
                      <div key={execution.id || execution.tempId} className="flex items-center justify-between bg-white p-2 rounded">
                        <span className="font-medium">
                          {execution.protocol?.name} - {execution.machine?.name || execution.machine?.serial_number}
                          {execution.tempId && (
                            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              {t('maintenance.pendingSync')}
                            </span>
                          )}
                        </span>
                        <button
                          onClick={() => handleResumeExecution(execution)}
                          className="px-3 py-1 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm"
                        >
                          {t('maintenance.resumeNow')}
                        </button>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('new')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'new'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('maintenance.newExecution')}
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {t('maintenance.executionHistory')}
          </button>

        </nav>
      </div>

      {activeTab === 'new' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">{t('maintenance.startNewMaintenance')}</h2>
          
          <div className="space-y-6">
            {/* Machine Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('maintenance.selectMachine')} *
              </label>
              <select
                value={selectedMachine?.id || ''}
                onChange={(e) => {
                  const machine = machines.find(m => m.id === e.target.value);
                  setSelectedMachine(machine);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">{t('maintenance.selectMachinePlaceholder')}</option>
                {machines.map(machine => (
                  <option key={machine.id} value={machine.id}>
                    {machine.name || machine.model} ({machine.serial_number})
                    {machine.location && ` - ${machine.location}`}
                  </option>
                ))}
              </select>
            </div>

            {/* Protocol Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('maintenance.selectProtocol')} *
              </label>
              <select
                value={selectedProtocol?.id || ''}
                onChange={(e) => {
                  const protocol = protocols.find(p => p.id === e.target.value);
                  setSelectedProtocol(protocol);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!selectedMachine}
              >
                <option value="">{t('maintenance.selectProtocolPlaceholder')}</option>
                {protocols.map(protocol => (
                  <option key={protocol.id} value={protocol.id}>
                    {protocol.name} ({protocol.protocol_type})
                    {protocol.estimated_duration_minutes && ` - ${protocol.estimated_duration_minutes} ${t('maintenance.min')}`}
                  </option>
                ))}
              </select>
            </div>

            {/* Protocol Details */}
            {selectedProtocol && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <h3 className="font-medium text-blue-900 mb-2">{selectedProtocol.name}</h3>
                {selectedProtocol.description && (
                  <p className="text-sm text-blue-800 mb-2">{selectedProtocol.description}</p>
                )}
                <div className="flex flex-wrap gap-4 text-sm text-blue-700">
                  <span>{t('maintenance.type')}: {selectedProtocol.protocol_type}</span>
                  {selectedProtocol.estimated_duration_minutes && (
                    <span>{t('maintenance.duration')}: {selectedProtocol.estimated_duration_minutes} {t('maintenance.min')}</span>
                  )}
                  {selectedProtocol.frequency_hours && (
                    <span>{t('maintenance.frequency')}: {t('maintenance.every')} {selectedProtocol.frequency_hours} {t('maintenance.hours')}</span>
                  )}
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <button
                onClick={handleStartExecution}
                disabled={!selectedMachine || !selectedProtocol}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {t('maintenance.startMaintenance')}
              </button>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <ExecutionHistory 
          executions={executions} 
          onRefresh={loadData}
          onResumeExecution={handleResumeExecution}
        />
      )}


    </div>
  );
};

export default MaintenanceExecutions;

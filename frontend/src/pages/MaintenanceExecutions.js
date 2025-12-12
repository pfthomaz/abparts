import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { machinesService } from '../services/machinesService';
import { getLocalizedProtocols, createExecution, getExecutions } from '../services/maintenanceProtocolsService';
import ExecutionForm from '../components/ExecutionForm';
import ExecutionHistory from '../components/ExecutionHistory';


const MaintenanceExecutions = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [machines, setMachines] = useState([]);
  const [protocols, setProtocols] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [selectedProtocol, setSelectedProtocol] = useState(null);
  const [showExecutionForm, setShowExecutionForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('new'); // 'new' or 'history'

  useEffect(() => {
    loadData();
  }, []);

  // Handle preselected machine/protocol from navigation state
  useEffect(() => {
    if (location.state?.preselectedMachine && location.state?.preselectedProtocol) {
      setSelectedMachine(location.state.preselectedMachine);
      setSelectedProtocol(location.state.preselectedProtocol);
      // Auto-start execution
      setShowExecutionForm(true);
    }
  }, [location.state]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [machinesData, protocolsData, executionsData] = await Promise.all([
        machinesService.getMachines(),
        getLocalizedProtocols({}, user.preferred_language),
        getExecutions()
      ]);
      console.log('Loaded executions:', executionsData);
      setMachines(machinesData);
      setProtocols(protocolsData.filter(p => p.is_active));
      setExecutions(executionsData);
      setError(null);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
        onComplete={handleExecutionComplete}
        onCancel={() => {
          setShowExecutionForm(false);
          setSelectedMachine(null);
          setSelectedProtocol(null);
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
        <ExecutionHistory executions={executions} onRefresh={loadData} />
      )}


    </div>
  );
};

export default MaintenanceExecutions;

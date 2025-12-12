import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { machinesService } from '../services/machinesService';
import { getLocalizedProtocols, getExecutions } from '../services/maintenanceProtocolsService';
import { useTranslation } from '../hooks/useTranslation';

const DailyOperations = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const [machines, setMachines] = useState([]);
  const [selectedMachine, setSelectedMachine] = useState(null);
  const [startProtocol, setStartProtocol] = useState(null);
  const [endProtocol, setEndProtocol] = useState(null);
  const [todayExecutions, setTodayExecutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sessionStatus, setSessionStatus] = useState(null); // 'not_started', 'in_progress', 'completed'

  useEffect(() => {
    loadData();
  }, []);

  // Handle returning from maintenance execution with preselected machine
  useEffect(() => {
    if (location.state?.selectedMachineId && machines.length > 0) {
      const machine = machines.find(m => m.id === location.state.selectedMachineId);
      if (machine) {
        setSelectedMachine(machine);
      }
      // Clear the state so it doesn't persist on refresh
      window.history.replaceState({}, document.title);
    }
  }, [location.state, machines]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [machinesData, protocolsData, executionsData] = await Promise.all([
        machinesService.getMachines(),
        getLocalizedProtocols({}, user?.preferred_language),
        getExecutions()
      ]);

      setMachines(machinesData);

      // Find start and end of day protocols
      // Use specific protocol IDs for reliable detection (language-independent)
      const START_PROTOCOL_ID = 'f459363d-1dbf-443f-b988-ab43bab0f520';
      const END_PROTOCOL_ID = '674da9b0-6d6b-4f40-a5c2-20ecc4d25aac';
      
      const start = protocolsData.find(p => p.id === START_PROTOCOL_ID);
      const end = protocolsData.find(p => p.id === END_PROTOCOL_ID);
      
      // Fallback to name-based detection for other protocols
      if (!start) {
        const startFallback = protocolsData.find(p => 
          p.protocol_type === 'daily' && 
          (p.name.toLowerCase().includes('start') || 
           p.name.toLowerCase().includes('pre-operation') ||
           p.name.toLowerCase().includes('έναρξη') || // Greek: start
           p.name.toLowerCase().includes('αρχή'))     // Greek: beginning
        );
        if (startFallback) setStartProtocol(startFallback);
      }
      
      if (!end) {
        const endFallback = protocolsData.find(p => 
          p.protocol_type === 'daily' && 
          (p.name.toLowerCase().includes('end') || 
           p.name.toLowerCase().includes('post-operation') ||
           p.name.toLowerCase().includes('τέλος') ||    // Greek: end
           p.name.toLowerCase().includes('τέλους'))     // Greek: end (genitive)
        );
        if (endFallback) setEndProtocol(endFallback);
      }

      if (start) setStartProtocol(start);
      if (end) setEndProtocol(end);

      // Filter today's executions
      const today = new Date().toISOString().split('T')[0];
      const todayExecs = executionsData.filter(exec => {
        const execDate = new Date(exec.performed_date || exec.created_at).toISOString().split('T')[0];
        return execDate === today;
      });
      setTodayExecutions(todayExecs);

    } catch (err) {
      console.error('Error loading data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!selectedMachine || !todayExecutions.length) {
      setSessionStatus('not_started');
      return;
    }

    const machineExecs = todayExecutions.filter(e => e.machine_id === selectedMachine.id);
    const hasStart = machineExecs.some(e => 
      e.protocol?.name.toLowerCase().includes('start') || 
      e.protocol?.name.toLowerCase().includes('pre-operation')
    );
    const hasEnd = machineExecs.some(e => 
      e.protocol?.name.toLowerCase().includes('end') || 
      e.protocol?.name.toLowerCase().includes('post-operation')
    );

    if (hasEnd) {
      setSessionStatus('completed');
    } else if (hasStart) {
      setSessionStatus('in_progress');
    } else {
      setSessionStatus('not_started');
    }
  }, [selectedMachine, todayExecutions]);

  const handleStartDay = () => {
    if (!selectedMachine || !startProtocol) return;
    navigate('/maintenance-executions', {
      state: {
        preselectedMachine: selectedMachine,
        preselectedProtocol: startProtocol,
        sessionType: 'start_of_day'
      }
    });
  };

  const handleEndDay = () => {
    if (!selectedMachine || !endProtocol) return;
    navigate('/maintenance-executions', {
      state: {
        preselectedMachine: selectedMachine,
        preselectedProtocol: endProtocol,
        sessionType: 'end_of_day'
      }
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg shadow-lg p-8 text-white mb-6">
        <h1 className="text-3xl font-bold mb-2">🌊 {t('dailyOperations.title')}</h1>
        <p className="text-cyan-100">{t('dailyOperations.subtitle')}</p>
      </div>
      
      <div className="space-y-6">

      {/* Machine Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('dailyOperations.selectMachine')}
        </label>
        <select
          value={selectedMachine?.id || ''}
          onChange={(e) => {
            const machine = machines.find(m => m.id === e.target.value);
            setSelectedMachine(machine);
          }}
          className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          <option value="">{t('dailyOperations.selectMachinePlaceholder')}</option>
          {machines.map(machine => (
            <option key={machine.id} value={machine.id}>
              {machine.name || machine.model} ({machine.serial_number})
            </option>
          ))}
        </select>
      </div>

      {selectedMachine && (
        <>
          {/* Session Status */}
          <div className={`rounded-lg shadow p-6 ${
            sessionStatus === 'completed' ? 'bg-green-50 border-2 border-green-200' :
            sessionStatus === 'in_progress' ? 'bg-yellow-50 border-2 border-yellow-200' :
            'bg-gray-50 border-2 border-gray-200'
          }`}>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-2xl">
                {sessionStatus === 'completed' ? '✅' :
                 sessionStatus === 'in_progress' ? '⚙️' : '🔵'}
              </span>
              <h2 className="text-xl font-bold text-gray-900">
                {sessionStatus === 'completed' ? t('dailyOperations.dayCompleted') :
                 sessionStatus === 'in_progress' ? t('dailyOperations.operationsInProgress') :
                 t('dailyOperations.readyToStart')}
              </h2>
            </div>
            <p className="text-gray-600">
              {sessionStatus === 'completed' ? t('dailyOperations.allDailyChecksCompleted') :
               sessionStatus === 'in_progress' ? t('dailyOperations.startCompletedRememberEnd') :
               t('dailyOperations.beginDayWithStartChecks')}
            </p>
          </div>

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Start of Day */}
            <div className={`bg-white rounded-lg shadow-lg p-6 ${
              sessionStatus === 'not_started' ? 'ring-2 ring-cyan-500' : ''
            }`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">🌅</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{t('dailyOperations.startOfDay')}</h3>
                  <p className="text-sm text-gray-500">{t('dailyOperations.preOperationChecks')}</p>
                </div>
              </div>
              
              {sessionStatus === 'not_started' ? (
                <button
                  onClick={handleStartDay}
                  disabled={!startProtocol}
                  className="w-full px-4 py-3 bg-cyan-600 text-white rounded-md hover:bg-cyan-700 font-medium disabled:bg-gray-400"
                >
                  {startProtocol ? t('dailyOperations.beginStartOfDayChecks') : t('dailyOperations.noProtocolConfigured')}
                </button>
              ) : (
                <div className="flex items-center gap-2 text-green-600">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{t('dailyOperations.completed')}</span>
                </div>
              )}
            </div>

            {/* End of Day */}
            <div className={`bg-white rounded-lg shadow-lg p-6 ${
              sessionStatus === 'in_progress' ? 'ring-2 ring-orange-500' : ''
            }`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">🌇</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{t('dailyOperations.endOfDay')}</h3>
                  <p className="text-sm text-gray-500">{t('dailyOperations.postOperationChecks')}</p>
                </div>
              </div>
              
              {sessionStatus === 'completed' ? (
                <div className="flex items-center gap-2 text-green-600">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{t('dailyOperations.completed')}</span>
                </div>
              ) : sessionStatus === 'in_progress' ? (
                <button
                  onClick={handleEndDay}
                  disabled={!endProtocol}
                  className="w-full px-4 py-3 bg-orange-600 text-white rounded-md hover:bg-orange-700 font-medium disabled:bg-gray-400"
                >
                  {endProtocol ? t('dailyOperations.completeEndOfDayChecks') : t('dailyOperations.noProtocolConfigured')}
                </button>
              ) : (
                <div className="text-gray-500 text-sm">
                  {t('dailyOperations.completeStartOfDayFirst')}
                </div>
              )}
            </div>
          </div>
        </>
      )}
      </div>
    </>
  );
};

export default DailyOperations;

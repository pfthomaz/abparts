import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { 
  getLocalizedChecklistItems, 
  createExecution, 
  completeChecklistItem,
  completeExecution
} from '../services/maintenanceProtocolsService';

const ExecutionForm = ({ machine, protocol, onComplete, onCancel }) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [checklistItems, setChecklistItems] = useState([]);
  const [executionId, setExecutionId] = useState(null);
  const [completedItems, setCompletedItems] = useState({});
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);  // Start as false, will be set to true when starting execution
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Don't auto-initialize - wait for user to enter hours

  const [machineHours, setMachineHours] = useState(machine.current_hours || 0);
  const [showHoursInput, setShowHoursInput] = useState(true);

  const initializeExecution = async (hours) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Starting execution with hours:', hours);
      
      // Load localized checklist items
      const items = await getLocalizedChecklistItems(protocol.id, user.preferred_language);
      console.log('Loaded localized checklist items:', items);
      setChecklistItems(items);

      // Create execution record
      const executionData = {
        protocol_id: protocol.id,
        machine_id: machine.id,
        status: 'in_progress'
      };
      
      // Only include machine hours if > 0
      if (hours > 0) {
        executionData.machine_hours_at_service = hours;
      }
      
      console.log('Creating execution with data:', executionData);
      
      const execution = await createExecution(executionData);
      console.log('Execution created:', execution);
      
      setExecutionId(execution.id);
      setShowHoursInput(false);
    } catch (err) {
      console.error('Error initializing execution:', err);
      setError(err.message);
      alert(`Failed to start maintenance: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStartExecution = () => {
    if (machineHours === null || machineHours === undefined || machineHours < 0) {
      alert('Please enter valid machine hours');
      return;
    }
    initializeExecution(machineHours);
  };

  const handleItemComplete = async (item, itemData) => {
    if (!executionId) return;

    try {
      await completeChecklistItem(executionId, item.id, {
        status: itemData.completed ? 'completed' : 'skipped',
        notes: itemData.notes || null,
        actual_quantity_used: itemData.quantity ? parseFloat(itemData.quantity) : null
      });

      setCompletedItems(prev => ({
        ...prev,
        [item.id]: { ...itemData, saved: true }
      }));
    } catch (err) {
      alert(t('maintenance.failedToSaveItem', { error: err.message }));
      // Revert the change on error
      setCompletedItems(prev => ({
        ...prev,
        [item.id]: { ...prev[item.id], completed: !itemData.completed }
      }));
    }
  };

  const handleItemChange = async (item, field, value) => {
    const itemData = {
      ...completedItems[item.id],
      [field]: value
    };
    
    setCompletedItems(prev => ({
      ...prev,
      [item.id]: itemData
    }));

    // Auto-save when checkbox is toggled
    if (field === 'completed') {
      await handleItemComplete(item, itemData);
    }
  };

  const handleFinish = async () => {
    // Check if all critical items are completed
    const criticalItems = checklistItems.filter(item => item.is_critical);
    const incompleteCritical = criticalItems.filter(
      item => !completedItems[item.id]?.completed
    );

    if (incompleteCritical.length > 0) {
      alert(t('maintenance.completeAllCriticalItems', { count: incompleteCritical.length }));
      return;
    }

    // Check if any items are not saved
    const unsavedItems = Object.entries(completedItems).filter(
      ([_, data]) => !data.saved
    );

    if (unsavedItems.length > 0) {
      alert(t('maintenance.saveAllItemsBeforeFinishing'));
      return;
    }

    if (!window.confirm(t('maintenance.confirmFinishExecution'))) {
      return;
    }

    try {
      setSaving(true);
      await completeExecution(executionId);
      alert(t('maintenance.executionCompletedSuccessfully'));
      onComplete();
    } catch (err) {
      alert(t('maintenance.failedToCompleteExecution', { error: err.message }));
    } finally {
      setSaving(false);
    }
  };

  if (showHoursInput) {
    return (
      <div className="bg-white rounded-lg shadow p-6 max-w-md mx-auto mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">{t('maintenance.enterCurrentMachineHours')}</h2>
        <p className="text-gray-600 mb-4">
          {t('maintenance.pleaseEnterHourMeterReading')} {machine.name || machine.serial_number}
        </p>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('maintenance.machineHours')} *
          </label>
          <input
            type="number"
            step="0.01"
            value={machineHours}
            onChange={(e) => setMachineHours(parseFloat(e.target.value) || 0)}
            className="w-full px-4 py-3 text-lg border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder={t('maintenance.hoursPlaceholder')}
            autoFocus
          />
        </div>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleStartExecution}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? t('maintenance.starting') : t('maintenance.startMaintenance')}
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p className="font-medium">{t('maintenance.errorInitializingExecution')}</p>
        <p className="text-sm mt-1">{error}</p>
        <button
          onClick={onCancel}
          className="mt-4 px-4 py-2 bg-white border border-red-300 rounded-md hover:bg-red-50"
        >
          {t('common.goBack')}
        </button>
      </div>
    );
  }

  const progress = checklistItems.length > 0
    ? (Object.values(completedItems).filter(item => item.saved).length / checklistItems.length) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{protocol.name}</h1>
            <p className="text-gray-600 mt-1">
              {t('maintenance.machine')}: {machine.serial_number} - {machine.model}
            </p>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-600 hover:text-gray-800"
          >
            ✕
          </button>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>{t('maintenance.progress')}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Checklist Items */}
      <div className="space-y-4">
        {checklistItems.map((item, index) => {
          const itemData = completedItems[item.id] || {};
          const isSaved = itemData.saved;
          
          return (
            <div
              key={item.id}
              className={`bg-white rounded-lg shadow p-6 ${
                isSaved ? 'border-l-4 border-green-500' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded flex items-center justify-center text-gray-600 font-medium">
                  {index + 1}
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-gray-900 flex items-center gap-2">
                        {item.item_description}
                        {item.is_critical && (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            {t('maintenance.critical')}
                          </span>
                        )}
                      </h3>
                      <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          {item.item_type}
                        </span>
                        {item.estimated_duration_minutes && (
                          <span>⏱️ {item.estimated_duration_minutes} min</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {item.notes && (
                    <p className="text-sm text-gray-600 mb-3 bg-gray-50 p-2 rounded">
                      ℹ️ {item.notes}
                    </p>
                  )}

                  <div className="space-y-3">
                    {/* Completion Checkbox - Larger and more prominent */}
                    <div className="flex items-center p-3 bg-gray-50 rounded-lg border-2 border-gray-200 hover:border-blue-300 transition-colors">
                      <input
                        type="checkbox"
                        id={`complete-${item.id}`}
                        checked={itemData.completed || false}
                        onChange={(e) => handleItemChange(item, 'completed', e.target.checked)}
                        className="h-6 w-6 text-green-600 focus:ring-green-500 border-gray-300 rounded cursor-pointer"
                        disabled={isSaved}
                      />
                      <label htmlFor={`complete-${item.id}`} className="ml-3 text-base font-medium text-gray-900 cursor-pointer flex-1">
                        {isSaved ? t('maintenance.completed') : t('maintenance.markAsCompleted')}
                      </label>
                      {isSaved && (
                        <span className="text-green-600 text-sm font-medium">{t('maintenance.saved')}</span>
                      )}
                    </div>

                    {/* Quantity Input */}
                    {item.estimated_quantity && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          {t('maintenance.quantityUsed')} {item.part && `(${item.part.name})`}
                        </label>
                        <input
                          type="number"
                          step="0.001"
                          value={itemData.quantity || ''}
                          onChange={(e) => handleItemChange(item, 'quantity', e.target.value)}
                          onBlur={() => isSaved && handleItemComplete(item, itemData)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder={t('maintenance.estimatedQuantity', { quantity: item.estimated_quantity })}
                          disabled={!itemData.completed}
                        />
                      </div>
                    )}

                    {/* Notes */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('maintenance.notes')}
                      </label>
                      <textarea
                        value={itemData.notes || ''}
                        onChange={(e) => handleItemChange(item, 'notes', e.target.value)}
                        onBlur={() => isSaved && handleItemComplete(item, itemData)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder={t('maintenance.addObservationsPlaceholder')}
                        disabled={!itemData.completed}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center">
          <button
            onClick={onCancel}
            className="px-6 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {t('common.cancel')}
          </button>
          <button
            onClick={handleFinish}
            disabled={progress < 100}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {t('maintenance.finishMaintenance')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExecutionForm;

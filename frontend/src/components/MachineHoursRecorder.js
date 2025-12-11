// frontend/src/components/MachineHoursRecorder.js

import React, { useState, useEffect } from 'react';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';

// Offline storage utilities
const OFFLINE_STORAGE_KEY = 'abparts_offline_machine_hours';

const saveOfflineRecord = (record) => {
  try {
    const existingRecords = JSON.parse(localStorage.getItem(OFFLINE_STORAGE_KEY) || '[]');
    const newRecord = {
      ...record,
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      synced: false
    };
    existingRecords.push(newRecord);
    localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(existingRecords));
    return newRecord;
  } catch (error) {
    console.error('Failed to save offline record:', error);
    return null;
  }
};

const getOfflineRecords = () => {
  try {
    return JSON.parse(localStorage.getItem(OFFLINE_STORAGE_KEY) || '[]');
  } catch (error) {
    console.error('Failed to get offline records:', error);
    return [];
  }
};

const markRecordSynced = (recordId) => {
  try {
    const records = getOfflineRecords();
    const updatedRecords = records.map(record =>
      record.id === recordId ? { ...record, synced: true } : record
    );
    localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(updatedRecords));
  } catch (error) {
    console.error('Failed to mark record as synced:', error);
  }
};

const removeOfflineRecord = (recordId) => {
  try {
    const records = getOfflineRecords();
    const filteredRecords = records.filter(record => record.id !== recordId);
    localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(filteredRecords));
  } catch (error) {
    console.error('Failed to remove offline record:', error);
  }
};

const MachineHoursRecorder = ({ machine, onSubmit, onClose, onHoursRecorded }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    hours_value: '',
    recorded_date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [offlineRecords, setOfflineRecords] = useState([]);
  const [showOfflineRecords, setShowOfflineRecords] = useState(false);

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Load offline records
  useEffect(() => {
    const records = getOfflineRecords().filter(record =>
      record.machine_id === machine.id && !record.synced
    );
    setOfflineRecords(records);
  }, [machine.id]);

  // Auto-sync offline records when coming back online
  useEffect(() => {
    if (isOnline && offlineRecords.length > 0) {
      syncOfflineRecords();
    }
  }, [isOnline, offlineRecords]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const syncOfflineRecords = async () => {
    const unsyncedRecords = getOfflineRecords().filter(record => !record.synced);

    for (const record of unsyncedRecords) {
      try {
        await machinesService.recordMachineHours(record.machine_id, {
          hours_value: record.hours_value,
          recorded_date: record.recorded_date,
          notes: record.notes
        });
        markRecordSynced(record.id);
      } catch (error) {
        console.error('Failed to sync offline record:', error);
        // Keep the record for next sync attempt
      }
    }

    // Refresh offline records display
    const remainingRecords = getOfflineRecords().filter(record =>
      record.machine_id === machine.id && !record.synced
    );
    setOfflineRecords(remainingRecords);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.hours_value || parseFloat(formData.hours_value) <= 0) {
      setError('Please enter a valid hours value');
      return;
    }

    const hoursData = {
      machine_id: machine.id,
      hours_value: parseFloat(formData.hours_value),
      recorded_date: formData.recorded_date,
      notes: formData.notes.trim() || null
    };

    setLoading(true);

    if (isOnline) {
      // Try to submit online first
      try {
        await machinesService.recordMachineHours(machine.id, hoursData);

        if (onHoursRecorded) {
          onHoursRecorded();
        }
        if (onSubmit) {
          onSubmit();
        }
        if (onClose) {
          onClose();
        }
      } catch (err) {
        // If online submission fails, save offline
        setError('Network error. Saving offline...');
        const offlineRecord = saveOfflineRecord(hoursData);
        if (offlineRecord) {
          setTimeout(() => {
            if (onSubmit) {
              onSubmit();
            }
            if (onClose) {
              onClose();
            }
          }, 1500);
        } else {
          setError('Failed to save offline. Please try again.');
        }
      }
    } else {
      // Save offline when not connected
      const offlineRecord = saveOfflineRecord(hoursData);
      if (offlineRecord) {
        setError('Saved offline. Will sync when connection is restored.');
        setTimeout(() => {
          if (onSubmit) {
            onSubmit();
          }
          if (onClose) {
            onClose();
          }
        }, 1500);
      } else {
        setError('Failed to save offline. Please try again.');
      }
    }

    setLoading(false);
  };

  const deleteOfflineRecord = (recordId) => {
    removeOfflineRecord(recordId);
    setOfflineRecords(prev => prev.filter(record => record.id !== recordId));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 sm:p-6 rounded-t-lg">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-semibold">Record Machine Hours</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-2 hover:bg-gray-100 rounded-full"
              disabled={loading}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Connection Status */}
          <div className={`flex items-center space-x-2 text-sm ${isOnline ? 'text-green-600' : 'text-orange-600'}`}>
            <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500' : 'bg-orange-500'}`}></div>
            <span>{isOnline ? 'Online' : 'Offline'}</span>
            {!isOnline && <span className="text-gray-500">- Data will be saved locally</span>}
          </div>
        </div>

        <div className="p-4 sm:p-6">
          {/* Machine Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Machine:</strong> {machine.name || machine.serial_number}
            </p>
            <p className="text-sm text-gray-600">
              <strong>Model:</strong> {machine.model}
            </p>
          </div>

          {/* Offline Records Alert */}
          {offlineRecords.length > 0 && (
            <div className="mb-4 p-3 bg-orange-50 border border-orange-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span className="text-sm text-orange-700">
                    {offlineRecords.length} unsaved record{offlineRecords.length > 1 ? 's' : ''}
                  </span>
                </div>
                <button
                  onClick={() => setShowOfflineRecords(!showOfflineRecords)}
                  className="text-orange-600 hover:text-orange-800 text-sm font-medium"
                >
                  {showOfflineRecords ? 'Hide' : 'Show'}
                </button>
              </div>

              {showOfflineRecords && (
                <div className="mt-3 space-y-2">
                  {offlineRecords.map((record) => (
                    <div key={record.id} className="flex items-center justify-between bg-white p-2 rounded border">
                      <div className="text-xs text-gray-600">
                        <div>{record.hours_value}h on {record.recorded_date}</div>
                        {record.notes && <div className="text-gray-500">{record.notes}</div>}
                      </div>
                      <button
                        onClick={() => deleteOfflineRecord(record.id)}
                        className="text-red-500 hover:text-red-700 p-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className={`mb-4 p-3 rounded-lg ${error.includes('Saved offline') || error.includes('Saving offline')
                ? 'bg-orange-100 border border-orange-400 text-orange-700'
                : 'bg-red-100 border border-red-400 text-red-700'
              }`}>
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="hours_value" className="block text-sm font-medium text-gray-700 mb-2">
                Hours Value *
              </label>
              <input
                type="number"
                id="hours_value"
                name="hours_value"
                value={formData.hours_value}
                onChange={handleInputChange}
                step="0.1"
                min="0.1"
                max="99999.9"
                className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter hours (e.g., 123.5)"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="recorded_date" className="block text-sm font-medium text-gray-700 mb-2">
                Date *
              </label>
              <input
                type="date"
                id="recorded_date"
                name="recorded_date"
                value={formData.recorded_date}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Optional notes about this reading..."
                disabled={loading}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-6 py-3 text-gray-700 bg-gray-200 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50 transition-colors"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
                disabled={loading}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Recording...</span>
                  </div>
                ) : (
                  `Record Hours ${!isOnline ? '(Offline)' : ''}`
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default MachineHoursRecorder;
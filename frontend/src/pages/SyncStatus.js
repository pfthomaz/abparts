// frontend/src/pages/SyncStatus.js

import { useState, useEffect } from 'react';
import { useTranslation } from '../hooks/useTranslation';
import { useOffline } from '../contexts/OfflineContext';
import { 
  getPendingOperations, 
  getQueueStatus, 
  getFailedOperations,
  retryOperation,
  removeOperation 
} from '../services/syncQueueManager';
import { 
  getUnsyncedNetCleaningRecords,
  getStorageUsage 
} from '../db/indexedDB';

const SyncStatus = () => {
  const { t } = useTranslation();
  const { 
    isOnline, 
    pendingCount, 
    isSyncing, 
    lastSyncTime, 
    syncError,
    triggerSync,
    storageInfo 
  } = useOffline();

  const [queueOperations, setQueueOperations] = useState([]);
  const [offlineRecords, setOfflineRecords] = useState([]);
  const [queueStats, setQueueStats] = useState(null);
  const [failedOps, setFailedOps] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [operations, records, stats, failed] = await Promise.all([
        getPendingOperations(),
        getUnsyncedNetCleaningRecords(),
        getQueueStatus(),
        getFailedOperations()
      ]);
      
      setQueueOperations(operations);
      setOfflineRecords(records);
      setQueueStats(stats);
      setFailedOps(failed);
    } catch (error) {
      console.error('[SyncStatus] Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [pendingCount, isSyncing]);

  const handleSync = async () => {
    await triggerSync();
    await loadData();
  };

  const handleRetry = async (operationId) => {
    try {
      await retryOperation(operationId);
      await loadData();
    } catch (error) {
      console.error('[SyncStatus] Error retrying operation:', error);
    }
  };

  const handleRemove = async (operationId) => {
    if (!window.confirm(t('syncStatus.confirmRemove'))) {
      return;
    }
    try {
      await removeOperation(operationId);
      await loadData();
    } catch (error) {
      console.error('[SyncStatus] Error removing operation:', error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getOperationTypeLabel = (type) => {
    const labels = {
      'NET_CLEANING_RECORD': t('syncStatus.types.netCleaningRecord'),
      'NET_CLEANING_PHOTO': t('syncStatus.types.netCleaningPhoto'),
      'MAINTENANCE_EXECUTION': t('syncStatus.types.maintenanceExecution'),
      'MACHINE_HOURS': t('syncStatus.types.machineHours'),
      'STOCK_ADJUSTMENT': t('syncStatus.types.stockAdjustment')
    };
    return labels[type] || type;
  };

  const getStatusBadge = (status) => {
    const badges = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'syncing': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-600">{t('common.loading')}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{t('syncStatus.title')}</h1>
        <button
          onClick={handleSync}
          disabled={!isOnline || isSyncing || pendingCount === 0}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {isSyncing && (
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          )}
          <span>{isSyncing ? t('syncStatus.syncing') : t('syncStatus.syncNow')}</span>
        </button>
      </div>

      {/* Connection Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.connectionStatus')}</p>
              <p className="text-2xl font-bold mt-1">
                {isOnline ? (
                  <span className="text-green-600">{t('syncStatus.online')}</span>
                ) : (
                  <span className="text-red-600">{t('syncStatus.offline')}</span>
                )}
              </p>
            </div>
            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isOnline ? 'bg-green-100' : 'bg-red-100'}`}>
              {isOnline ? (
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              )}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.pendingOperations')}</p>
              <p className="text-2xl font-bold mt-1">{pendingCount}</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.lastSync')}</p>
              <p className="text-sm font-medium mt-1">
                {lastSyncTime ? formatDate(lastSyncTime) : t('syncStatus.never')}
              </p>
            </div>
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
              <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Storage Info */}
      {storageInfo && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{t('syncStatus.storageUsage')}</h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{t('syncStatus.used')}</span>
              <span className="font-medium">{formatBytes(storageInfo.usage)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">{t('syncStatus.quota')}</span>
              <span className="font-medium">{formatBytes(storageInfo.quota)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full" 
                style={{ width: `${storageInfo.percentage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 text-right">{storageInfo.percentage}% {t('syncStatus.used')}</p>
          </div>
        </div>
      )}

      {/* Sync Error */}
      {syncError && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <div className="flex items-start">
            <svg className="w-5 h-5 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="font-medium">{t('syncStatus.syncError')}</p>
              <p className="text-sm mt-1">{syncError}</p>
            </div>
          </div>
        </div>
      )}

      {/* Queue Statistics */}
      {queueStats && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{t('syncStatus.queueStatistics')}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.total')}</p>
              <p className="text-2xl font-bold">{queueStats.total}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.pending')}</p>
              <p className="text-2xl font-bold text-yellow-600">{queueStats.pending}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.syncing')}</p>
              <p className="text-2xl font-bold text-blue-600">{queueStats.syncing}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('syncStatus.failed')}</p>
              <p className="text-2xl font-bold text-red-600">{queueStats.failed}</p>
            </div>
          </div>
        </div>
      )}

      {/* Failed Operations */}
      {failedOps.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-red-600">{t('syncStatus.failedOperations')}</h2>
          <div className="space-y-3">
            {failedOps.map(op => (
              <div key={op.id} className="border border-red-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-medium">{getOperationTypeLabel(op.type)}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusBadge(op.status)}`}>
                        {t(`syncStatus.statuses.${op.status}`)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{t('syncStatus.attempts')}: {op.retryCount} / 3</p>
                    {op.error && (
                      <p className="text-sm text-red-600 mt-1">{op.error}</p>
                    )}
                    <p className="text-xs text-gray-500 mt-1">{formatDate(op.createdAt)}</p>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleRetry(op.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      {t('syncStatus.retry')}
                    </button>
                    <button
                      onClick={() => handleRemove(op.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      {t('syncStatus.remove')}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Pending Operations */}
      {queueOperations.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">{t('syncStatus.pendingOperations')}</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t('syncStatus.type')}</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t('syncStatus.status')}</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t('syncStatus.priority')}</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t('syncStatus.created')}</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {queueOperations.map(op => (
                  <tr key={op.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{getOperationTypeLabel(op.type)}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusBadge(op.status)}`}>
                        {t(`syncStatus.statuses.${op.status}`)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{op.priority}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDate(op.createdAt)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Offline Records */}
      {offlineRecords.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">{t('syncStatus.offlineRecords')}</h2>
          <p className="text-sm text-gray-600 mb-4">
            {t('syncStatus.offlineRecordsHelp')}
          </p>
          <div className="space-y-3">
            {offlineRecords.map(record => (
              <div key={record.id} className="border border-blue-200 rounded-lg p-4 bg-blue-50">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{t('syncStatus.netCleaningRecord')}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {t('syncStatus.operator')}: {record.operator_name}
                    </p>
                    <p className="text-sm text-gray-600">
                      {t('syncStatus.mode')}: {record.cleaning_mode}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{formatDate(record.start_time)}</p>
                  </div>
                  <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    {t('syncStatus.waitingSync')}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {pendingCount === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="w-16 h-16 text-green-500 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t('syncStatus.allSynced')}</h3>
          <p className="text-gray-600">{t('syncStatus.allSyncedHelp')}</p>
        </div>
      )}
    </div>
  );
};

export default SyncStatus;

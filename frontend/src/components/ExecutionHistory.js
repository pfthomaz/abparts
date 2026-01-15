import React, { useState } from 'react';
import { formatDate } from '../utils';
import { useTranslation } from '../hooks/useTranslation';
import { useAuth } from '../AuthContext';
import { deleteExecution } from '../services/maintenanceProtocolsService';

const ExecutionHistory = ({ executions, onRefresh, onResumeExecution }) => {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [selectedExecution, setSelectedExecution] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [isDeleting, setIsDeleting] = useState(false);

  console.log('ExecutionHistory received executions:', executions);

  const canDeleteExecution = (execution) => {
    console.log('canDeleteExecution check:', {
      user,
      userRole: user?.role,
      executionMachineOrgId: execution.machine?.customer_organization_id,
      userOrgId: user?.organization_id,
      canDelete: user && (user.role === 'super_admin' || (user.role === 'admin' && execution.machine?.customer_organization_id === user.organization_id))
    });
    
    if (!user) return false;
    // Super admin can delete any execution
    if (user.role === 'super_admin') return true;
    // Admin can delete executions in their organization
    if (user.role === 'admin' && execution.machine?.customer_organization_id === user.organization_id) return true;
    return false;
  };

  const handleDeleteExecution = async (execution) => {
    if (!window.confirm(t('maintenance.confirmDeleteExecution'))) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteExecution(execution.id);
      alert(t('maintenance.executionDeletedSuccessfully'));
      setSelectedExecution(null);
      if (onRefresh) {
        onRefresh();
      }
    } catch (error) {
      console.error('Failed to delete execution:', error);
      alert(t('maintenance.failedToDeleteExecution'));
    } finally {
      setIsDeleting(false);
    }
  };

  const filteredExecutions = executions.filter(exec => {
    if (filterStatus === 'all') return true;
    return exec.status === filterStatus;
  });

  console.log('Filtered executions:', filteredExecutions);

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    const icons = {
      scheduled: '📅',
      in_progress: '⚙️',
      completed: '✅',
      cancelled: '❌'
    };
    return icons[status] || '•';
  };

  if (selectedExecution) {
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <button
              onClick={() => setSelectedExecution(null)}
              className="text-blue-600 hover:text-blue-800 mb-4"
            >
              ← {t('maintenance.backToHistory')}
            </button>
            <div className="flex gap-2">
              {selectedExecution.status === 'in_progress' && onResumeExecution && (
                <button
                  onClick={() => {
                    setSelectedExecution(null);
                    onResumeExecution(selectedExecution);
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  {t('maintenance.resumeExecution')}
                </button>
              )}
              {canDeleteExecution(selectedExecution) && (
                <button
                  onClick={() => handleDeleteExecution(selectedExecution)}
                  disabled={isDeleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isDeleting ? t('common.loading') : t('common.delete')}
                </button>
              )}
            </div>
          </div>
          <h2 className="text-2xl font-bold text-gray-900">{t('maintenance.executionDetails')}</h2>
        </div>

        <div className="p-6 space-y-6">
          {/* Execution Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-500">{t('maintenance.protocol')}</label>
              <p className="text-gray-900">{selectedExecution.protocol?.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">{t('maintenance.machine')}</label>
              <p className="text-gray-900">
                {selectedExecution.machine?.name || selectedExecution.machine?.model} ({selectedExecution.machine?.serial_number})
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">{t('maintenance.performedBy')}</label>
              <p className="text-gray-900">{selectedExecution.performed_by?.name || selectedExecution.performed_by?.username || t('common.unknown')}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">{t('common.date')}</label>
              <p className="text-gray-900">{formatDate(selectedExecution.performed_date || selectedExecution.created_at)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-500">{t('common.status')}</label>
              <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getStatusBadge(selectedExecution.status)}`}>
                {t(`maintenance.status.${selectedExecution.status}`)}
              </span>
            </div>
            {selectedExecution.machine_hours_at_service && (
              <div>
                <label className="text-sm font-medium text-gray-500">{t('maintenance.machineHours')}</label>
                <p className="text-gray-900">{selectedExecution.machine_hours_at_service} {t('maintenance.hours')}</p>
              </div>
            )}
          </div>

          {selectedExecution.notes && (
            <div>
              <label className="text-sm font-medium text-gray-500">{t('maintenance.notes')}</label>
              <p className="text-gray-900 mt-1 bg-gray-50 p-3 rounded">{selectedExecution.notes}</p>
            </div>
          )}

          {/* Checklist Completions */}
          {selectedExecution.checklist_completions && selectedExecution.checklist_completions.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('maintenance.checklistItems')}</h3>
              <div className="space-y-3">
                {selectedExecution.checklist_completions.map((completion, index) => (
                  <div key={completion.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-gray-100 rounded flex items-center justify-center text-sm text-gray-600">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-gray-900">
                            {completion.checklist_item?.item_description}
                          </h4>
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                            completion.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {t(`maintenance.status.${completion.status}`)}
                          </span>
                        </div>
                        {completion.actual_quantity_used && (
                          <p className="text-sm text-gray-600">
                            {t('maintenance.quantityUsedValue', { quantity: completion.actual_quantity_used })}
                          </p>
                        )}
                        {completion.notes && (
                          <p className="text-sm text-gray-600 mt-1 bg-gray-50 p-2 rounded">
                            {completion.notes}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">{t('maintenance.executionHistory')}</h2>
          <div className="flex items-center gap-4">
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('maintenance.allStatus')}</option>
              <option value="scheduled">{t('maintenance.status.scheduled')}</option>
              <option value="in_progress">{t('maintenance.status.in_progress')}</option>
              <option value="completed">{t('maintenance.status.completed')}</option>
              <option value="cancelled">{t('maintenance.status.cancelled')}</option>
            </select>
            <button
              onClick={onRefresh}
              className="px-4 py-2 text-blue-600 hover:text-blue-800"
            >
              🔄 {t('common.refresh')}
            </button>
          </div>
        </div>
      </div>

      {filteredExecutions.length === 0 && (
        <div className="p-12 text-center text-gray-500">
          {t('maintenance.noExecutionsFound')}
        </div>
      )}

      <div className="divide-y divide-gray-200">
        {filteredExecutions.map((execution) => (
          <div
            key={execution.id}
            className={`p-6 hover:bg-gray-50 transition-colors ${
              execution.status === 'in_progress' ? 'bg-yellow-50 border-l-4 border-yellow-500' : ''
            }`}
          >
            <div className="flex items-start justify-between">
              <div 
                className="flex-1 cursor-pointer"
                onClick={() => setSelectedExecution(execution)}
              >
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xl">{getStatusIcon(execution.status)}</span>
                  <h3 className="font-medium text-gray-900">{execution.protocol?.name}</h3>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusBadge(execution.status)}`}>
                    {t(`maintenance.status.${execution.status}`)}
                  </span>
                  {execution.status === 'in_progress' && (
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800 animate-pulse">
                      {t('maintenance.incomplete')}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>
                    {t('maintenance.machine')}: {execution.machine?.name || execution.machine?.model} ({execution.machine?.serial_number})
                  </span>
                  <span>
                    {t('maintenance.by')}: {execution.performed_by?.name || execution.performed_by?.username || t('common.unknown')}
                  </span>
                  <span>
                    {t('common.date')}: {formatDate(execution.performed_date || execution.created_at)}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                {execution.status === 'in_progress' && onResumeExecution && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onResumeExecution(execution);
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
                  >
                    {t('maintenance.resume')}
                  </button>
                )}
                <button 
                  onClick={() => setSelectedExecution(execution)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  {t('maintenance.viewDetails')} →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExecutionHistory;

// frontend/src/pages/Transactions.js

import { useState } from 'react';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS, isAdmin } from '../utils/permissions';
import TransactionHistory from '../components/TransactionHistory';
import TransactionForm from '../components/TransactionForm';
import TransactionAnalyticsDashboard from '../components/TransactionAnalyticsDashboard';
import TransactionApprovalWorkflow from '../components/TransactionApprovalWorkflow';
import TransactionReversalInterface from '../components/TransactionReversalInterface';
import TwoPhaseOrderWizard from '../components/TwoPhaseOrderWizard';
import PartUsageRecorder from '../components/PartUsageRecorder';
import InventoryTransactionLog from '../components/InventoryTransactionLog';
import Modal from '../components/Modal';
import { transactionService } from '../services/transactionService';

const Transactions = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('history');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showOrderWizard, setShowOrderWizard] = useState(false);
  const [showPartUsageRecorder, setShowPartUsageRecorder] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleCreateTransaction = async (transactionData) => {
    try {
      await transactionService.createTransaction(transactionData);
      setRefreshTrigger(prev => prev + 1);
      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  };

  const tabs = [
    {
      id: 'history',
      label: t('transactions.tabs.history'),
      icon: '📋',
      description: t('transactions.tabs.historyDesc'),
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS
    },
    {
      id: 'audit-log',
      label: t('transactions.tabs.auditTrail'),
      icon: '🔍',
      description: t('transactions.tabs.auditTrailDesc'),
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS
    },
    {
      id: 'analytics',
      label: t('transactions.tabs.analytics'),
      icon: '📊',
      description: t('transactions.tabs.analyticsDesc'),
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS
    },
    {
      id: 'approvals',
      label: t('transactions.tabs.approvals'),
      icon: '✅',
      description: t('transactions.tabs.approvalsDesc'),
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS,
      adminOnly: true
    },
    {
      id: 'reversals',
      label: t('transactions.tabs.reversals'),
      icon: '↩️',
      description: t('transactions.tabs.reversalsDesc'),
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS,
      adminOnly: true
    }
  ];

  const availableTabs = tabs.filter(tab => {
    if (tab.adminOnly && !isAdmin(user)) return false;
    return true;
  });

  const renderTabContent = () => {
    switch (activeTab) {
      case 'history':
        return <TransactionHistory key={refreshTrigger} />;
      case 'audit-log':
        return <InventoryTransactionLog key={refreshTrigger} />;
      case 'analytics':
        return <TransactionAnalyticsDashboard />;
      case 'approvals':
        return <TransactionApprovalWorkflow />;
      case 'reversals':
        return <TransactionReversalInterface />;
      default:
        return <TransactionHistory key={refreshTrigger} />;
    }
  };

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">{t('transactions.title')}</h1>
            <p className="text-gray-600 mt-1 text-sm sm:text-base">
              {t('transactions.subtitle')}
            </p>
          </div>

          {/* Desktop Action Buttons */}
          <div className="hidden sm:flex space-x-3">
            <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
              <button
                onClick={() => setShowOrderWizard(true)}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                {t('transactions.createOrder')}
              </button>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.RECORD_PART_USAGE} hideIfNoPermission={true}>
              <button
                onClick={() => setShowPartUsageRecorder(true)}
                className="px-4 py-2 text-sm font-medium text-white bg-orange-600 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              >
                {t('transactions.recordUsage')}
              </button>
            </PermissionGuard>

            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {t('transactions.createTransaction')}
            </button>
          </div>

          {/* Mobile Action Buttons */}
          <div className="flex sm:hidden space-x-2 overflow-x-auto pb-2">
            <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
              <button
                onClick={() => setShowOrderWizard(true)}
                className="flex-shrink-0 px-3 py-2 text-xs font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                {t('transactions.createOrder')}
              </button>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.RECORD_PART_USAGE} hideIfNoPermission={true}>
              <button
                onClick={() => setShowPartUsageRecorder(true)}
                className="flex-shrink-0 px-3 py-2 text-xs font-medium text-white bg-orange-600 rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              >
                {t('transactions.recordUsage')}
              </button>
            </PermissionGuard>

            <button
              onClick={() => setShowCreateModal(true)}
              className="flex-shrink-0 px-3 py-2 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {t('transactions.createTransaction')}
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            {/* Desktop Tab Navigation */}
            <nav className="-mb-px hidden md:flex space-x-8 px-6" aria-label="Tabs">
              {availableTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span>{tab.label}</span>
                  {tab.adminOnly && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      {t('common.admin')}
                    </span>
                  )}
                </button>
              ))}
            </nav>

            {/* Mobile Tab Navigation - Horizontal Scroll */}
            <div className="md:hidden">
              <nav className="-mb-px flex overflow-x-auto scrollbar-hide px-4 mobile-tab-nav" aria-label="Tabs">
                {availableTabs.map((tab, index) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      } flex-shrink-0 py-3 px-3 border-b-2 font-medium text-sm flex items-center space-x-1.5 transition-colors min-w-max rounded-t-lg ${index === 0 ? 'ml-0' : 'ml-1'}`}
                  >
                    <span className="text-base">{tab.icon}</span>
                    <span className="text-xs whitespace-nowrap">{tab.label}</span>
                    {tab.adminOnly && (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {t('common.admin')}
                      </span>
                    )}
                  </button>
                ))}
              </nav>

              {/* Mobile scroll indicator */}
              <div className="flex justify-center py-1">
                <div className="flex space-x-1">
                  {availableTabs.map((tab) => (
                    <div
                      key={`indicator-${tab.id}`}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${activeTab === tab.id ? 'bg-blue-500' : 'bg-gray-300'
                        }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Tab Description */}
          <div className="px-4 sm:px-6 py-3 bg-gray-50 border-b border-gray-200">
            <p className="text-xs sm:text-sm text-gray-600">
              {availableTabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>

          {/* Tab Content */}
          <div className="p-4 sm:p-6">
            {renderTabContent()}
          </div>
        </div>

        {/* Create Transaction Modal */}
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title={t('transactions.createNewTransaction')}
          size="lg"
        >
          <TransactionForm
            onSubmit={handleCreateTransaction}
            onClose={() => setShowCreateModal(false)}
          />
        </Modal>

        {/* Two-Phase Order Wizard */}
        <TwoPhaseOrderWizard
          isOpen={showOrderWizard}
          onClose={() => setShowOrderWizard(false)}
          onOrderComplete={(order) => {
            setRefreshTrigger(prev => prev + 1);
            // console.log('Order created:', order);
          }}
        />

        {/* Part Usage Recorder */}
        <PartUsageRecorder
          isOpen={showPartUsageRecorder}
          onClose={() => setShowPartUsageRecorder(false)}
          onUsageRecorded={(transaction) => {
            setRefreshTrigger(prev => prev + 1);
            // console.log('Usage recorded:', transaction);
          }}
        />
      </div>
    </PermissionGuard>
  );
};

export default Transactions;
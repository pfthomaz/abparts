// frontend/src/pages/Transactions.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import PermissionGuard from '../components/PermissionGuard';
import { PERMISSIONS, isAdmin } from '../utils/permissions';
import TransactionHistory from '../components/TransactionHistory';
import TransactionForm from '../components/TransactionForm';
import TransactionAnalyticsDashboard from '../components/TransactionAnalyticsDashboard';
import TransactionApprovalWorkflow from '../components/TransactionApprovalWorkflow';
import TransactionReversalInterface from '../components/TransactionReversalInterface';
import Modal from '../components/Modal';
import { transactionService } from '../services/transactionService';

const Transactions = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('history');
  const [showCreateModal, setShowCreateModal] = useState(false);
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
      label: 'Transaction History',
      icon: '📋',
      description: 'View and search transaction records',
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS
    },
    {
      id: 'analytics',
      label: 'Analytics & Reports',
      icon: '📊',
      description: 'Transaction analytics and reporting',
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS
    },
    {
      id: 'approvals',
      label: 'Approvals',
      icon: '✅',
      description: 'Manage transaction approvals',
      permission: PERMISSIONS.VIEW_ORG_TRANSACTIONS,
      adminOnly: true
    },
    {
      id: 'reversals',
      label: 'Reversals & Corrections',
      icon: '↩️',
      description: 'Reverse or correct transactions',
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Transaction Management</h1>
            <p className="text-gray-600 mt-1">
              Manage and track all inventory transactions across your organization
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Create Transaction
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
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
                      Admin
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Description */}
          <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
            <p className="text-sm text-gray-600">
              {availableTabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {renderTabContent()}
          </div>
        </div>

        {/* Create Transaction Modal */}
        <Modal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          title="Create New Transaction"
          size="lg"
        >
          <TransactionForm
            onSubmit={handleCreateTransaction}
            onClose={() => setShowCreateModal(false)}
          />
        </Modal>
      </div>
    </PermissionGuard>
  );
};

export default Transactions;
// frontend/src/components/ChecklistItemManager.js

import React, { useState, useEffect } from 'react';
import {
  getChecklistItems,
  createChecklistItem,
  updateChecklistItem,
  deleteChecklistItem,
  reorderChecklistItems
} from '../services/maintenanceProtocolsService';
import ChecklistItemForm from './ChecklistItemForm';
import { useTranslation } from '../hooks/useTranslation';

const ChecklistItemManager = ({ protocol, onBack, onUpdate }) => {
  const { t } = useTranslation();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showItemForm, setShowItemForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [draggedItem, setDraggedItem] = useState(null);

  useEffect(() => {
    loadItems();
  }, [protocol.id]);

  const loadItems = async () => {
    try {
      setLoading(true);
      const data = await getChecklistItems(protocol.id);
      setItems(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddItem = () => {
    setEditingItem(null);
    setShowItemForm(true);
  };

  const handleEditItem = (item) => {
    setEditingItem(item);
    setShowItemForm(true);
  };

  const handleDeleteItem = async (itemId) => {
    if (!window.confirm(t('checklistManager.confirmDelete'))) {
      return;
    }

    try {
      await deleteChecklistItem(protocol.id, itemId);
      loadItems();
      onUpdate();
    } catch (err) {
      alert(`${t('checklistManager.deleteFailed')}: ${err.message}`);
    }
  };

  const handleItemSaved = () => {
    setShowItemForm(false);
    setEditingItem(null);
    loadItems();
    onUpdate();
  };

  const handleDragStart = (e, item) => {
    setDraggedItem(item);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e, targetItem) => {
    e.preventDefault();
    
    if (!draggedItem || draggedItem.id === targetItem.id) {
      setDraggedItem(null);
      return;
    }

    // Reorder items
    const newItems = [...items];
    const draggedIndex = newItems.findIndex(i => i.id === draggedItem.id);
    const targetIndex = newItems.findIndex(i => i.id === targetItem.id);

    newItems.splice(draggedIndex, 1);
    newItems.splice(targetIndex, 0, draggedItem);

    // Update order numbers
    const itemOrders = newItems.map((item, index) => ({
      id: item.id,
      order: index + 1
    }));

    try {
      await reorderChecklistItems(protocol.id, itemOrders);
      setItems(newItems.map((item, index) => ({ ...item, item_order: index + 1 })));
      onUpdate();
    } catch (err) {
      alert(`${t('checklistManager.reorderFailed')}: ${err.message}`);
      loadItems(); // Reload to get correct order
    }

    setDraggedItem(null);
  };

  const getItemTypeIcon = (type) => {
    const icons = {
      check: '✓',
      service: '🔧',
      replacement: '🔄'
    };
    return icons[type] || '•';
  };

  const getItemTypeBadge = (type) => {
    const colors = {
      check: 'bg-blue-100 text-blue-800',
      service: 'bg-green-100 text-green-800',
      replacement: 'bg-purple-100 text-purple-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (showItemForm) {
    return (
      <ChecklistItemForm
        protocolId={protocol.id}
        item={editingItem}
        existingItems={items}
        onSave={handleItemSaved}
        onCancel={() => {
          setShowItemForm(false);
          setEditingItem(null);
        }}
      />
    );
  }

  return (
    <div>
      <div className="mb-6">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← {t('checklistManager.backToProtocols')}
        </button>
        <h2 className="text-2xl font-bold text-gray-900">{t('checklistManager.title')}</h2>
        <div className="mt-2 flex items-center gap-4">
          <span className="text-gray-600">{t('checklistManager.protocol')}: <span className="font-medium">{protocol.name}</span></span>
          <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
            {t(`maintenanceProtocols.types.${protocol.protocol_type}`)}
          </span>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="mb-6">
        <button
          onClick={handleAddItem}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          + {t('checklistManager.addItem')}
        </button>
      </div>

      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">{t('checklistManager.loading')}</p>
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">{t('checklistManager.noItems')}</p>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200">
            <p className="text-sm text-gray-600">
              💡 {t('checklistManager.dragTip')}
            </p>
          </div>
          
          <div className="divide-y divide-gray-200">
            {items.map((item, index) => (
              <div
                key={item.id}
                draggable
                onDragStart={(e) => handleDragStart(e, item)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, item)}
                className={`p-4 hover:bg-gray-50 cursor-move transition-colors ${
                  draggedItem?.id === item.id ? 'opacity-50' : ''
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded flex items-center justify-center text-gray-600 font-medium">
                    {index + 1}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{getItemTypeIcon(item.item_type)}</span>
                          <h3 className="font-medium text-gray-900">{item.item_description}</h3>
                          {item.is_critical && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                              {t('checklistManager.critical')}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-3 text-sm text-gray-600">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getItemTypeBadge(item.item_type)}`}>
                            {t(`checklistManager.itemTypes.${item.item_type}`)}
                          </span>
                          
                          {item.item_category && (
                            <span className="text-gray-500">
                              {item.item_category}
                            </span>
                          )}
                          
                          {item.estimated_duration_minutes && (
                            <span className="text-gray-500">
                              ⏱️ {item.estimated_duration_minutes} {t('checklistManager.minutes')}
                            </span>
                          )}
                          
                          {item.part && (
                            <span className="text-blue-600">
                              🔧 {item.part.name}
                              {item.estimated_quantity && ` (${item.estimated_quantity})`}
                            </span>
                          )}
                        </div>
                        
                        {item.notes && (
                          <p className="text-sm text-gray-500 mt-2">{item.notes}</p>
                        )}
                      </div>
                      
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={() => handleEditItem(item)}
                          className="text-blue-600 hover:text-blue-800 text-sm px-3 py-1 rounded hover:bg-blue-50"
                        >
                          {t('checklistManager.edit')}
                        </button>
                        <button
                          onClick={() => handleDeleteItem(item.id)}
                          className="text-red-600 hover:text-red-800 text-sm px-3 py-1 rounded hover:bg-red-50"
                        >
                          {t('checklistManager.delete')}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChecklistItemManager;

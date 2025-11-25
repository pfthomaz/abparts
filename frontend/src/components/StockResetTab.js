// frontend/src/components/StockResetTab.js

import { useState, useEffect } from 'react';
import PartSearchSelector from './PartSearchSelector';
import { warehouseService } from '../services/warehouseService';
import { api } from '../services/api';

const StockResetTab = ({ warehouse, onSuccess }) => {
  const [adjustments, setAdjustments] = useState([]);
  const [allParts, setAllParts] = useState([]);
  const [selectedPartId, setSelectedPartId] = useState('');
  const [reason, setReason] = useState('Initial Stock Entry');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [error, setError] = useState(null);

  // Helper to format quantity based on unit of measure
  const formatQuantity = (qty, unit) => {
    const lowerUnit = (unit || '').toLowerCase();
    // Use decimals for liquids/volumes, integers for countable items
    if (lowerUnit.includes('liter') || lowerUnit.includes('gallon') || 
        lowerUnit.includes('ml') || lowerUnit.includes('kg') || lowerUnit.includes('gram')) {
      return parseFloat(qty).toFixed(3);
    }
    return Math.round(parseFloat(qty));
  };

  // Load current inventory and all parts
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch all parts first (backend max limit is 1000)
        const partsResponse = await api.get('/parts/?limit=1000');
        const parts = Array.isArray(partsResponse) ? partsResponse : (partsResponse.items || []);
        console.log('Loaded parts for search:', parts.length, 'parts');
        setAllParts(parts);
        
        // Fetch inventory with part details using the warehouse-specific endpoint
        const inventoryResponse = await api.get(`/inventory/warehouse/${warehouse.id}?limit=1000`);
        const inventory = Array.isArray(inventoryResponse) ? inventoryResponse : [];
        console.log('Loaded inventory for warehouse:', inventory.length, 'items');
        
        // Create a map of part_id to part details
        const partsMap = {};
        parts.forEach(part => {
          partsMap[part.id] = part;
        });
        
        // Filter inventory to only show parts with stock > 0, valid part data, and remove duplicates
        const uniqueInventory = [];
        const seenPartIds = new Set();
        
        inventory.forEach(item => {
          const stock = parseFloat(item.current_stock || 0);
          const part = partsMap[item.part_id];
          
          // Only include if:
          // 1. Stock > 0
          // 2. Part exists in parts list (not orphaned)
          // 3. Not already added (no duplicates)
          if (stock > 0 && part && !seenPartIds.has(item.part_id)) {
            seenPartIds.add(item.part_id);
            uniqueInventory.push(item);
          }
        });
        
        setAdjustments(uniqueInventory.map(item => {
          const part = partsMap[item.part_id];
          return {
            part_id: item.part_id,
            part_number: part.part_number,
            part_name: part.name,
            current_quantity: parseFloat(item.current_stock),
            new_quantity: parseFloat(item.current_stock),
            unit_of_measure: item.unit_of_measure || part.unit_of_measure || 'units'
          };
        }));
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load inventory and parts');
      }
    };

    if (warehouse?.id) {
      fetchData();
    }
  }, [warehouse]);

  const handleAddPart = async (partId) => {
    const part = allParts.find(p => p.id === partId);
    if (!part) return;
    
    // Check if part already in list
    if (adjustments.find(a => a.part_id === partId)) {
      alert('Part already in adjustment list');
      setSelectedPartId('');
      return;
    }
    
    // Fetch current inventory for this part in this warehouse
    let currentStock = 0;
    try {
      const inventoryResponse = await api.get(`/inventory/warehouse/${warehouse.id}?limit=1000`);
      const inventory = Array.isArray(inventoryResponse) ? inventoryResponse : [];
      console.log('📦 Fetched inventory for warehouse:', warehouse.id, 'Total items:', inventory.length);
      
      // Find the specific part in this warehouse's inventory
      const partInventory = inventory.find(item => item.part_id === partId);
      if (partInventory) {
        currentStock = parseFloat(partInventory.current_stock || 0);
        console.log('✅ Found existing inventory for part:', part.part_number, 'Current stock:', currentStock);
      } else {
        console.log('ℹ️ No existing inventory for part:', part.part_number, 'Starting with 0');
      }
    } catch (err) {
      console.error('❌ Error fetching inventory for part:', err);
      // Continue with 0 if fetch fails
    }
    
    const newAdjustment = {
      part_id: part.id,
      part_number: part.part_number,
      part_name: part.name,
      current_quantity: currentStock,
      new_quantity: currentStock,
      unit_of_measure: part.unit_of_measure || 'units'
    };
    
    console.log('➕ Adding part to adjustments:', newAdjustment);
    setAdjustments([...adjustments, newAdjustment]);
    
    setSelectedPartId(''); // Clear selection
  };

  const handleQuantityChange = (partId, newQty) => {
    setAdjustments(adjustments.map(adj =>
      adj.part_id === partId ? { ...adj, new_quantity: parseFloat(newQty) || 0 } : adj
    ));
  };

  const handleRemovePart = (partId) => {
    setAdjustments(adjustments.filter(adj => adj.part_id !== partId));
  };

  const getChangedAdjustments = () => {
    return adjustments.filter(adj => adj.new_quantity !== adj.current_quantity);
  };

  const getSummary = () => {
    const changes = getChangedAdjustments();
    const increases = changes.filter(adj => adj.new_quantity > adj.current_quantity);
    const decreases = changes.filter(adj => adj.new_quantity < adj.current_quantity);
    
    const totalIncrease = increases.reduce((sum, adj) => sum + (adj.new_quantity - adj.current_quantity), 0);
    const totalDecrease = decreases.reduce((sum, adj) => sum + (adj.current_quantity - adj.new_quantity), 0);
    
    return {
      totalChanges: changes.length,
      totalIncrease: Math.round(totalIncrease),
      totalDecrease: Math.round(totalDecrease)
    };
  };

  const handleSubmit = async () => {
    const changes = getChangedAdjustments();
    
    if (changes.length === 0) {
      alert('No changes to apply');
      return;
    }

    if (!reason) {
      alert('Please select a reason for the stock reset');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        adjustments: changes.map(adj => ({
          part_id: adj.part_id,
          new_quantity: adj.new_quantity.toString(),
          unit_of_measure: adj.unit_of_measure
        })),
        reason,
        notes
      };
      
      console.log('📤 Submitting stock reset:', payload);
      console.log('📊 Changes being applied:', changes.map(adj => ({
        part: adj.part_number,
        current: adj.current_quantity,
        new: adj.new_quantity,
        diff: adj.new_quantity - adj.current_quantity
      })));
      
      const result = await warehouseService.resetStock(warehouse.id, payload);
      console.log('✅ Stock reset response:', result);
      
      alert(`Stock reset successful! ${changes.length} parts adjusted.`);
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error('❌ Error resetting stock:', err);
      setError(err.message || 'Failed to reset stock');
    } finally {
      setLoading(false);
      setShowPreview(false);
    }
  };

  const summary = getSummary();

  return (
    <div className="p-6">
      {/* Warning Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              <strong>Warning:</strong> This will adjust inventory quantities. Use for initial setup, stocktake corrections, or system reconciliation.
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Part Search */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Add Part to Adjustment List
        </label>
        <div className="relative">
          <PartSearchSelector
            parts={allParts}
            value={selectedPartId}
            onChange={handleAddPart}
            placeholder="Search by part number, name, or description..."
            disabled={loading}
            className="relative z-10"
          />
        </div>
        {allParts.length === 0 && (
          <p className="text-sm text-red-500 mt-1">⚠️ No parts loaded. Check console for errors.</p>
        )}
        {allParts.length > 0 && (
          <p className="text-sm text-green-600 mt-1">✓ {allParts.length} parts available for search</p>
        )}
      </div>

      {/* Adjustments Table */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Stock Adjustments ({adjustments.length} parts)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 border">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part Number
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part Name
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  New Quantity
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Δ
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {adjustments.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    No parts in adjustment list. Use the search above to add parts.
                  </td>
                </tr>
              ) : (
                adjustments.map(adj => {
                  const diff = adj.new_quantity - adj.current_quantity;
                  return (
                    <tr key={adj.part_id} className={diff !== 0 ? 'bg-blue-50' : ''}>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {adj.part_number}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        {adj.part_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-600">
                        {formatQuantity(adj.current_quantity, adj.unit_of_measure)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <input
                          type="number"
                          step={adj.unit_of_measure?.toLowerCase().includes('liter') || 
                                adj.unit_of_measure?.toLowerCase().includes('kg') ? "0.001" : "1"}
                          min="0"
                          value={adj.new_quantity}
                          onChange={(e) => handleQuantityChange(adj.part_id, e.target.value)}
                          className="w-28 px-2 py-1 border border-gray-300 rounded text-right focus:ring-blue-500 focus:border-blue-500"
                          disabled={loading}
                        />
                      </td>
                      <td className={`px-4 py-3 text-sm text-right font-medium ${
                        diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-500'
                      }`}>
                        {diff > 0 ? '+' : ''}{formatQuantity(diff, adj.unit_of_measure)}
                      </td>
                      <td className="px-4 py-3 text-center">
                        <button
                          onClick={() => handleRemovePart(adj.part_id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                          disabled={loading}
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Reason and Notes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Reason <span className="text-red-500">*</span>
          </label>
          <select
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          >
            <option value="Initial Stock Entry">Initial Stock Entry</option>
            <option value="Physical Stocktake Correction">Physical Stocktake Correction</option>
            <option value="System Reconciliation">System Reconciliation</option>
            <option value="Damaged Goods Write-off">Damaged Goods Write-off</option>
            <option value="Found Stock">Found Stock</option>
            <option value="Other">Other</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Optional notes..."
            disabled={loading}
          />
        </div>
      </div>

      {/* Summary */}
      {summary.totalChanges > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h4 className="font-medium text-blue-900 mb-2">Summary</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-blue-700">Parts to adjust:</span>
              <span className="ml-2 font-semibold text-blue-900">{summary.totalChanges}</span>
            </div>
            <div>
              <span className="text-green-700">Total increase:</span>
              <span className="ml-2 font-semibold text-green-900">{summary.totalIncrease} units</span>
            </div>
            <div>
              <span className="text-red-700">Total decrease:</span>
              <span className="ml-2 font-semibold text-red-900">{summary.totalDecrease} units</span>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={() => setShowPreview(true)}
          disabled={loading || summary.totalChanges === 0}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Preview Changes
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading || summary.totalChanges === 0}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Applying...' : 'Apply Stock Reset'}
        </button>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Confirm Stock Reset</h3>
            
            <p className="text-gray-700 mb-4">
              You are about to adjust <strong>{summary.totalChanges} parts</strong> in <strong>{warehouse.name}</strong>:
            </p>

            <div className="bg-gray-50 rounded p-4 mb-4 max-h-60 overflow-y-auto">
              {getChangedAdjustments().map(adj => {
                const diff = adj.new_quantity - adj.current_quantity;
                return (
                  <div key={adj.part_id} className="flex justify-between py-2 border-b last:border-b-0">
                    <span className="font-medium">{adj.part_number}</span>
                    <span className={diff > 0 ? 'text-green-600' : 'text-red-600'}>
                      {formatQuantity(adj.current_quantity, adj.unit_of_measure)} → {formatQuantity(adj.new_quantity, adj.unit_of_measure)} 
                      ({diff > 0 ? '+' : ''}{formatQuantity(diff, adj.unit_of_measure)})
                    </span>
                  </div>
                );
              })}
            </div>

            <div className="mb-4">
              <p className="text-sm text-gray-600"><strong>Reason:</strong> {reason}</p>
              {notes && <p className="text-sm text-gray-600"><strong>Notes:</strong> {notes}</p>}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
              <p className="text-sm text-blue-800">
                <strong>This action will:</strong>
              </p>
              <ul className="text-sm text-blue-700 mt-2 space-y-1">
                <li>✓ Create adjustment transactions for audit trail</li>
                <li>✓ Update inventory quantities</li>
                <li>✓ Log changes with reason and notes</li>
              </ul>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleSubmit}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                disabled={loading}
              >
                {loading ? 'Applying...' : 'Confirm Reset'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockResetTab;

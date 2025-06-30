// frontend/src/components/StockAdjustmentForm.js
import React, { useState, useEffect, useContext } from 'react';
import { useAuth } from '../AuthContext';

const StockAdjustmentReason = {
    STOCKTAKE_DISCREPANCY: "Stocktake Discrepancy",
    DAMAGED_GOODS: "Damaged Goods",
    FOUND_STOCK: "Found Stock",
    INITIAL_STOCK_ENTRY: "Initial Stock Entry",
    RETURN_TO_VENDOR: "Return to Vendor",
    CUSTOMER_RETURN_RESALABLE: "Customer Return - Resalable",
    CUSTOMER_RETURN_DAMAGED: "Customer Return - Damaged",
    OTHER: "Other",
};

const StockAdjustmentForm = ({ inventoryItem, onSuccess, onCancel, API_BASE_URL, parts, organizations }) => {
    const { token } = useContext(useAuth);
    const [quantityAdjusted, setQuantityAdjusted] = useState('');
    const [reasonCode, setReasonCode] = useState(StockAdjustmentReason.STOCKTAKE_DISCREPANCY);
    const [notes, setNotes] = useState('');
    const [error, setError] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);

        if (!inventoryItem || !inventoryItem.id) {
            setError("Inventory item is not specified.");
            setSubmitting(false);
            return;
        }

        const parsedQuantity = parseInt(quantityAdjusted, 10);
        if (isNaN(parsedQuantity)) {
            setError("Quantity adjusted must be a valid number.");
            setSubmitting(false);
            return;
        }

        if (!reasonCode) {
            setError("Reason code is required.");
            setSubmitting(false);
            return;
        }

        const adjustmentData = {
            quantity_adjusted: parsedQuantity,
            reason_code: reasonCode,
            notes: notes,
        };

        try {
            const response = await fetch(`${API_BASE_URL}/stock_adjustments/inventory/${inventoryItem.id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify(adjustmentData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to create stock adjustment: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Stock adjustment successful:', result);
            if (onSuccess) {
                onSuccess(result);
            }
        } catch (err) {
            console.error("Stock adjustment error:", err);
            setError(err.message || "An unexpected error occurred.");
        } finally {
            setSubmitting(false);
        }
    };

    if (!inventoryItem) {
        return <p>Loading inventory details or inventory item not selected.</p>;
    }

    const getPartDisplayInfo = (partId) => {
        if (!parts) return 'Loading parts...';
        const part = parts.find(p => p.id === partId);
        return part ? `${part.part_number} - ${part.name}` : 'Unknown Part';
    };

    const getOrganizationDisplayInfo = (orgId) => {
        if (!organizations) return 'Loading organizations...';
        const org = organizations.find(o => o.id === orgId);
        return org ? org.name : 'Unknown Organization';
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-lg font-semibold">
                Adjust Stock for: {getPartDisplayInfo(inventoryItem.part_id)}
            </h3>
            <p className="text-sm text-gray-600">
                Current Stock: {inventoryItem.current_stock} at Organization: {getOrganizationDisplayInfo(inventoryItem.organization_id)}
            </p>

            <div>
                <label htmlFor="quantityAdjusted" className="block text-sm font-medium text-gray-700">
                    Quantity Adjusted <span className="text-red-500">*</span>
                </label>
                <input
                    type="number"
                    name="quantityAdjusted"
                    id="quantityAdjusted"
                    value={quantityAdjusted}
                    onChange={(e) => setQuantityAdjusted(e.target.value)}
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="e.g., -5 or 10"
                />
                <p className="mt-1 text-xs text-gray-500">Positive to increase stock, negative to decrease.</p>
            </div>

            <div>
                <label htmlFor="reasonCode" className="block text-sm font-medium text-gray-700">
                    Reason Code <span className="text-red-500">*</span>
                </label>
                <select
                    name="reasonCode"
                    id="reasonCode"
                    value={reasonCode}
                    onChange={(e) => setReasonCode(e.target.value)}
                    required
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                    {Object.entries(StockAdjustmentReason).map(([key, value]) => (
                        <option key={key} value={value}>{value}</option>
                    ))}
                </select>
            </div>

            <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                    Notes
                </label>
                <textarea
                    name="notes"
                    id="notes"
                    rows="3"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Optional details about the adjustment..."
                ></textarea>
            </div>

            {error && <p className="text-sm text-red-600 bg-red-100 p-2 rounded-md">{error}</p>}

            <div className="flex justify-end space-x-3">
                <button
                    type="button"
                    onClick={onCancel}
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                    Cancel
                </button>
                <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                    {submitting ? 'Submitting...' : 'Submit Adjustment'}
                </button>
            </div>
        </form>
    );
};

export default StockAdjustmentForm;

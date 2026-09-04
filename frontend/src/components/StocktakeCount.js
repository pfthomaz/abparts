// frontend/src/components/StocktakeCount.js
//
// Mobile-first physical inventory counting screen.
// The operator walks the warehouse, records the actual quantity of each part,
// and can add parts that were found in stock but not on the worksheet.
// An admin / super-admin then approves, which resets warehouse inventory to the
// counted quantities (via completeStocktake with apply_adjustments).

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { inventoryWorkflowService } from '../services/inventoryWorkflowService';
import { partsService } from '../services/partsService';
import PartSearchSelector from './PartSearchSelector';
import { printStocktake } from '../utils/printStocktake';

const num = (v) => (v === null || v === undefined || v === '' ? null : parseFloat(v));

const DiscrepancyChip = ({ expected, actual }) => {
  if (actual === null || actual === undefined) return null;
  const d = parseFloat(actual) - parseFloat(expected || 0);
  if (d === 0) {
    return <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">✓ Match</span>;
  }
  const pct = expected && parseFloat(expected) !== 0 ? (d / parseFloat(expected)) * 100 : null;
  const big = pct !== null && Math.abs(pct) > 10;
  const cls = big ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800';
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}>
      {d > 0 ? '+' : ''}{d.toFixed(3)}{pct !== null ? ` (${pct.toFixed(0)}%)` : ''}
    </span>
  );
};

const CountCard = ({ item, draft, saving, disabled, onDraft, onCommit, onStep, onZero }) => {
  const value = draft !== undefined ? draft : (item.actual_quantity != null ? String(item.actual_quantity) : '');
  const counted = item.actual_quantity != null;
  const unexpected = parseFloat(item.expected_quantity || 0) === 0;

  return (
    <div className={`rounded-lg border p-3 shadow-sm ${counted ? 'border-green-200 bg-green-50/40' : 'border-gray-200 bg-white'}`}>
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-900 break-words">{item.part_number}</span>
            {unexpected && (
              <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-purple-700">Unexpected</span>
            )}
          </div>
          <div className="text-sm text-gray-600 break-words">{item.part_name}</div>
          <div className="mt-1 text-xs text-gray-500">
            Expected: <span className="font-medium text-gray-700">{parseFloat(item.expected_quantity || 0).toFixed(3)}</span> {item.unit_of_measure}
          </div>
        </div>
        <div className="shrink-0">{counted && <DiscrepancyChip expected={item.expected_quantity} actual={item.actual_quantity} />}</div>
      </div>

      <div className="mt-3 flex items-center gap-2">
        <button
          type="button"
          disabled={disabled}
          onClick={() => onStep(item, -1)}
          className="h-11 w-11 shrink-0 rounded-md border border-gray-300 bg-white text-2xl font-bold text-gray-700 active:bg-gray-100 disabled:opacity-40"
          aria-label="decrease"
        >−</button>
        <input
          type="text"
          inputMode="decimal"
          disabled={disabled}
          value={value}
          onChange={(e) => onDraft(item.id, e.target.value)}
          onBlur={() => onCommit(item)}
          placeholder="count"
          className="h-11 w-24 rounded-md border border-gray-300 text-center text-xl font-semibold focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50"
        />
        <button
          type="button"
          disabled={disabled}
          onClick={() => onStep(item, 1)}
          className="h-11 w-11 shrink-0 rounded-md border border-gray-300 bg-white text-2xl font-bold text-gray-700 active:bg-gray-100 disabled:opacity-40"
          aria-label="increase"
        >＋</button>
        <button
          type="button"
          disabled={disabled}
          onClick={() => onZero(item)}
          className="h-11 shrink-0 rounded-md border border-gray-300 bg-white px-3 text-sm font-medium text-gray-700 active:bg-gray-100 disabled:opacity-40"
        >None in stock</button>
        <span className="ml-auto text-xs text-gray-400">{saving ? 'Saving…' : (counted ? '✓ counted' : '')}</span>
      </div>
    </div>
  );
};

const StocktakeCount = ({ stocktake, currentUser, onClose, onUpdated }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('code'); // 'code' | 'name'
  const [search, setSearch] = useState('');
  const [drafts, setDrafts] = useState({});
  const [savingIds, setSavingIds] = useState(() => new Set());
  const [busy, setBusy] = useState(false);

  const [showAddPart, setShowAddPart] = useState(false);
  const [parts, setParts] = useState([]);
  const [newPartId, setNewPartId] = useState('');
  const [newPartQty, setNewPartQty] = useState('');
  const [addingPart, setAddingPart] = useState(false);

  const [showApprove, setShowApprove] = useState(false);
  const [applyAdjustments, setApplyAdjustments] = useState(true);

  const isAdmin = ['admin', 'super_admin'].includes(currentUser?.role);
  const readOnly = stocktake.status === 'completed' || stocktake.status === 'cancelled';
  const editable = !readOnly;

  const loadItems = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await inventoryWorkflowService.getStocktakeItems(stocktake.id);
      setItems(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || 'Failed to load stocktake items');
    } finally {
      setLoading(false);
    }
  }, [stocktake.id]);

  useEffect(() => { loadItems(); }, [loadItems]);

  const counted = items.filter((i) => i.actual_quantity != null).length;
  const total = items.length;
  const allCounted = total > 0 && counted === total;
  const pct = total ? Math.round((counted / total) * 100) : 0;

  const visibleItems = useMemo(() => {
    const q = search.trim().toLowerCase();
    let list = items;
    if (q) {
      list = list.filter(
        (i) => (i.part_number || '').toLowerCase().includes(q) || (i.part_name || '').toLowerCase().includes(q)
      );
    }
    return [...list].sort((a, b) =>
      sortBy === 'name'
        ? (a.part_name || '').localeCompare(b.part_name || '', undefined, { sensitivity: 'base' })
        : (a.part_number || '').localeCompare(b.part_number || '', undefined, { numeric: true, sensitivity: 'base' })
    );
  }, [items, search, sortBy]);

  const setSaving = (id, on) => setSavingIds((prev) => {
    const next = new Set(prev);
    if (on) next.add(id); else next.delete(id);
    return next;
  });

  const persist = async (item, qty) => {
    const parsed = num(qty);
    if (parsed === null || Number.isNaN(parsed)) return;
    if (item.actual_quantity != null && parseFloat(item.actual_quantity) === parsed) return;
    setSaving(item.id, true);
    setError('');
    try {
      const updated = await inventoryWorkflowService.updateStocktakeItem(item.id, {
        actual_quantity: parsed,
        notes: item.notes || '',
      });
      setItems((prev) => prev.map((i) => (i.id === item.id ? { ...i, ...updated } : i)));
      setDrafts((prev) => { const n = { ...prev }; delete n[item.id]; return n; });
    } catch (err) {
      setError(err.message || 'Failed to save count');
    } finally {
      setSaving(item.id, false);
    }
  };

  const handleDraft = (id, val) => setDrafts((prev) => ({ ...prev, [id]: val }));
  const handleCommit = (item) => {
    const d = drafts[item.id];
    if (d !== undefined && d !== '') persist(item, d);
  };
  const handleStep = (item, delta) => {
    const base = drafts[item.id] !== undefined && drafts[item.id] !== ''
      ? parseFloat(drafts[item.id])
      : (item.actual_quantity != null ? parseFloat(item.actual_quantity) : parseFloat(item.expected_quantity || 0));
    const next = Math.max(0, (Number.isNaN(base) ? 0 : base) + delta);
    handleDraft(item.id, String(next));
    persist(item, next);
  };
  const handleZero = (item) => { handleDraft(item.id, '0'); persist(item, 0); };

  const openAddPart = async () => {
    setShowAddPart(true);
    if (parts.length === 0) {
      try {
        const data = await partsService.getParts();
        setParts(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err.message || 'Failed to load parts list');
      }
    }
  };

  const partsNotInStocktake = useMemo(() => {
    const have = new Set(items.map((i) => i.part_id));
    return parts.filter((p) => !have.has(p.id));
  }, [parts, items]);

  const submitNewPart = async () => {
    if (!newPartId) return;
    setAddingPart(true);
    setError('');
    try {
      const created = await inventoryWorkflowService.addStocktakeItem(stocktake.id, {
        part_id: newPartId,
        actual_quantity: newPartQty === '' ? null : parseFloat(newPartQty),
      });
      setItems((prev) => [created, ...prev]);
      setNewPartId('');
      setNewPartQty('');
      setShowAddPart(false);
    } catch (err) {
      setError(err.message || 'Failed to add part');
    } finally {
      setAddingPart(false);
    }
  };

  const approve = async () => {
    setBusy(true);
    setError('');
    try {
      await inventoryWorkflowService.completeStocktake(stocktake.id, applyAdjustments);
      setShowApprove(false);
      onUpdated && onUpdated();
      onClose && onClose();
    } catch (err) {
      setError(err.message || 'Failed to approve stocktake');
    } finally {
      setBusy(false);
    }
  };

  const discrepancyCount = items.filter(
    (i) => i.actual_quantity != null && parseFloat(i.actual_quantity) !== parseFloat(i.expected_quantity || 0)
  ).length;

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-gray-100">
      {/* Header */}
      <div className="shrink-0 border-b bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <div className="truncate text-lg font-bold text-gray-900">{stocktake.warehouse_name}</div>
            <div className="truncate text-xs text-gray-500">
              {stocktake.organization_name} · {stocktake.status.replace('_', ' ')}
            </div>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100"
          >Close</button>
        </div>

        <div className="mt-2">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <span>{counted} of {total} counted{discrepancyCount ? ` · ${discrepancyCount} discrepancies` : ''}</span>
            <span>{pct}%</span>
          </div>
          <div className="mt-1 h-1.5 w-full overflow-hidden rounded-full bg-gray-200">
            <div className="h-full bg-blue-600 transition-all" style={{ width: `${pct}%` }} />
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2">
          <div className="flex overflow-hidden rounded-md border border-gray-300 text-sm">
            <button
              onClick={() => setSortBy('code')}
              className={`px-3 py-1.5 font-medium ${sortBy === 'code' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
            >Code</button>
            <button
              onClick={() => setSortBy('name')}
              className={`px-3 py-1.5 font-medium ${sortBy === 'name' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}`}
            >Name</button>
          </div>
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search part…"
            className="h-9 flex-1 rounded-md border border-gray-300 px-3 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {error && (
        <div className="shrink-0 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div>
      )}

      {/* Item list */}
      <div className="flex-1 space-y-2 overflow-y-auto p-3">
        {loading ? (
          <div className="py-10 text-center text-gray-500">Loading…</div>
        ) : visibleItems.length === 0 ? (
          <div className="py-10 text-center text-gray-500">
            {items.length === 0 ? 'No parts on this worksheet yet.' : 'No parts match your search.'}
          </div>
        ) : (
          visibleItems.map((item) => (
            <CountCard
              key={item.id}
              item={item}
              draft={drafts[item.id]}
              saving={savingIds.has(item.id)}
              disabled={!editable || busy}
              onDraft={handleDraft}
              onCommit={handleCommit}
              onStep={handleStep}
              onZero={handleZero}
            />
          ))
        )}
      </div>

      {/* Footer actions */}
      <div className="shrink-0 space-y-2 border-t bg-white p-3">
        <div className="flex gap-2">
          {editable && (
            <button
              onClick={openAddPart}
              className="flex-1 rounded-md border border-dashed border-blue-400 py-2.5 text-sm font-medium text-blue-700 active:bg-blue-50"
            >+ Add part found in stock</button>
          )}
          <button
            onClick={() => printStocktake(stocktake, items, { sortBy })}
            className="rounded-md border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 active:bg-gray-100"
          >Print</button>
        </div>

        {readOnly ? (
          <button onClick={onClose} className="w-full rounded-md bg-gray-800 py-3 font-semibold text-white">Close</button>
        ) : isAdmin ? (
          <button
            onClick={() => setShowApprove(true)}
            disabled={!allCounted || busy}
            className="w-full rounded-md bg-green-600 py-3 font-semibold text-white active:bg-green-700 disabled:opacity-40"
          >
            {allCounted ? 'Approve & update inventory' : `Count all parts first (${total - counted} left)`}
          </button>
        ) : (
          <button
            onClick={onClose}
            className="w-full rounded-md bg-blue-600 py-3 font-semibold text-white active:bg-blue-700"
          >
            {allCounted ? 'Done — submit for approval' : `Save & close (${total - counted} still to count)`}
          </button>
        )}
        {!isAdmin && !readOnly && (
          <p className="text-center text-xs text-gray-500">Your counts are saved automatically. An admin will review and approve.</p>
        )}
      </div>

      {/* Add-part sheet */}
      {showAddPart && (
        <div className="fixed inset-0 z-[60] flex items-end bg-black/40 sm:items-center sm:justify-center" onClick={() => setShowAddPart(false)}>
          <div className="w-full rounded-t-2xl bg-white p-4 sm:max-w-md sm:rounded-2xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900">Add part found in stock</h3>
            <p className="mt-1 text-sm text-gray-500">Its expected quantity is 0. Enter what you counted.</p>
            <div className="mt-3">
              <label className="mb-1 block text-sm font-medium text-gray-700">Part</label>
              <PartSearchSelector parts={partsNotInStocktake} value={newPartId} onChange={setNewPartId} />
            </div>
            <div className="mt-3">
              <label className="mb-1 block text-sm font-medium text-gray-700">Quantity counted</label>
              <input
                type="text"
                inputMode="decimal"
                value={newPartQty}
                onChange={(e) => setNewPartQty(e.target.value)}
                placeholder="e.g. 3"
                className="h-11 w-full rounded-md border border-gray-300 px-3 text-lg focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="mt-4 flex gap-2">
              <button onClick={() => setShowAddPart(false)} className="flex-1 rounded-md border border-gray-300 py-2.5 font-medium text-gray-700">Cancel</button>
              <button
                onClick={submitNewPart}
                disabled={!newPartId || addingPart}
                className="flex-1 rounded-md bg-blue-600 py-2.5 font-semibold text-white disabled:opacity-40"
              >{addingPart ? 'Adding…' : 'Add'}</button>
            </div>
          </div>
        </div>
      )}

      {/* Approve confirmation */}
      {showApprove && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4" onClick={() => setShowApprove(false)}>
          <div className="w-full max-w-md rounded-2xl bg-white p-5" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-bold text-gray-900">Approve stocktake</h3>
            <p className="mt-1 text-sm text-gray-600">
              {counted} parts counted, {discrepancyCount} with a discrepancy.
            </p>
            <label className="mt-3 flex items-start gap-2 text-sm text-gray-700">
              <input type="checkbox" checked={applyAdjustments} onChange={(e) => setApplyAdjustments(e.target.checked)} className="mt-0.5" />
              <span>Reset warehouse inventory to the counted quantities (creates adjustment records for every difference).</span>
            </label>
            <div className="mt-4 flex gap-2">
              <button onClick={() => setShowApprove(false)} className="flex-1 rounded-md border border-gray-300 py-2.5 font-medium text-gray-700">Cancel</button>
              <button onClick={approve} disabled={busy} className="flex-1 rounded-md bg-green-600 py-2.5 font-semibold text-white disabled:opacity-50">
                {busy ? 'Approving…' : 'Approve'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StocktakeCount;

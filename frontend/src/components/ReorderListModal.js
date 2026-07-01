// frontend/src/components/ReorderListModal.js
// Reorder list modal — shows all under-stocked parts with deficit quantities
// and provides PDF and Excel export.

import React, { useState, useEffect, useCallback } from 'react';
import { inventoryService } from '../services/inventoryService';
import { useAuth } from '../AuthContext';

// ── helpers ───────────────────────────────────────────────────────────────────

const fmt = (n) => parseFloat(n || 0).toLocaleString(undefined, { maximumFractionDigits: 3 });

function buildReorderRows(aggregatedInventory, filter) {
  // filter: 'critical' = zero stock only, 'low' = below min (incl. zero), 'all' = both
  return aggregatedInventory
    .map((item) => {
      const current = parseFloat(item.total_stock || 0);
      // API returns 'total_minimum_stock' from the aggregation endpoint
      const minimum = parseFloat(item.total_minimum_stock || item.min_stock_recommendation || 0);
      const deficit = Math.max(0, minimum - current);
      const isCritical = current === 0 && minimum > 0; // only critical if there's an actual minimum to meet
      const isLow = current > 0 && minimum > 0 && current <= minimum;
      return {
        part_number: item.part_number || '',
        part_name: item.part_name || 'Unknown Part',
        current_stock: current,
        minimum_stock: minimum,
        deficit,
        unit: item.unit_of_measure || '',
        status: isCritical ? 'critical' : isLow ? 'low' : 'ok',
        warehouse_count: item.warehouse_count || 0,
      };
    })
    .filter((row) => {
      if (filter === 'critical') return row.status === 'critical';
      if (filter === 'low') return row.status === 'low';
      return row.status === 'critical' || row.status === 'low'; // 'all'
    })
    .sort((a, b) => {
      // Critical first, then by deficit descending
      if (a.status !== b.status) return a.status === 'critical' ? -1 : 1;
      return b.deficit - a.deficit;
    });
}

// ── PDF export ────────────────────────────────────────────────────────────────

async function exportToPDF(rows, title) {
  const { default: jsPDF } = await import('jspdf');
  const { default: autoTable } = await import('jspdf-autotable');

  const doc = new jsPDF({ orientation: 'landscape' });

  doc.setFontSize(16);
  doc.text(title, 14, 18);
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 26);

  autoTable(doc, {
    startY: 32,
    head: [['Part Number', 'Part Name', 'Current Stock', 'Min Stock', 'Deficit (to order)', 'Unit', 'Status']],
    body: rows.map((r) => [
      r.part_number,
      r.part_name,
      fmt(r.current_stock),
      fmt(r.minimum_stock),
      fmt(r.deficit),
      r.unit,
      r.status === 'critical' ? 'OUT OF STOCK' : 'LOW STOCK',
    ]),
    styles: { fontSize: 9 },
    headStyles: { fillColor: [37, 99, 235] },
    bodyStyles: { textColor: [50, 50, 50] },
    alternateRowStyles: { fillColor: [245, 247, 250] },
    didParseCell(data) {
      if (data.section === 'body' && data.column.index === 6) {
        const val = data.cell.raw;
        data.cell.styles.textColor = val === 'OUT OF STOCK' ? [220, 38, 38] : [217, 119, 6];
        data.cell.styles.fontStyle = 'bold';
      }
    },
  });

  const safeTitle = title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
  doc.save(`${safeTitle}_${new Date().toISOString().slice(0, 10)}.pdf`);
}

// ── Excel export ──────────────────────────────────────────────────────────────

async function exportToExcel(rows, title) {
  const XLSX = await import('xlsx');

  const wsData = [
    ['Part Number', 'Part Name', 'Current Stock', 'Min Stock', 'Deficit (to order)', 'Unit', 'Status'],
    ...rows.map((r) => [
      r.part_number,
      r.part_name,
      parseFloat(r.current_stock),
      parseFloat(r.minimum_stock),
      parseFloat(r.deficit),
      r.unit,
      r.status === 'critical' ? 'OUT OF STOCK' : 'LOW STOCK',
    ]),
  ];

  const ws = XLSX.utils.aoa_to_sheet(wsData);

  // Column widths
  ws['!cols'] = [
    { wch: 16 }, { wch: 36 }, { wch: 16 }, { wch: 14 }, { wch: 20 }, { wch: 10 }, { wch: 14 },
  ];

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Reorder List');

  const safeTitle = title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
  XLSX.writeFile(wb, `${safeTitle}_${new Date().toISOString().slice(0, 10)}.xlsx`);
}

// ── component ─────────────────────────────────────────────────────────────────

const ReorderListModal = ({ isOpen, onClose, initialFilter = 'all' }) => {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState(initialFilter);
  const [exporting, setExporting] = useState(null); // 'pdf' | 'excel' | null
  const [warehouses, setWarehouses] = useState([]);
  const [selectedWarehouseId, setSelectedWarehouseId] = useState('');

  const orgId = user?.organization_id || user?.organization?.id;

  // Load warehouses for this organization on open
  useEffect(() => {
    if (!isOpen || !orgId) return;
    const token = localStorage.getItem('authToken');
    const apiBase = process.env.REACT_APP_API_BASE_URL ||
      (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/api');
    fetch(`${apiBase}/warehouses/?organization_id=${orgId}&limit=100`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        const list = Array.isArray(data) ? data : (data?.items || data?.warehouses || []);
        setWarehouses(list);
        if (list.length > 0 && !selectedWarehouseId) {
          setSelectedWarehouseId(list[0].id);
        }
      })
      .catch(() => setWarehouses([]));
  }, [isOpen, orgId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchData = useCallback(async () => {
    if (!selectedWarehouseId) return;
    setLoading(true);
    setError('');
    try {
      // Use per-warehouse inventory — accurate stock + minimum per warehouse
      const data = await inventoryService.getWarehouseInventory(selectedWarehouseId);
      const items = Array.isArray(data) ? data : [];
      // Map warehouse inventory rows to the same shape buildReorderRows expects
      const mapped = items.map(item => ({
        part_id: item.part_id,
        part_number: item.part_number || '',
        part_name: item.part_name || item.part?.name || '',
        unit_of_measure: item.unit_of_measure || '',
        total_stock: parseFloat(item.current_stock || 0),
        total_minimum_stock: parseFloat(item.minimum_stock_recommendation || 0),
        warehouse_count: 1,
      }));
      setRows(buildReorderRows(mapped, filter));
    } catch (err) {
      setError('Failed to load inventory data: ' + (err.message || err));
    } finally {
      setLoading(false);
    }
  }, [selectedWarehouseId, filter]);

  useEffect(() => {
    if (isOpen && selectedWarehouseId) fetchData();
  }, [isOpen, fetchData, selectedWarehouseId]);

  const warehouseName = warehouses.find(w => w.id === selectedWarehouseId)?.name || '';
  const title =
    filter === 'critical' ? `Critical Stock — ${warehouseName}`
      : filter === 'low' ? `Low Stock — ${warehouseName}`
        : `Reorder List — ${warehouseName}`;

  const handleExportPDF = async () => {
    setExporting('pdf');
    try { await exportToPDF(rows, title); }
    catch (e) { alert('PDF export failed: ' + e.message); }
    finally { setExporting(null); }
  };

  const handleExportExcel = async () => {
    setExporting('excel');
    try { await exportToExcel(rows, title); }
    catch (e) { alert('Excel export failed: ' + e.message); }
    finally { setExporting(null); }
  };

  if (!isOpen) return null;

  const criticalCount = rows.filter((r) => r.status === 'critical').length;
  const lowCount = rows.filter((r) => r.status === 'low').length;
  const totalDeficit = rows.reduce((s, r) => s + r.deficit, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{title}</h2>
            <p className="text-sm text-gray-500 mt-0.5">
              {rows.length} part{rows.length !== 1 ? 's' : ''} to reorder
              {totalDeficit > 0 && ` · total deficit: ${fmt(totalDeficit)} units`}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1 rounded-lg hover:bg-gray-100">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Warehouse selector + filter tabs + export buttons */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-3 border-b border-gray-100 bg-gray-50">
          <div className="flex flex-wrap items-center gap-3">
            {/* Warehouse selector */}
            {warehouses.length > 1 && (
              <select
                value={selectedWarehouseId}
                onChange={e => setSelectedWarehouseId(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {warehouses.map(w => (
                  <option key={w.id} value={w.id}>{w.name}</option>
                ))}
              </select>
            )}
            {warehouses.length === 1 && (
              <span className="text-sm font-medium text-gray-700">{warehouses[0]?.name}</span>
            )}

            {/* Filter tabs */}
            <div className="flex space-x-1">
              {[
                { key: 'all', label: 'All under-stocked' },
                { key: 'critical', label: `Out of stock (${rows.filter(r => r.status === 'critical').length})` },
                { key: 'low', label: `Low stock (${rows.filter(r => r.status === 'low').length})` },
              ].map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setFilter(key)}
                  className={`px-3 py-1.5 text-sm rounded-lg font-medium transition-colors ${
                    filter === key
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={handleExportExcel}
              disabled={!!exporting || rows.length === 0}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exporting === 'excel' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              )}
              <span>Excel</span>
            </button>

            <button
              onClick={handleExportPDF}
              disabled={!!exporting || rows.length === 0}
              className="flex items-center space-x-1.5 px-3 py-1.5 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exporting === 'pdf' ? (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              )}
              <span>PDF</span>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading && (
            <div className="flex items-center justify-center py-16 text-gray-400">
              <svg className="w-6 h-6 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Loading inventory…
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          {!loading && !error && rows.length === 0 && (
            <div className="text-center py-16">
              <svg className="w-12 h-12 text-green-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-600 font-medium">All parts are sufficiently stocked</p>
              <p className="text-gray-400 text-sm mt-1">No parts need to be ordered right now.</p>
            </div>
          )}

          {!loading && !error && rows.length > 0 && (
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                  <th className="pb-3 pr-4">Part</th>
                  <th className="pb-3 pr-4 text-right">Current</th>
                  <th className="pb-3 pr-4 text-right">Minimum</th>
                  <th className="pb-3 pr-4 text-right font-bold text-gray-700">To Order</th>
                  <th className="pb-3 pr-4">Unit</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rows.map((row, i) => (
                  <tr key={i} className={`hover:bg-gray-50 ${row.status === 'critical' ? 'bg-red-50/40' : ''}`}>
                    <td className="py-3 pr-4">
                      <div className="font-medium text-gray-900">{row.part_name}</div>
                      {row.part_number && (
                        <div className="text-xs text-gray-400 font-mono">{row.part_number}</div>
                      )}
                    </td>
                    <td className={`py-3 pr-4 text-right font-mono ${row.status === 'critical' ? 'text-red-600 font-bold' : 'text-gray-700'}`}>
                      {fmt(row.current_stock)}
                    </td>
                    <td className="py-3 pr-4 text-right font-mono text-gray-600">
                      {fmt(row.minimum_stock)}
                    </td>
                    <td className="py-3 pr-4 text-right">
                      <span className={`font-bold font-mono text-base ${row.status === 'critical' ? 'text-red-700' : 'text-orange-600'}`}>
                        {fmt(row.deficit)}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-gray-500">{row.unit}</td>
                    <td className="py-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        row.status === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {row.status === 'critical' ? 'Out of stock' : 'Low stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-100 flex justify-between items-center text-sm text-gray-500">
          <span>
            {rows.length} part{rows.length !== 1 ? 's' : ''} listed
            {totalDeficit > 0 && ` · total units to order: ${fmt(totalDeficit)}`}
          </span>
          <button onClick={onClose} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReorderListModal;

// frontend/src/utils/printStocktake.js
//
// Opens a clean, printable stocktake sheet in a new window and triggers print.
// Columns: Code | Part name | Expected | Actual | Difference.
// Uncounted rows print with a blank Actual cell, so the same sheet doubles as a
// blank worksheet to fill in by hand.

const fmtNum = (v) => {
  if (v === null || v === undefined || v === '') return '';
  const n = Number(v);
  if (Number.isNaN(n)) return '';
  // trim trailing zeros: 3.000 -> "3", 2.500 -> "2.5"
  return n.toFixed(3).replace(/\.?0+$/, '');
};

const esc = (s) =>
  String(s ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));

export function printStocktake(stocktake = {}, items = [], { sortBy = 'code' } = {}) {
  const rows = [...items].sort((a, b) =>
    sortBy === 'name'
      ? (a.part_name || '').localeCompare(b.part_name || '', undefined, { sensitivity: 'base' })
      : (a.part_number || '').localeCompare(b.part_number || '', undefined, { numeric: true, sensitivity: 'base' })
  );

  const counted = rows.filter((i) => i.actual_quantity !== null && i.actual_quantity !== undefined).length;
  const printedAt = new Date().toLocaleString();

  const bodyRows = rows.map((it, idx) => {
    const expected = fmtNum(it.expected_quantity);
    const hasActual = it.actual_quantity !== null && it.actual_quantity !== undefined;
    const actual = hasActual ? fmtNum(it.actual_quantity) : '';
    let diff = '';
    if (hasActual) {
      const d = Number(it.actual_quantity) - Number(it.expected_quantity || 0);
      diff = (d > 0 ? '+' : '') + fmtNum(d);
    }
    const unexpected = Number(it.expected_quantity || 0) === 0;
    return `<tr>
      <td class="num">${idx + 1}</td>
      <td>${esc(it.part_number)}${unexpected ? ' <span class="tag">NEW</span>' : ''}</td>
      <td>${esc(it.part_name)}</td>
      <td class="num">${expected}</td>
      <td class="num actual">${actual}</td>
      <td class="num">${diff}</td>
    </tr>`;
  }).join('');

  const html = `<!doctype html><html><head><meta charset="utf-8">
<title>Stocktake - ${esc(stocktake.warehouse_name || '')}</title>
<style id="print-style">
  @page { size: A4; margin: 14mm; }
  * { box-sizing: border-box; }
  body { font: 12px -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #111; }
  h1 { font-size: 16px; margin: 0 0 6px; }
  .meta { margin: 0 0 12px; color: #333; line-height: 1.5; }
  .meta b { color: #000; }
  table { width: 100%; border-collapse: collapse; }
  th, td { border: 1px solid #999; padding: 4px 6px; text-align: left; vertical-align: top; }
  th { background: #eee; font-weight: 600; }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  td.actual { min-width: 60px; }
  .tag { font-size: 9px; border: 1px solid #999; border-radius: 3px; padding: 0 3px; color: #555; }
  tr { page-break-inside: avoid; }
  thead { display: table-header-group; }
  .sig { margin-top: 32px; display: flex; gap: 48px; }
  .sig div { flex: 1; border-top: 1px solid #333; padding-top: 4px; font-size: 11px; color: #333; }
  @media screen { body { max-width: 800px; margin: 24px auto; padding: 0 16px; } }
</style></head><body>
  <h1>Physical inventory count</h1>
  <div class="meta">
    Warehouse: <b>${esc(stocktake.warehouse_name || '-')}</b>${stocktake.organization_name ? ` &mdash; ${esc(stocktake.organization_name)}` : ''}<br>
    ${stocktake.scheduled_date ? `Scheduled: ${esc(new Date(stocktake.scheduled_date).toLocaleString())} &nbsp;&middot;&nbsp; ` : ''}Printed: ${esc(printedAt)}<br>
    Status: ${esc((stocktake.status || '').replace('_', ' ') || '-')} &nbsp;&middot;&nbsp; Parts: ${rows.length} &nbsp;&middot;&nbsp; Counted: ${counted}
  </div>
  <table>
    <thead><tr>
      <th class="num">#</th><th>Code</th><th>Part name</th>
      <th class="num">Expected</th><th class="num">Actual</th><th class="num">Difference</th>
    </tr></thead>
    <tbody>${bodyRows || '<tr><td colspan="6">No parts on this stocktake.</td></tr>'}</tbody>
  </table>
  <div class="sig"><div>Counted by &nbsp;/&nbsp; date</div><div>Approved by &nbsp;/&nbsp; date</div></div>
</body></html>`;

  // Print via a hidden same-origin iframe - no pop-up, no blocker issues.
  const prev = document.getElementById('__stocktake_print_frame');
  if (prev) prev.remove();

  const frame = document.createElement('iframe');
  frame.id = '__stocktake_print_frame';
  frame.setAttribute('aria-hidden', 'true');
  frame.style.cssText = 'position:fixed;right:0;bottom:0;width:0;height:0;border:0;visibility:hidden;';
  document.body.appendChild(frame);

  let printed = false;
  const doPrint = () => {
    if (printed) return;
    printed = true;
    try {
      frame.contentWindow.focus();
      frame.contentWindow.print();
    } catch (e) {
      // Fallback: open in a new tab if the iframe print is blocked for any reason
      const w = window.open('', '_blank');
      if (w) { w.document.write(html); w.document.close(); w.focus(); w.print(); }
    }
    setTimeout(() => frame.remove(), 1000);
  };

  frame.onload = doPrint;
  const doc = frame.contentWindow.document;
  doc.open();
  doc.write(html);
  doc.close();
  // Fallback in case onload doesn't fire for a written document
  setTimeout(doPrint, 400);
}

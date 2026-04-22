// ============================================================
//  SC Appraisal · MLS/CAMA Review Portal — Shared Status API
//  Paste this entire file into your Google Apps Script editor
//  then click Deploy → Manage Deployments → create new version
// ============================================================

const SHEET_NAME = "ReviewStatuses";
const HEADERS    = ["WeekKey","ParcelID","Status","Reviewer","UpdatedAt","Note","Address","Zone"];

// ── Zone → Support Staff routing ─────────────────────────────
const ZONE_SUPPORT = {
  "canton":    { name: "Stephanie M. Moore", email: "smmoore@starkcountyohio.gov" },
  "southern":  { name: "Stephanie M. Moore", email: "smmoore@starkcountyohio.gov" },
  "northwest": { name: "Stephanie M. Moore", email: "smmoore@starkcountyohio.gov" },
  "western":   { name: "Jill S. Flounders",  email: "jsflounders@starkcountyohio.gov" },
  "northeast": { name: "Jill S. Flounders",  email: "jsflounders@starkcountyohio.gov" },
  "northern":  { name: "Jill S. Flounders",  email: "jsflounders@starkcountyohio.gov" },
};

// ── GET ───────────────────────────────────────────────────────
function doGet(e) {
  try {
    const weekKey  = e.parameter.weekKey;
    const allWeeks = e.parameter.allWeeks === "true";
    const sheet    = getOrCreateSheet();
    const data     = sheetToObject(sheet);

    if (allWeeks) {
      const summary = {};
      for (const [wk, parcels] of Object.entries(data)) {
        const vals = Object.values(parcels).map(p => p.status);
        summary[wk] = {
          reviewed:   vals.filter(v => v === "Reviewed").length,
          fieldVisit: vals.filter(v => v === "Field Visit").length,
          total:      vals.filter(Boolean).length,
        };
      }
      return jsonResponse({ weeks: summary });
    }

    if (!weekKey) return jsonResponse({ error: "weekKey or allWeeks=true required" });

    const weekData = data[weekKey] || {};
    const statuses = {};
    const notes    = {};
    for (const [pid, info] of Object.entries(weekData)) {
      if (info.status) statuses[pid] = info.status;
      if (info.note)   notes[pid]    = info.note;
    }
    return jsonResponse({ weekKey, statuses, notes });

  } catch(err) {
    return jsonResponse({ error: err.message });
  }
}

// ── POST ──────────────────────────────────────────────────────
function doPost(e) {
  try {
    const body   = JSON.parse(e.postData.contents);
    const action = body.action || "setStatus";

    if (action === "notify") return handleNotify(body);

    const { weekKey, parcelId, status, reviewer="Unknown",
            note="", address="", zone="" } = body;

    if (!weekKey || !parcelId) return jsonResponse({ error: "weekKey and parcelId required" });

    const sheet = getOrCreateSheet();
    upsertRow(sheet, weekKey, parcelId, status, reviewer, note, address, zone);
    return jsonResponse({ ok: true, weekKey, parcelId, status });

  } catch(err) {
    return jsonResponse({ error: err.message });
  }
}

// ── Send field visit emails grouped by zone ───────────────────
function handleNotify(body) {
  const { weekKey, weekLabel = weekKey } = body;
  if (!weekKey) return jsonResponse({ error: "weekKey required" });

  const sheet   = getOrCreateSheet();
  const data    = sheetToObject(sheet);
  const parcels = data[weekKey] || {};

  const fieldVisits = Object.entries(parcels)
    .filter(([, info]) => info.status === "Field Visit")
    .map(([pid, info]) => ({
      parcelId: pid,
      address:  info.address  || "(no address)",
      zone:     info.zone     || "",
      note:     info.note     || "(no reason given)",
      reviewer: info.reviewer || "Unknown",
    }));

  if (fieldVisits.length === 0) {
    return jsonResponse({ ok: true, sent: 0, message: "No Field Visit parcels found" });
  }

  // Group by support staff
  const grouped  = {};
  const unrouted = [];

  for (const p of fieldVisits) {
    const support = ZONE_SUPPORT[p.zone.toLowerCase().trim()];
    if (support) {
      if (!grouped[support.email]) grouped[support.email] = { support, zones: {} };
      if (!grouped[support.email].zones[p.zone]) grouped[support.email].zones[p.zone] = [];
      grouped[support.email].zones[p.zone].push(p);
    } else {
      unrouted.push(p);
    }
  }

  let sent = 0;
  for (const [email, info] of Object.entries(grouped)) {
    const count = Object.values(info.zones).reduce((s, a) => s + a.length, 0);
    MailApp.sendEmail({
      to:       email,
      subject:  `Field Visit Requests — ${weekLabel} (${count} parcel${count !== 1 ? "s" : ""})`,
      htmlBody: buildEmailHtml(info.support.name, weekLabel, info.zones),
    });
    sent++;
  }

  if (unrouted.length > 0) {
    const both = [...new Set(Object.values(ZONE_SUPPORT).map(s => s.email))].join(",");
    MailApp.sendEmail({
      to:       both,
      subject:  `⚠ Field Visit Requests (unknown zone) — ${weekLabel}`,
      htmlBody: buildEmailHtml("Support Staff", weekLabel, { "Unknown Zone": unrouted }, true),
    });
  }

  return jsonResponse({ ok: true, sent, total: fieldVisits.length });
}

// ── Email HTML ────────────────────────────────────────────────
function buildEmailHtml(recipientName, weekLabel, zoneGroups, hasUnknown) {
  const firstName    = recipientName.split(" ")[0];
  const totalParcels = Object.values(zoneGroups).reduce((s, a) => s + a.length, 0);

  const zonesHtml = Object.entries(zoneGroups).map(([zone, parcels]) => {
    const rows = parcels.map(p => `
      <tr>
        <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-family:monospace;font-size:13px;white-space:nowrap;">${p.parcelId}</td>
        <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:13px;">${p.address}</td>
        <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:13px;">${p.note}</td>
        <td style="padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:12px;color:#64748b;">${p.reviewer}</td>
      </tr>`).join("");
    return `
      <div style="margin-bottom:28px;">
        <div style="background:#1e3a8a;color:#fff;padding:8px 14px;border-radius:6px 6px 0 0;font-size:12px;font-weight:700;letter-spacing:0.06em;font-family:monospace;">
          ${zone.toUpperCase()} &mdash; ${parcels.length} PARCEL${parcels.length !== 1 ? "S" : ""}
        </div>
        <table style="width:100%;border-collapse:collapse;border:1px solid #e2e8f0;border-top:none;">
          <thead><tr style="background:#f8fafc;">
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#64748b;font-family:monospace;border-bottom:1px solid #e2e8f0;">PARCEL ID</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#64748b;font-family:monospace;border-bottom:1px solid #e2e8f0;">ADDRESS</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#64748b;font-family:monospace;border-bottom:1px solid #e2e8f0;">REASON</th>
            <th style="padding:8px 14px;text-align:left;font-size:11px;color:#64748b;font-family:monospace;border-bottom:1px solid #e2e8f0;">REVIEWER</th>
          </tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }).join("");

  return `<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:700px;margin:32px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">
    <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);padding:28px 32px;">
      <div style="font-size:11px;letter-spacing:0.15em;color:#7dd3fc;font-family:monospace;margin-bottom:8px;">STARK COUNTY AUDITOR&rsquo;S OFFICE &middot; PROPERTY ASSESSMENT</div>
      <div style="font-size:22px;font-weight:700;color:#f8fafc;margin-bottom:4px;">Field Visit Requests</div>
      <div style="font-size:13px;color:#94a3b8;">${weekLabel}</div>
    </div>
    <div style="padding:28px 32px;">
      <p style="font-size:14px;color:#374151;margin:0 0 24px 0;">
        ${firstName}, the following parcel${totalParcels !== 1 ? "s have" : " has"} been flagged for field visits
        during the portal review of <strong>${weekLabel}</strong>.
        Please create field visit workflows before Tuesday&rsquo;s inquiry.
      </p>
      ${zonesHtml}
      <div style="padding:14px 18px;background:#f0fdf4;border:1px solid #86efac;border-radius:8px;font-size:13px;color:#166534;">
        <strong>${totalParcels} parcel${totalParcels !== 1 ? "s" : ""}</strong> flagged for field visits this week.
        ${hasUnknown ? "<br><strong style='color:#b45309;'>&#9888; Zone unknown &mdash; please assign manually.</strong>" : ""}
      </div>
    </div>
    <div style="padding:14px 32px;background:#f8fafc;border-top:1px solid #e2e8f0;">
      <div style="font-size:11px;color:#94a3b8;font-family:monospace;">MLS/CAMA Review Portal &middot; Stark County Auditor&rsquo;s Office &middot; Auto-generated</div>
    </div>
  </div>
</body></html>`;
}

// ── Sheet helpers ─────────────────────────────────────────────

function getOrCreateSheet() {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let   sheet = ss.getSheetByName(SHEET_NAME);

  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    styleHeader(sheet);
    sheet.setColumnWidths(1, HEADERS.length, 155);
    return sheet;
  }

  // Migrate: add any missing header columns to existing sheet
  const lastCol         = sheet.getLastColumn();
  const existingHeaders = lastCol > 0 ? sheet.getRange(1,1,1,lastCol).getValues()[0] : [];
  let   migrated        = false;
  for (let i = 0; i < HEADERS.length; i++) {
    if (!existingHeaders[i]) { sheet.getRange(1, i+1).setValue(HEADERS[i]); migrated = true; }
  }
  if (migrated) styleHeader(sheet);
  return sheet;
}

function styleHeader(sheet) {
  const hdr = sheet.getRange(1, 1, 1, HEADERS.length);
  hdr.setFontWeight("bold");
  hdr.setBackground("#1e3a8a");
  hdr.setFontColor("#ffffff");
}

function sheetToObject(sheet) {
  const rows = sheet.getDataRange().getValues();
  const out  = {};
  for (let i = 1; i < rows.length; i++) {
    const [weekKey, parcelId, status, reviewer, , note, address, zone] = rows[i];
    if (!weekKey || !parcelId) continue;
    if (!out[weekKey]) out[weekKey] = {};
    out[weekKey][String(parcelId)] = {
      status:   String(status   || ""),
      reviewer: String(reviewer || ""),
      note:     String(note     || ""),
      address:  String(address  || ""),
      zone:     String(zone     || ""),
    };
  }
  return out;
}

function upsertRow(sheet, weekKey, parcelId, status, reviewer, note, address, zone) {
  const rows = sheet.getDataRange().getValues();
  const now  = new Date().toLocaleString("en-US", { timeZone: "America/New_York" });

  for (let i = 1; i < rows.length; i++) {
    if (String(rows[i][0]) === String(weekKey) &&
        String(rows[i][1]) === String(parcelId)) {
      const addr = address || String(rows[i][6] || "");
      const zn   = zone    || String(rows[i][7] || "");
      if (!status) {
        sheet.getRange(i+1, 3, 1, 6).setValues([["", reviewer, now, "", addr, zn]]);
        sheet.getRange(i+1, 1, 1, HEADERS.length).setBackground("#ffffff");
      } else {
        sheet.getRange(i+1, 3, 1, 6).setValues([[status, reviewer, now, note, addr, zn]]);
        colorRow(sheet, i+1, status);
      }
      return;
    }
  }
  sheet.appendRow([weekKey, parcelId, status || "", reviewer, now, note, address, zone]);
  if (status) colorRow(sheet, sheet.getLastRow(), status);
}

function colorRow(sheet, rowNum, status) {
  const colors = { "Reviewed": "#d1fae5", "Field Visit": "#dbeafe" };
  sheet.getRange(rowNum, 1, 1, HEADERS.length).setBackground(colors[status] || "#ffffff");
}

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

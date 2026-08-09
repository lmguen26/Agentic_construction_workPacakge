from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _esc(value: Any) -> str:
    if value is None:
        return "—"
    return html.escape(str(value))


def _cards(items: list[dict[str, Any]], title_key: str, subtitle_keys: list[str]) -> str:
    if not items:
        return '<div class="empty">No records</div>'
    out = []
    for item in items:
        title = _esc(item.get(title_key) or item.get("id") or "Record")
        subs = "".join(f"<div><strong>{html.escape(k)}:</strong> {_esc(item.get(k))}</div>" for k in subtitle_keys)
        out.append(f'<article class="card"><h3>{title}</h3>{subs}</article>')
    return "".join(out)


def _recommended_work_packages(context: dict[str, Any]) -> list[dict[str, Any]]:
    return context.get("recommended_work_packages") or context.get("work_packages") or []


def _work_package_review_cards(context: dict[str, Any]) -> str:
    candidates = _recommended_work_packages(context)
    if not candidates:
        return '<div class="empty">No recommended work packages available for review.</div>'
    out = []
    for wp in candidates:
        wp_id_raw = str(wp.get("work_package_id") or wp.get("id") or "UNKNOWN-WP")
        wp_id = _esc(wp_id_raw)
        title = _esc(wp.get("title") or wp.get("recommendation") or wp_id_raw)
        out.append(f'''
        <article class="review-card" data-work-package-id="{wp_id}">
          <div class="review-card-head"><div><strong>{title}</strong><div class="small">{wp_id}</div></div><span class="status review-state">NOT_REVIEWED</span></div>
          <div class="review-grid">
            <label>Decision
              <select class="wp-decision">
                <option>NOT_REVIEWED</option><option>APPROVE</option><option>APPROVE_WITH_CHANGES</option><option>RETURN_FOR_REVISION</option><option>DEFER</option><option>REJECT</option>
              </select>
            </label>
            <label><input type="checkbox" class="scope-review" /> Scope change requested</label>
            <label><input type="checkbox" class="cost-review" /> Cost review required</label>
            <label><input type="checkbox" class="timing-review" /> Timing review required</label>
            <label><input type="checkbox" class="risk-review" /> Risk review required</label>
            <label><input type="checkbox" class="wp-complete" /> Work package review complete</label>
          </div>
          <label>Reviewer comment<textarea class="wp-comment" rows="3" placeholder="Rationale, requested changes, conditions, unresolved questions..."></textarea></label>
          <div class="small wp-reviewed-at">Not yet reviewed</div>
        </article>''')
    return "".join(out)


def _initial_review_metadata(context: dict[str, Any]) -> dict[str, Any]:
    building_id = context.get("building_id", "UNKNOWN")
    work_packages = _recommended_work_packages(context)
    return {
        "review_schema_version": "0.3",
        "review_id": None,
        "building_id": building_id,
        "pipeline_run_id": context.get("pipeline_run_id"),
        "artifact_version": context.get("artifact_version") or context.get("context_version"),
        "reviewer_id": None,
        "reviewer_name": None,
        "reviewer_role": None,
        "review_started_at": None,
        "review_completed_at": None,
        "review_status": "NOT_STARTED",
        "completion_confirmed": False,
        "overall_comment": None,
        "work_package_reviews": [
            {
                "work_package_id": wp.get("work_package_id") or wp.get("id"),
                "decision": "NOT_REVIEWED",
                "reviewed_at": None,
                "reviewer_comment": None,
                "scope_change_requested": False,
                "cost_review_required": False,
                "timing_review_required": False,
                "risk_review_required": False,
                "completion_confirmed": False,
            }
            for wp in work_packages
        ],
        "audit_events": [],
    }


def render_building_datasheet(context: dict[str, Any], output_path: Path) -> Path:
    b = context.get("building", {})
    derived = context.get("derived_facts", {})
    dq = context.get("data_quality_gate", context.get("data_quality", {}))
    building_id = context.get("building_id", "UNKNOWN")

    payload = json.dumps(context, ensure_ascii=False).replace("</", "<\\/")
    review_payload = json.dumps(_initial_review_metadata(context), ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{_esc(b.get('building_name') or building_id)} - Building Datasheet</title>
<style>
:root {{ font-family: Arial, sans-serif; color: #1f2937; background: #f3f4f6; }} body {{ margin: 0; }}
header {{ background: white; border-bottom: 1px solid #ddd; padding: 22px 28px; position: sticky; top: 0; z-index: 2; }}
h1 {{ margin: 0 0 6px; font-size: 24px; }} .small {{ color: #6b7280; font-size: 13px; }}
main {{ padding: 24px 28px 60px; max-width: 1400px; margin: auto; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.metric, .card, section, .review-card {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; }}
.metric {{ padding: 14px; }} .metric .value {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
section {{ margin-top: 18px; padding: 18px; }} section h2 {{ margin-top: 0; font-size: 18px; }}
.card, .review-card {{ padding: 12px; margin: 8px 0; }} .card h3 {{ margin: 0 0 8px; font-size: 15px; }}
.empty {{ color: #6b7280; font-style: italic; }} .status {{ display: inline-block; padding: 5px 9px; border-radius: 999px; background: #eef2ff; font-size: 12px; font-weight: 700; }}
nav button, .action {{ border: 0; background: #e5e7eb; padding: 8px 10px; margin: 6px 6px 0 0; border-radius: 7px; cursor: pointer; }}
.action.primary {{ background: #111827; color: white; }}
pre {{ white-space: pre-wrap; word-break: break-word; background: #111827; color: #f9fafb; padding: 14px; border-radius: 8px; max-height: 600px; overflow: auto; }}
.hidden {{ display: none; }} .review-panel {{ border: 2px solid #c7d2fe; }}
.review-grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:10px; margin:12px 0; }}
label {{ display:block; font-size:13px; font-weight:600; margin-top:8px; }} input[type=text], select, textarea {{ width:100%; box-sizing:border-box; margin-top:5px; padding:8px; border:1px solid #d1d5db; border-radius:6px; font:inherit; }}
.review-card-head {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }}
.audit {{ max-height:220px; overflow:auto; border:1px solid #e5e7eb; border-radius:8px; padding:10px; background:#f9fafb; }}
.audit div {{ padding:5px 0; border-bottom:1px solid #eee; font-size:12px; }}
.save-note {{ margin-top:8px; padding:9px 10px; border-radius:7px; background:#f0fdf4; font-size:12px; }}
</style>
</head>
<body>
<header>
  <h1>{_esc(b.get('building_name') or building_id)}</h1>
  <div class="small">Building ID: {_esc(building_id)} · {_esc(b.get('municipality'))}, {_esc(b.get('province'))}</div>
  <nav><button onclick="showAll()">All</button><button onclick="filterSections('condition')">Condition</button><button onclick="filterSections('business')">Business</button><button onclick="filterSections('strategy')">Strategy</button><button onclick="filterSections('review')">Human review</button><button onclick="filterSections('raw')">Raw context</button></nav>
</header>
<main>
  <div class="grid">
    <div class="metric"><div>Ownership</div><div class="value">{_esc(b.get('ownership_type'))}</div></div>
    <div class="metric"><div>Gross area</div><div class="value">{_esc(b.get('gross_area_sqft'))} ft²</div></div>
    <div class="metric"><div>Replacement value</div><div class="value">${_esc(derived.get('calculated_replacement_value'))}</div></div>
    <div class="metric"><div>Detention horizon</div><div class="value">{_esc(derived.get('detention_horizon_years'))} years</div></div>
    <div class="metric"><div>Detention band</div><div class="value">{_esc(derived.get('detention_band'))}</div></div>
    <div class="metric"><div>Data quality</div><div class="value"><span class="status">{_esc(dq.get('gate_status') or dq.get('status'))}</span></div></div>
  </div>

  <section data-group="condition"><h2>Deficiencies</h2>{_cards(context.get('deficiencies', []), 'title', ['deficiency_id','uniformat_code','action_type','condition_rating','intervention_horizon','source_total_cost'])}</section>
  <section data-group="condition"><h2>Components</h2>{_cards(context.get('components', []), 'component_name', ['component_id','component_type','uniformat_code','installation_year','condition_rating','replacement_value'])}</section>
  <section data-group="condition"><h2>Accessibility</h2>{_cards(context.get('accessibility', []), 'criterion_description', ['criterion_id','compliance_status','priority','recommended_action'])}</section>
  <section data-group="business"><h2>Service points</h2>{_cards(context.get('service_points', []), 'service_point_name', ['service_point_id','business_entity_type','service_point_status'])}</section>
  <section data-group="business"><h2>Occupancies</h2>{_cards(context.get('occupancies', []), 'occupancy_id', ['service_point_id','occupancy_type','occupancy_status','occupied_area_sqft','lease_id'])}</section>
  <section data-group="business"><h2>Leases</h2>{_cards(context.get('leases', []), 'lease_id', ['service_point_id','lease_status','lease_start_date','lease_end_date','leased_area_sqft'])}</section>
  <section data-group="strategy"><h2>Initiatives</h2>{_cards(context.get('initiatives', []), 'initiative_name', ['initiative_id','initiative_type','planned_start_year','planned_completion_year','estimated_cost'])}</section>
  <section data-group="strategy"><h2>Projects</h2>{_cards(context.get('projects', []), 'project_name', ['project_id','project_status','planned_start_date','planned_completion_date','approved_budget','forecast_cost'])}</section>
  <section data-group="strategy"><h2>Strategic context</h2>{_cards(context.get('strategic_context', []), 'structured_summary', ['strategic_context_id','source_type','confidence_level','human_validated'])}</section>
  <section data-group="strategy"><h2>Asset strategy</h2><pre>{_esc(json.dumps(context.get('asset_strategy'), indent=2, ensure_ascii=False))}</pre></section>

  <section data-group="review" class="review-panel">
    <h2>Human-in-the-loop review</h2>
    <div class="grid">
      <label>Reviewer ID<input id="reviewer-id" type="text" placeholder="Required reviewer identifier" /></label>
      <label>Reviewer name<input id="reviewer-name" type="text" /></label>
      <label>Reviewer role<input id="reviewer-role" type="text" /></label>
      <label>Review status<select id="review-status"><option>NOT_STARTED</option><option>IN_PROGRESS</option><option>COMPLETED</option><option>RETURNED_FOR_REVISION</option></select></label>
    </div>
    <div class="small">Review started: <span id="started-at">—</span> · Completed: <span id="completed-at">—</span></div>
    <div class="save-note">Review metadata is embedded in this SPA as JSON and autosaved locally in the browser for this building/artifact.</div>
    <h3>Recommended work packages</h3>
    {_work_package_review_cards(context)}
    <label>Overall review comment<textarea id="overall-comment" rows="4"></textarea></label>
    <label><input id="completion-confirmed" type="checkbox" /> I confirm that the review is complete and that all work-package decisions have been reviewed.</label>
    <div><button class="action" onclick="startReview()">Start / resume review</button><button class="action primary" onclick="completeReview()">Complete review</button><button class="action" onclick="downloadReviewedHtml()">Export reviewed SPA</button><button class="action" onclick="downloadReviewJson()">Export review JSON</button></div>
    <h3>Audit trail</h3><div id="audit" class="audit"></div>
  </section>

  <section data-group="raw"><h2>Canonical site context</h2><pre id="raw"></pre><h2>Embedded review metadata</h2><pre id="review-raw"></pre></section>
</main>
<script type="application/json" id="site-context">{payload}</script>
<script type="application/json" id="review-metadata">{review_payload}</script>
<script>
const ctx = JSON.parse(document.getElementById('site-context').textContent);
const reviewNode = document.getElementById('review-metadata');
let review = JSON.parse(reviewNode.textContent);
const storageKey = `building-review:${{ctx.building_id}}:${{review.artifact_version || 'NA'}}`;

document.getElementById('raw').textContent = JSON.stringify(ctx, null, 2);

function nowIso() {{ return new Date().toISOString(); }}
function actor() {{ return document.getElementById('reviewer-id').value.trim() || 'UNIDENTIFIED'; }}
function syncEmbeddedReview() {{
  reviewNode.textContent = JSON.stringify(review);
  document.getElementById('review-raw').textContent = JSON.stringify(review, null, 2);
  try {{ localStorage.setItem(storageKey, JSON.stringify(review)); }} catch (e) {{}}
}}
function logEvent(type, details={{}}) {{
  review.audit_events.push({{event_type:type,timestamp:nowIso(),actor_id:actor(),details}});
  syncEmbeddedReview();
  renderAudit();
}}
function renderAudit() {{
  document.getElementById('audit').innerHTML = review.audit_events.slice().reverse().map(e=>`<div><strong>${{e.event_type}}</strong> · ${{e.timestamp}} · ${{e.actor_id}}<br>${{JSON.stringify(e.details)}}</div>`).join('') || '<div class="small">No events yet.</div>';
}}
function collectWpReviews() {{
  return [...document.querySelectorAll('.review-card')].map(card=>({{
    work_package_id:card.dataset.workPackageId,
    decision:card.querySelector('.wp-decision').value,
    reviewed_at:card.querySelector('.wp-reviewed-at').dataset.iso || null,
    reviewer_comment:card.querySelector('.wp-comment').value || null,
    scope_change_requested:card.querySelector('.scope-review').checked,
    cost_review_required:card.querySelector('.cost-review').checked,
    timing_review_required:card.querySelector('.timing-review').checked,
    risk_review_required:card.querySelector('.risk-review').checked,
    completion_confirmed:card.querySelector('.wp-complete').checked
  }}));
}}
function captureForm() {{
  review.reviewer_id = document.getElementById('reviewer-id').value.trim() || null;
  review.reviewer_name = document.getElementById('reviewer-name').value || null;
  review.reviewer_role = document.getElementById('reviewer-role').value || null;
  review.review_status = document.getElementById('review-status').value;
  review.completion_confirmed = document.getElementById('completion-confirmed').checked;
  review.overall_comment = document.getElementById('overall-comment').value || null;
  review.work_package_reviews = collectWpReviews();
  syncEmbeddedReview();
}}
function applyReviewToForm() {{
  document.getElementById('reviewer-id').value = review.reviewer_id || '';
  document.getElementById('reviewer-name').value = review.reviewer_name || '';
  document.getElementById('reviewer-role').value = review.reviewer_role || '';
  document.getElementById('review-status').value = review.review_status || 'NOT_STARTED';
  document.getElementById('completion-confirmed').checked = !!review.completion_confirmed;
  document.getElementById('overall-comment').value = review.overall_comment || '';
  document.getElementById('started-at').textContent = review.review_started_at || '—';
  document.getElementById('completed-at').textContent = review.review_completed_at || '—';
  const byId = Object.fromEntries((review.work_package_reviews || []).map(r=>[r.work_package_id,r]));
  document.querySelectorAll('.review-card').forEach(card=>{{
    const r = byId[card.dataset.workPackageId]; if (!r) return;
    card.querySelector('.wp-decision').value = r.decision || 'NOT_REVIEWED';
    card.querySelector('.review-state').textContent = r.decision || 'NOT_REVIEWED';
    card.querySelector('.wp-comment').value = r.reviewer_comment || '';
    card.querySelector('.scope-review').checked = !!r.scope_change_requested;
    card.querySelector('.cost-review').checked = !!r.cost_review_required;
    card.querySelector('.timing-review').checked = !!r.timing_review_required;
    card.querySelector('.risk-review').checked = !!r.risk_review_required;
    card.querySelector('.wp-complete').checked = !!r.completion_confirmed;
    card.querySelector('.wp-reviewed-at').dataset.iso = r.reviewed_at || '';
    card.querySelector('.wp-reviewed-at').textContent = r.reviewed_at ? 'Last changed: '+r.reviewed_at : 'Not yet reviewed';
  }});
  syncEmbeddedReview(); renderAudit();
}}
function startReview() {{
  if (!document.getElementById('reviewer-id').value.trim()) {{ alert('Reviewer ID is required.'); return; }}
  captureForm();
  if (!review.review_id) review.review_id = `REV-${{ctx.building_id}}-${{Date.now()}}`;
  if (!review.review_started_at) review.review_started_at = nowIso();
  review.review_status = 'IN_PROGRESS';
  document.getElementById('review-status').value = 'IN_PROGRESS';
  document.getElementById('started-at').textContent = review.review_started_at;
  logEvent('REVIEW_STARTED_OR_RESUMED');
}}
function completeReview() {{
  captureForm();
  if (!review.reviewer_id) {{ alert('Reviewer ID is required.'); return; }}
  if (!review.work_package_reviews.every(r=>r.decision!=='NOT_REVIEWED' && r.completion_confirmed)) {{ alert('Each work package must have a decision and completion confirmation.'); return; }}
  if (!review.completion_confirmed) {{ alert('Overall completion confirmation is required.'); return; }}
  if (!review.review_id) review.review_id = `REV-${{ctx.building_id}}-${{Date.now()}}`;
  if (!review.review_started_at) review.review_started_at = nowIso();
  review.review_completed_at = nowIso();
  review.review_status = 'COMPLETED';
  document.getElementById('review-status').value = 'COMPLETED';
  document.getElementById('started-at').textContent = review.review_started_at;
  document.getElementById('completed-at').textContent = review.review_completed_at;
  logEvent('REVIEW_COMPLETED',{{work_package_count:review.work_package_reviews.length}});
}}
function downloadReviewJson() {{
  captureForm(); if (!review.reviewer_id) {{ alert('Reviewer ID is required before export.'); return; }}
  logEvent('REVIEW_JSON_EXPORTED');
  const blob=new Blob([JSON.stringify(review,null,2)],{{type:'application/json'}}); const a=document.createElement('a');
  a.href=URL.createObjectURL(blob); a.download=`${{ctx.building_id}}-review.json`; a.click(); URL.revokeObjectURL(a.href);
}}
function downloadReviewedHtml() {{
  captureForm(); if (!review.reviewer_id) {{ alert('Reviewer ID is required before export.'); return; }}
  logEvent('REVIEWED_SPA_EXPORTED');
  syncEmbeddedReview();
  const clone = document.documentElement.cloneNode(true);
  clone.querySelector('#review-metadata').textContent = JSON.stringify(review).replace(/<\\//g,'<\\\\/');
  const blob = new Blob(['<!doctype html>\n'+clone.outerHTML],{{type:'text/html'}}); const a=document.createElement('a');
  a.href=URL.createObjectURL(blob); a.download=`${{ctx.building_id}}-reviewed.html`; a.click(); URL.revokeObjectURL(a.href);
}}
function filterSections(group) {{ document.querySelectorAll('section').forEach(s => s.classList.toggle('hidden', s.dataset.group !== group)); }}
function showAll() {{ document.querySelectorAll('section').forEach(s => s.classList.remove('hidden')); }}

document.querySelectorAll('#reviewer-id,#reviewer-name,#reviewer-role,#review-status,#overall-comment,#completion-confirmed').forEach(el=>el.addEventListener('change',captureForm));
document.querySelectorAll('.wp-decision,.wp-comment,.scope-review,.cost-review,.timing-review,.risk-review,.wp-complete').forEach(el=>el.addEventListener('change',ev=>{{
  const card=ev.target.closest('.review-card'); const ts=nowIso(); card.querySelector('.review-state').textContent=card.querySelector('.wp-decision').value;
  card.querySelector('.wp-reviewed-at').dataset.iso=ts; card.querySelector('.wp-reviewed-at').textContent='Last changed: '+ts;
  captureForm(); logEvent('WORK_PACKAGE_REVIEW_CHANGED',{{work_package_id:card.dataset.workPackageId,decision:card.querySelector('.wp-decision').value}});
}}));

try {{ const saved=localStorage.getItem(storageKey); if(saved) review=JSON.parse(saved); }} catch(e) {{}}
applyReviewToForm();
</script>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")
    return output_path

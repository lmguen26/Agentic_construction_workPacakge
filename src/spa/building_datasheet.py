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


def _work_package_review_cards(context: dict[str, Any]) -> str:
    candidates = context.get("recommended_work_packages") or context.get("work_packages") or []
    if not candidates:
        return '<div class="empty">No recommended work packages available for review.</div>'
    out = []
    for wp in candidates:
        wp_id = _esc(wp.get("work_package_id") or wp.get("id") or "UNKNOWN-WP")
        title = _esc(wp.get("title") or wp.get("recommendation") or wp_id)
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


def render_building_datasheet(context: dict[str, Any], output_path: Path) -> Path:
    b = context.get("building", {})
    derived = context.get("derived_facts", {})
    dq = context.get("data_quality_gate", context.get("data_quality", {}))
    building_id = context.get("building_id", "UNKNOWN")

    payload = json.dumps(context, ensure_ascii=False).replace("</", "<\\/")
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
.hidden {{ display: none; }}
.review-panel {{ border: 2px solid #c7d2fe; }}
.review-grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:10px; margin:12px 0; }}
label {{ display:block; font-size:13px; font-weight:600; margin-top:8px; }} input[type=text], select, textarea {{ width:100%; box-sizing:border-box; margin-top:5px; padding:8px; border:1px solid #d1d5db; border-radius:6px; font:inherit; }}
.review-card-head {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }}
.audit {{ max-height:220px; overflow:auto; border:1px solid #e5e7eb; border-radius:8px; padding:10px; background:#f9fafb; }}
.audit div {{ padding:5px 0; border-bottom:1px solid #eee; font-size:12px; }}
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
    <h3>Recommended work packages</h3>
    {_work_package_review_cards(context)}
    <label>Overall review comment<textarea id="overall-comment" rows="4"></textarea></label>
    <label><input id="completion-confirmed" type="checkbox" /> I confirm that the review is complete and that all work-package decisions have been reviewed.</label>
    <div><button class="action" onclick="startReview()">Start / resume review</button><button class="action primary" onclick="completeReview()">Complete review</button><button class="action" onclick="downloadReview()">Export review JSON</button></div>
    <h3>Audit trail</h3><div id="audit" class="audit"></div>
  </section>

  <section data-group="raw"><h2>Canonical site context</h2><pre id="raw"></pre></section>
</main>
<script type="application/json" id="site-context">{payload}</script>
<script>
const ctx = JSON.parse(document.getElementById('site-context').textContent);
document.getElementById('raw').textContent = JSON.stringify(ctx, null, 2);
let auditEvents = [];
let reviewStartedAt = null;
let reviewCompletedAt = null;
function nowIso() {{ return new Date().toISOString(); }}
function actor() {{ return document.getElementById('reviewer-id').value.trim() || 'UNIDENTIFIED'; }}
function logEvent(type, details={{}}) {{ const e={{event_type:type,timestamp:nowIso(),actor_id:actor(),details}}; auditEvents.push(e); renderAudit(); }}
function renderAudit() {{ document.getElementById('audit').innerHTML = auditEvents.slice().reverse().map(e=>`<div><strong>${{e.event_type}}</strong> · ${{e.timestamp}} · ${{e.actor_id}}<br>${{JSON.stringify(e.details)}}</div>`).join('') || '<div class="small">No events yet.</div>'; }}
function startReview() {{ if (!document.getElementById('reviewer-id').value.trim()) {{ alert('Reviewer ID is required.'); return; }} if (!reviewStartedAt) reviewStartedAt=nowIso(); document.getElementById('started-at').textContent=reviewStartedAt; document.getElementById('review-status').value='IN_PROGRESS'; logEvent('REVIEW_STARTED_OR_RESUMED'); }}
function collectWpReviews() {{ return [...document.querySelectorAll('.review-card')].map(card=>{{ const decision=card.querySelector('.wp-decision').value; const complete=card.querySelector('.wp-complete').checked; return {{work_package_id:card.dataset.workPackageId,decision,reviewed_at:nowIso(),reviewer_comment:card.querySelector('.wp-comment').value||null,scope_change_requested:card.querySelector('.scope-review').checked,cost_review_required:card.querySelector('.cost-review').checked,timing_review_required:card.querySelector('.timing-review').checked,risk_review_required:card.querySelector('.risk-review').checked,completion_confirmed:complete}}; }}); }}
function buildReview() {{ return {{review_id:`REV-${{ctx.building_id}}-${{Date.now()}}`,building_id:ctx.building_id,pipeline_run_id:ctx.pipeline_run_id||null,artifact_version:ctx.artifact_version||ctx.context_version||null,reviewer_id:document.getElementById('reviewer-id').value.trim(),reviewer_name:document.getElementById('reviewer-name').value||null,reviewer_role:document.getElementById('reviewer-role').value||null,review_started_at:reviewStartedAt||nowIso(),review_completed_at:reviewCompletedAt,review_status:document.getElementById('review-status').value,completion_confirmed:document.getElementById('completion-confirmed').checked,overall_comment:document.getElementById('overall-comment').value||null,work_package_reviews:collectWpReviews(),audit_events:auditEvents}}; }}
function completeReview() {{ if (!document.getElementById('reviewer-id').value.trim()) {{ alert('Reviewer ID is required.'); return; }} const reviews=collectWpReviews(); if (!reviews.every(r=>r.decision!=='NOT_REVIEWED' && r.completion_confirmed)) {{ alert('Each work package must have a decision and completion confirmation.'); return; }} if (!document.getElementById('completion-confirmed').checked) {{ alert('Overall completion confirmation is required.'); return; }} if (!reviewStartedAt) reviewStartedAt=nowIso(); reviewCompletedAt=nowIso(); document.getElementById('started-at').textContent=reviewStartedAt; document.getElementById('completed-at').textContent=reviewCompletedAt; document.getElementById('review-status').value='COMPLETED'; logEvent('REVIEW_COMPLETED',{{work_package_count:reviews.length}}); }}
function downloadReview() {{ const review=buildReview(); if (!review.reviewer_id) {{ alert('Reviewer ID is required before export.'); return; }} logEvent('REVIEW_EXPORTED'); const blob=new Blob([JSON.stringify(buildReview(),null,2)],{{type:'application/json'}}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=`${{ctx.building_id}}-review.json`; a.click(); URL.revokeObjectURL(a.href); }}
document.querySelectorAll('.wp-decision,.wp-comment,.scope-review,.cost-review,.timing-review,.risk-review,.wp-complete').forEach(el=>el.addEventListener('change',ev=>{{ const card=ev.target.closest('.review-card'); card.querySelector('.review-state').textContent=card.querySelector('.wp-decision').value; card.querySelector('.wp-reviewed-at').textContent='Last changed: '+nowIso(); logEvent('WORK_PACKAGE_REVIEW_CHANGED',{{work_package_id:card.dataset.workPackageId,decision:card.querySelector('.wp-decision').value}}); }}));
function filterSections(group) {{ document.querySelectorAll('section').forEach(s => s.classList.toggle('hidden', s.dataset.group !== group)); }}
function showAll() {{ document.querySelectorAll('section').forEach(s => s.classList.remove('hidden')); }}
renderAudit();
</script>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")
    return output_path

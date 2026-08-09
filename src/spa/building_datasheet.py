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
:root {{ font-family: Arial, sans-serif; color: #1f2937; background: #f3f4f6; }}
body {{ margin: 0; }}
header {{ background: white; border-bottom: 1px solid #ddd; padding: 22px 28px; position: sticky; top: 0; z-index: 2; }}
h1 {{ margin: 0 0 6px; font-size: 24px; }}
.small {{ color: #6b7280; font-size: 13px; }}
main {{ padding: 24px 28px 60px; max-width: 1400px; margin: auto; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
.metric, .card, section {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; }}
.metric {{ padding: 14px; }}
.metric .value {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
section {{ margin-top: 18px; padding: 18px; }}
section h2 {{ margin-top: 0; font-size: 18px; }}
.card {{ padding: 12px; margin: 8px 0; }}
.card h3 {{ margin: 0 0 8px; font-size: 15px; }}
.empty {{ color: #6b7280; font-style: italic; }}
.status {{ display: inline-block; padding: 5px 9px; border-radius: 999px; background: #eef2ff; font-size: 12px; font-weight: 700; }}
nav button {{ border: 0; background: #e5e7eb; padding: 8px 10px; margin: 6px 6px 0 0; border-radius: 7px; cursor: pointer; }}
pre {{ white-space: pre-wrap; word-break: break-word; background: #111827; color: #f9fafb; padding: 14px; border-radius: 8px; max-height: 600px; overflow: auto; }}
.hidden {{ display: none; }}
</style>
</head>
<body>
<header>
  <h1>{_esc(b.get('building_name') or building_id)}</h1>
  <div class="small">Building ID: {_esc(building_id)} · {_esc(b.get('municipality'))}, {_esc(b.get('province'))}</div>
  <nav>
    <button onclick="showAll()">All</button>
    <button onclick="filterSections('condition')">Condition</button>
    <button onclick="filterSections('business')">Business</button>
    <button onclick="filterSections('strategy')">Strategy</button>
    <button onclick="filterSections('raw')">Raw context</button>
  </nav>
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

  <section data-group="raw"><h2>Canonical site context</h2><pre id="raw"></pre></section>
</main>
<script type="application/json" id="site-context">{payload}</script>
<script>
const ctx = JSON.parse(document.getElementById('site-context').textContent);
document.getElementById('raw').textContent = JSON.stringify(ctx, null, 2);
function filterSections(group) {{
  document.querySelectorAll('section').forEach(s => s.classList.toggle('hidden', s.dataset.group !== group));
}}
function showAll() {{ document.querySelectorAll('section').forEach(s => s.classList.remove('hidden')); }}
</script>
</body>
</html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding="utf-8")
    return output_path

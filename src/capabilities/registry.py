from __future__ import annotations

CAPABILITIES = {
    "data_quality": {"label": "Data quality", "core": True},
    "site_context": {"label": "Canonical site context", "core": True},
    "opportunity_normalization": {"label": "Opportunity normalization (Agent A)", "core": True},
    "bundling_blending": {"label": "Bundling / blending (Agent B)", "core": True},
    "costing": {"label": "Costing (Agent C + deterministic engine)", "core": True},
    "recommendation": {"label": "Strategic recommendation (Agent T)", "core": True},
    "executive_summary": {"label": "Executive summary (Agent E)", "core": True},
    "accessibility": {"label": "Universal accessibility", "core": False},
    "component_lifecycle": {"label": "Component lifecycle", "core": False},
    "lease_strategy": {"label": "Lease / occupancy strategy", "core": False},
    "existing_projects_initiatives": {"label": "Existing projects / initiatives", "core": False},
    "strategic_context": {"label": "Structured strategic context", "core": False},
    "risk_compliance": {"label": "Risk / compliance", "core": False},
    "fci_replacement_value": {"label": "FCI / replacement-value analysis", "core": False},
    "cost_sensitivity": {"label": "Cost sensitivity / uncertainty", "core": False},
    "amortization": {"label": "Amortization / accounting", "core": False},
    "alternative_work_packages": {"label": "Alternative work-package configurations", "core": False},
    "timing_alternatives": {"label": "Timing alternatives", "core": False},
}

EFFORT_LEVELS = {
    "RAPID": "Reduced analytical breadth; prioritize material issues and obvious coordination opportunities.",
    "STANDARD": "Normal site-level processing and review depth.",
    "THOROUGH": "Expanded alternatives, conflicts, uncertainty and review checks for complex/high-value sites.",
}

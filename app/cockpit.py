from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from app.selection_panel import HierarchicalSelectionPanel
from src.capabilities.registry import CAPABILITIES, EFFORT_LEVELS
from src.orchestration.analysis_manifest import build_manifest, load_profile
from src.quality.data_quality_gate import evaluate_site

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "outputs"


class SiteAnalysisCockpit(tk.Toplevel):
    def __init__(self, master: tk.Misc, portfolio: dict, buildings: list[dict]):
        super().__init__(master)
        self.title("Site Analysis Cockpit")
        self.geometry("1120x900")
        self.portfolio = portfolio
        self.buildings = buildings
        self.profile_id = tk.StringVar(value="LEVEL_1_WORK_PACKAGES")
        self.effort = tk.StringVar(value="STANDARD")
        self.requested_by = tk.StringVar()
        self.module_vars = {k: tk.BooleanVar(value=False) for k in CAPABILITIES}
        self._build_ui()
        self._apply_profile()

    def _build_ui(self):
        outer = ttk.Frame(self, padding=14)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Site Investment Analysis Cockpit", font=("TkDefaultFont", 16, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Filter cumulatively by region, branch and site, then optionally refine the final building selection. Each building remains an independent analysis run.",
            foreground="#555555",
        ).pack(anchor="w", pady=(2, 8))

        self.selector = HierarchicalSelectionPanel(outer, self.buildings, on_change=lambda _rows: self._refresh_readiness())
        self.selector.pack(fill="x", pady=(4, 8))

        topgrid = ttk.Frame(outer)
        topgrid.pack(fill="x", pady=8)
        ttk.Label(topgrid, text="Requested by").grid(row=0, column=0, sticky="w")
        ttk.Entry(topgrid, textvariable=self.requested_by, width=24).grid(row=1, column=0, sticky="ew", padx=(0, 10))
        ttk.Label(topgrid, text="Effort").grid(row=0, column=1, sticky="w")
        ttk.Combobox(topgrid, textvariable=self.effort, values=list(EFFORT_LEVELS), state="readonly", width=16).grid(row=1, column=1, sticky="w")

        profiles = ttk.LabelFrame(outer, text="Analysis depth", padding=10)
        profiles.pack(fill="x", pady=6)
        for idx, (value, label) in enumerate([
            ("LEVEL_0_VALIDATION", "Level 0 — Validate only"),
            ("LEVEL_1_WORK_PACKAGES", "Level 1 — Work Package Analysis"),
            ("LEVEL_2_STRATEGIC", "Level 2 — Strategic Site Analysis"),
            ("LEVEL_3_ADVANCED", "Level 3 — Advanced Investment Analysis"),
            ("CUSTOM", "Custom"),
        ]):
            ttk.Radiobutton(profiles, text=label, value=value, variable=self.profile_id, command=self._apply_profile).grid(row=0, column=idx, sticky="w", padx=4)

        modules = ttk.LabelFrame(outer, text="Capabilities / optional modules", padding=10)
        modules.pack(fill="both", expand=True, pady=6)
        for idx, (key, meta) in enumerate(CAPABILITIES.items()):
            row, col = divmod(idx, 2)
            ttk.Checkbutton(modules, text=meta["label"], variable=self.module_vars[key], command=self._module_changed).grid(row=row, column=col, sticky="w", padx=6, pady=3)

        self.readiness = tk.Text(outer, height=10, wrap="word")
        self.readiness.pack(fill="x", pady=8)
        self.readiness.configure(state="disabled")

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        ttk.Button(actions, text="Refresh readiness", command=self._refresh_readiness).pack(side="left")
        ttk.Button(actions, text="Create analysis manifests", command=self._create_manifests).pack(side="right")
        self._refresh_readiness()

    def _selected_buildings(self) -> list[dict]:
        return self.selector.selected_buildings()

    def _apply_profile(self):
        pid = self.profile_id.get()
        if pid == "CUSTOM":
            return
        profile = load_profile(pid)
        for key, var in self.module_vars.items():
            var.set(bool(profile["modules"].get(key, False)))
        self.effort.set(profile.get("default_effort", "STANDARD"))
        self._refresh_readiness()

    def _module_changed(self):
        if self.profile_id.get() != "CUSTOM":
            self.profile_id.set("CUSTOM")

    def _set_readiness(self, payload: str):
        self.readiness.configure(state="normal")
        self.readiness.delete("1.0", "end")
        self.readiness.insert("1.0", payload)
        self.readiness.configure(state="disabled")

    def _refresh_readiness(self):
        selected = self._selected_buildings() if hasattr(self, "selector") else []
        if not selected:
            if hasattr(self, "readiness"):
                self._set_readiness("No buildings in scope.")
            return
        lines = [f"Scope: {len(selected)} building(s)"]
        counts = {"VALIDATED": 0, "REVIEW_REQUIRED": 0, "BLOCKED": 0}
        for b in selected:
            bid = b["building_id"]
            result = evaluate_site(self.portfolio, bid)
            gate = result.get("gate_status", "BLOCKED")
            counts[gate] = counts.get(gate, 0) + 1
            lines.append(f"{bid}: {gate} | region={b.get('region_id')} | branch={b.get('branch_id')} | site={b.get('site_id')}")
        lines.insert(1, f"Validated={counts.get('VALIDATED',0)} · Review required={counts.get('REVIEW_REQUIRED',0)} · Blocked={counts.get('BLOCKED',0)}")
        self._set_readiness("\n".join(lines))

    def _create_manifests(self):
        selected = self._selected_buildings()
        if not selected:
            messagebox.showwarning("No scope", "Select at least one building or higher-level scope.")
            return
        modules = {k: v.get() for k, v in self.module_vars.items()}
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        created, blocked = [], []
        for b in selected:
            bid = b["building_id"]
            quality = evaluate_site(self.portfolio, bid)
            if quality.get("gate_status") == "BLOCKED":
                blocked.append(bid)
                continue
            manifest = build_manifest(
                building_id=bid,
                profile_id=self.profile_id.get(),
                effort=self.effort.get(),
                requested_by=self.requested_by.get().strip() or None,
                module_overrides=modules,
            )
            manifest["selection_scope"] = {
                "region_id": b.get("region_id"),
                "branch_id": b.get("branch_id"),
                "site_id": b.get("site_id"),
            }
            path = OUTPUT_DIR / f"{bid}.analysis_manifest.json"
            path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            created.append(str(path))

        scope = self.selector.current_scope()
        batch_index = {
            "selected_building_ids": [b["building_id"] for b in selected],
            "scope_filters": {
                "regions": list(scope.region_ids),
                "branches": list(scope.branch_ids),
                "sites": list(scope.site_ids),
            },
            "profile_id": self.profile_id.get(),
            "effort": self.effort.get(),
            "created_manifests": created,
            "blocked_buildings": blocked,
        }
        (OUTPUT_DIR / "latest_batch_selection.json").write_text(json.dumps(batch_index, indent=2), encoding="utf-8")
        messagebox.showinfo("Analysis manifests", f"Created {len(created)} manifest(s).\nBlocked: {len(blocked)}")


def open_cockpit(master: tk.Misc, portfolio: dict, buildings: list[dict]):
    SiteAnalysisCockpit(master, portfolio, buildings)

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from src.capabilities.registry import CAPABILITIES, EFFORT_LEVELS
from src.orchestration.analysis_manifest import build_manifest, load_profile
from src.quality.data_quality_gate import evaluate_site

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "examples" / "synthetic_portfolio" / "portfolio.json"
OUTPUT_DIR = ROOT / "data" / "outputs"


class SiteAnalysisCockpit(tk.Toplevel):
    def __init__(self, master: tk.Misc, portfolio: dict, buildings: list[dict]):
        super().__init__(master)
        self.title("Site Analysis Cockpit")
        self.geometry("980x760")
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

        ttk.Label(outer, text="Building").pack(anchor="w", pady=(10, 2))
        choices = [f"{b.get('building_id')} — {b.get('building_name', '')}" for b in self.buildings]
        self.building_combo = ttk.Combobox(outer, values=choices, state="readonly", width=90)
        self.building_combo.pack(fill="x")
        if choices:
            self.building_combo.current(0)
        self.building_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_readiness())

        topgrid = ttk.Frame(outer)
        topgrid.pack(fill="x", pady=10)
        ttk.Label(topgrid, text="Requested by").grid(row=0, column=0, sticky="w")
        ttk.Entry(topgrid, textvariable=self.requested_by, width=24).grid(row=1, column=0, sticky="ew", padx=(0, 10))
        ttk.Label(topgrid, text="Effort").grid(row=0, column=1, sticky="w")
        effort_combo = ttk.Combobox(topgrid, textvariable=self.effort, values=list(EFFORT_LEVELS), state="readonly", width=16)
        effort_combo.grid(row=1, column=1, sticky="w")

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
        self.module_widgets = {}
        for idx, (key, meta) in enumerate(CAPABILITIES.items()):
            row, col = divmod(idx, 2)
            cb = ttk.Checkbutton(modules, text=meta["label"], variable=self.module_vars[key], command=self._module_changed)
            cb.grid(row=row, column=col, sticky="w", padx=6, pady=3)
            self.module_widgets[key] = cb

        self.readiness = tk.Text(outer, height=9, wrap="word")
        self.readiness.pack(fill="x", pady=8)
        self.readiness.configure(state="disabled")

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        ttk.Button(actions, text="Refresh readiness", command=self._refresh_readiness).pack(side="left")
        ttk.Button(actions, text="Create analysis manifest", command=self._create_manifest).pack(side="right")
        self._refresh_readiness()

    def _building_id(self):
        value = self.building_combo.get().strip()
        return value.split(" — ", 1)[0] if value else ""

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

    def _set_readiness(self, payload):
        self.readiness.configure(state="normal")
        self.readiness.delete("1.0", "end")
        self.readiness.insert("1.0", payload)
        self.readiness.configure(state="disabled")

    def _refresh_readiness(self):
        bid = self._building_id()
        if not bid:
            return
        result = evaluate_site(self.portfolio, bid)
        result_map = {r["source"]: r for r in result.get("results", [])}
        lines = [f"Data Quality Gate: {result.get('gate_status')}"]
        for key in ["deficiencies", "components", "accessibility", "leases", "asset_strategy", "strategic_context", "projects", "initiatives"]:
            if key in result_map:
                r = result_map[key]
                lines.append(f"{key}: {r['status']} ({r['severity']}) — {r['reason']}")
        self._set_readiness("\n".join(lines))

    def _create_manifest(self):
        bid = self._building_id()
        if not bid:
            return
        quality = evaluate_site(self.portfolio, bid)
        if quality.get("gate_status") == "BLOCKED":
            messagebox.showwarning("Blocked", "The site is blocked by the Data Quality Gate.")
            return
        modules = {k: v.get() for k, v in self.module_vars.items()}
        manifest = build_manifest(
            building_id=bid,
            profile_id=self.profile_id.get(),
            effort=self.effort.get(),
            requested_by=self.requested_by.get().strip() or None,
            module_overrides=modules,
        )
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"{bid}.analysis_manifest.json"
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        messagebox.showinfo("Analysis manifest", f"Created:\n{path}")


def open_cockpit(master: tk.Misc, portfolio: dict, buildings: list[dict]):
    SiteAnalysisCockpit(master, portfolio, buildings)

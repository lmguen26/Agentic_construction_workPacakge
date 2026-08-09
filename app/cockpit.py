from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

from src.capabilities.registry import CAPABILITIES, EFFORT_LEVELS
from src.orchestration.analysis_manifest import build_manifest, load_profile
from src.quality.data_quality_gate import evaluate_site

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "outputs"


class SiteAnalysisCockpit(tk.Toplevel):
    def __init__(self, master: tk.Misc, portfolio: dict, buildings: list[dict]):
        super().__init__(master)
        self.title("Site Analysis Cockpit")
        self.geometry("1040x820")
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
            text="Select one or multiple buildings. Each selected building keeps its own validation, manifest, outputs, SPA and review history.",
            foreground="#555555",
        ).pack(anchor="w", pady=(2, 8))

        site_frame = ttk.LabelFrame(outer, text="Building scope", padding=8)
        site_frame.pack(fill="x", pady=(4, 8))
        self.building_list = tk.Listbox(site_frame, selectmode=tk.EXTENDED, height=7, exportselection=False)
        self.building_list.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(site_frame, orient="vertical", command=self.building_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.building_list.configure(yscrollcommand=scrollbar.set)
        for b in self.buildings:
            self.building_list.insert("end", f"{b.get('building_id')} — {b.get('building_name', '')}")
        if self.buildings:
            self.building_list.selection_set(0)
        self.building_list.bind("<<ListboxSelect>>", lambda _e: self._refresh_readiness())

        select_row = ttk.Frame(outer)
        select_row.pack(fill="x", pady=(0, 6))
        ttk.Button(select_row, text="Select all", command=self._select_all).pack(side="left")
        ttk.Button(select_row, text="Clear selection", command=self._clear_selection).pack(side="left", padx=(6, 0))
        self.scope_label = ttk.Label(select_row, text="1 building selected")
        self.scope_label.pack(side="right")

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
        self.module_widgets = {}
        for idx, (key, meta) in enumerate(CAPABILITIES.items()):
            row, col = divmod(idx, 2)
            cb = ttk.Checkbutton(modules, text=meta["label"], variable=self.module_vars[key], command=self._module_changed)
            cb.grid(row=row, column=col, sticky="w", padx=6, pady=3)
            self.module_widgets[key] = cb

        self.readiness = tk.Text(outer, height=10, wrap="word")
        self.readiness.pack(fill="x", pady=8)
        self.readiness.configure(state="disabled")

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        ttk.Button(actions, text="Refresh readiness", command=self._refresh_readiness).pack(side="left")
        ttk.Button(actions, text="Create analysis manifest(s)", command=self._create_manifests).pack(side="right")
        self._refresh_readiness()

    def _selected_building_ids(self) -> list[str]:
        ids = []
        for idx in self.building_list.curselection():
            value = self.building_list.get(idx)
            ids.append(value.split(" — ", 1)[0].strip())
        return ids

    def _select_all(self):
        self.building_list.selection_set(0, "end")
        self._refresh_readiness()

    def _clear_selection(self):
        self.building_list.selection_clear(0, "end")
        self._refresh_readiness()

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
        bids = self._selected_building_ids()
        self.scope_label.configure(text=f"{len(bids)} building{'s' if len(bids) != 1 else ''} selected")
        if not bids:
            self._set_readiness("No building selected.")
            return

        lines = []
        for bid in bids:
            result = evaluate_site(self.portfolio, bid)
            result_map = {r["source"]: r for r in result.get("results", [])}
            lines.append(f"{bid}: Data Quality Gate = {result.get('gate_status')}")
            for key in ["deficiencies", "components", "accessibility", "leases", "asset_strategy", "strategic_context", "projects", "initiatives"]:
                if key in result_map and result_map[key]["status"] in {"MISSING", "PARTIAL", "CONFLICT", "STALE"}:
                    r = result_map[key]
                    lines.append(f"  - {key}: {r['status']} ({r['severity']})")
        self._set_readiness("\n".join(lines))

    def _create_manifests(self):
        bids = self._selected_building_ids()
        if not bids:
            messagebox.showwarning("No selection", "Select at least one building.")
            return

        modules = {k: v.get() for k, v in self.module_vars.items()}
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        created = []
        blocked = []

        for bid in bids:
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
            path = OUTPUT_DIR / f"{bid}.analysis_manifest.json"
            path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            created.append(str(path))

        batch_index = {
            "selected_building_ids": bids,
            "profile_id": self.profile_id.get(),
            "effort": self.effort.get(),
            "requested_by": self.requested_by.get().strip() or None,
            "created_manifests": created,
            "blocked_building_ids": blocked,
        }
        batch_path = OUTPUT_DIR / "latest_batch_selection.json"
        batch_path.write_text(json.dumps(batch_index, indent=2, ensure_ascii=False), encoding="utf-8")

        message = f"Created {len(created)} per-building manifest(s)."
        if blocked:
            message += f"\nBlocked and skipped: {', '.join(blocked)}"
        message += f"\nBatch index: {batch_path}"
        messagebox.showinfo("Analysis manifests", message)


def open_cockpit(master: tk.Misc, portfolio: dict, buildings: list[dict]):
    SiteAnalysisCockpit(master, portfolio, buildings)

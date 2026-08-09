from __future__ import annotations

import json
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from app.cockpit import open_cockpit
from app.selection_panel import HierarchicalSelectionPanel
from src.context.site_context_builder import build_site_context
from src.quality.data_quality_gate import evaluate_site
from src.spa.building_datasheet import render_building_datasheet

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "examples" / "synthetic_portfolio" / "portfolio.json"
OUTPUT_DIR = ROOT / "data" / "outputs"


class SiteSelectorApp(tk.Tk):
    def __init__(self, portfolio_path: Path = DEFAULT_PORTFOLIO):
        super().__init__()
        self.title("Asset Investment Planning - Scope Selector")
        self.geometry("1120x820")
        self.portfolio_path = portfolio_path
        self.portfolio = self._load_portfolio()
        self.buildings = self.portfolio.get("buildings", [])
        self.status_var = tk.StringVar(value="Ready")
        self._build_ui()

    def _load_portfolio(self):
        try:
            return json.loads(self.portfolio_path.read_text(encoding="utf-8"))
        except Exception as exc:
            messagebox.showerror("Load error", f"Could not load portfolio:\n{exc}")
            return {}

    def _build_ui(self):
        wrapper = ttk.Frame(self, padding=16)
        wrapper.pack(fill="both", expand=True)

        ttk.Label(wrapper, text="Select analysis scope", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(
            wrapper,
            text="Use cumulative multi-select filters for Region → Branch → Site → Building. Higher-level selections expand to all matching buildings unless the building list is further refined.",
            foreground="#555555",
        ).pack(anchor="w", pady=(2, 8))

        self.selector = HierarchicalSelectionPanel(wrapper, self.buildings, on_change=self._scope_changed)
        self.selector.pack(fill="x", pady=(4, 10))

        button_row = ttk.Frame(wrapper)
        button_row.pack(fill="x", pady=(0, 12))
        ttk.Button(button_row, text="Validate scope", command=self.validate_sites).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Build site context(s)", command=self.build_contexts).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Generate HTML datasheet(s)", command=self.generate_htmls).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Open Analysis Cockpit", command=self.open_analysis_cockpit).pack(side="right")

        ttk.Label(
            wrapper,
            text="Batch scope controls throughput only. Each building keeps its own validation, manifest, site context, SPA, review metadata and revision history.",
            foreground="#555555",
        ).pack(anchor="w", pady=(0, 10))

        self.summary = tk.Text(wrapper, height=24, wrap="word")
        self.summary.pack(fill="both", expand=True)
        self.summary.configure(state="disabled")

        ttk.Label(wrapper, textvariable=self.status_var).pack(anchor="w", pady=(8, 0))
        self._scope_changed(self.selector.selected_buildings())

    def _selected_buildings(self) -> list[dict]:
        return self.selector.selected_buildings()

    def _selected_building_ids(self) -> list[str]:
        return [b["building_id"] for b in self._selected_buildings()]

    def _write_summary(self, payload):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", json.dumps(payload, indent=2, ensure_ascii=False))
        self.summary.configure(state="disabled")

    def _scope_changed(self, selected: list[dict]):
        scope = self.selector.current_scope() if hasattr(self, "selector") else None
        payload = {
            "building_count": len(selected),
            "scope_filters": {
                "regions": list(scope.region_ids) if scope else [],
                "branches": list(scope.branch_ids) if scope else [],
                "sites": list(scope.site_ids) if scope else [],
            },
            "buildings": [
                {
                    "building_id": b.get("building_id"),
                    "building_name": b.get("building_name"),
                    "region_id": b.get("region_id"),
                    "branch_id": b.get("branch_id"),
                    "site_id": b.get("site_id"),
                }
                for b in selected
            ],
        }
        if hasattr(self, "summary"):
            self._write_summary(payload)
            self.status_var.set(f"{len(selected)} building(s) in scope")

    def open_analysis_cockpit(self):
        open_cockpit(self, self.portfolio, self.buildings)

    def validate_sites(self):
        bids = self._selected_building_ids()
        if not bids:
            return
        results = {bid: evaluate_site(self.portfolio, bid) for bid in bids}
        self._write_summary(results)
        blocked = [bid for bid, result in results.items() if result.get("gate_status") == "BLOCKED"]
        self.status_var.set(f"Validated {len(bids)} building(s); {len(blocked)} blocked")

    def build_contexts(self):
        bids = self._selected_building_ids()
        if not bids:
            return
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        created, blocked = [], []
        for bid in bids:
            quality = evaluate_site(self.portfolio, bid)
            if quality.get("gate_status") == "BLOCKED":
                blocked.append(bid)
                continue
            context = build_site_context(self.portfolio, bid)
            context["data_quality_gate"] = quality
            path = OUTPUT_DIR / f"{bid}.site_context.json"
            path.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
            created.append(str(path))
        self._write_summary({"created": created, "blocked": blocked})
        self.status_var.set(f"Created {len(created)} site context(s); {len(blocked)} blocked")

    def generate_htmls(self):
        bids = self._selected_building_ids()
        if not bids:
            return
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        generated, blocked = [], []
        for bid in bids:
            quality = evaluate_site(self.portfolio, bid)
            if quality.get("gate_status") == "BLOCKED":
                blocked.append(bid)
                continue
            context = build_site_context(self.portfolio, bid)
            context["data_quality_gate"] = quality
            context_path = OUTPUT_DIR / f"{bid}.site_context.json"
            context_path.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
            html_path = OUTPUT_DIR / f"{bid}.building_datasheet.html"
            render_building_datasheet(context, html_path)
            generated.append(str(html_path))
            if len(bids) == 1:
                webbrowser.open(html_path.resolve().as_uri())
        self._write_summary({"generated": generated, "blocked": blocked})
        self.status_var.set(f"Generated {len(generated)} datasheet(s); {len(blocked)} blocked")
        if len(generated) > 1:
            messagebox.showinfo("Batch generation", f"Generated {len(generated)} HTML datasheets in:\n{OUTPUT_DIR}")


if __name__ == "__main__":
    SiteSelectorApp().mainloop()

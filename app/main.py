from __future__ import annotations

import json
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from app.cockpit import open_cockpit
from src.context.site_context_builder import build_site_context
from src.quality.data_quality_gate import evaluate_site
from src.spa.building_datasheet import render_building_datasheet

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORTFOLIO = ROOT / "examples" / "synthetic_portfolio" / "portfolio.json"
OUTPUT_DIR = ROOT / "data" / "outputs"


class SiteSelectorApp(tk.Tk):
    def __init__(self, portfolio_path: Path = DEFAULT_PORTFOLIO):
        super().__init__()
        self.title("Asset Investment Planning - Site Selector")
        self.geometry("980x720")
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

        ttk.Label(wrapper, text="Select one or multiple buildings", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        ttk.Label(
            wrapper,
            text="Ctrl/Cmd-click or Shift-click to select multiple sites. Batch actions preserve independent per-building outputs.",
            foreground="#555555",
        ).pack(anchor="w", pady=(2, 8))

        list_frame = ttk.Frame(wrapper)
        list_frame.pack(fill="x")
        self.building_list = tk.Listbox(list_frame, selectmode=tk.EXTENDED, height=8, exportselection=False)
        self.building_list.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.building_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.building_list.configure(yscrollcommand=scrollbar.set)
        for b in self.buildings:
            self.building_list.insert("end", f"{b.get('building_id')} — {b.get('building_name', '')}")
        self.building_list.bind("<<ListboxSelect>>", self._on_select)

        select_row = ttk.Frame(wrapper)
        select_row.pack(fill="x", pady=(6, 10))
        ttk.Button(select_row, text="Select all", command=self._select_all).pack(side="left")
        ttk.Button(select_row, text="Clear selection", command=self._clear_selection).pack(side="left", padx=(6, 0))
        self.selection_label = ttk.Label(select_row, text="0 buildings selected")
        self.selection_label.pack(side="right")

        button_row = ttk.Frame(wrapper)
        button_row.pack(fill="x", pady=(0, 12))
        ttk.Button(button_row, text="Validate selected", command=self.validate_sites).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Build site context(s)", command=self.build_contexts).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Generate HTML datasheet(s)", command=self.generate_htmls).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Open Analysis Cockpit", command=self.open_analysis_cockpit).pack(side="right")

        ttk.Label(
            wrapper,
            text="Use the Analysis Cockpit to choose analysis depth, effort and optional capabilities for the selected building scope.",
            foreground="#555555",
        ).pack(anchor="w", pady=(0, 10))

        self.summary = tk.Text(wrapper, height=24, wrap="word")
        self.summary.pack(fill="both", expand=True)
        self.summary.configure(state="disabled")

        ttk.Label(wrapper, textvariable=self.status_var).pack(anchor="w", pady=(8, 0))

        if self.buildings:
            self.building_list.selection_set(0)
            self._on_select()

    def _selected_building_ids(self) -> list[str]:
        ids = []
        for idx in self.building_list.curselection():
            value = self.building_list.get(idx)
            ids.append(value.split(" — ", 1)[0].strip())
        return ids

    def _select_all(self):
        self.building_list.selection_set(0, "end")
        self._on_select()

    def _clear_selection(self):
        self.building_list.selection_clear(0, "end")
        self._on_select()

    def _write_summary(self, payload):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", json.dumps(payload, indent=2, ensure_ascii=False))
        self.summary.configure(state="disabled")

    def _on_select(self, _event=None):
        bids = self._selected_building_ids()
        self.selection_label.configure(text=f"{len(bids)} building{'s' if len(bids) != 1 else ''} selected")
        selected = [b for b in self.buildings if b.get("building_id") in bids]
        self._write_summary(selected if len(selected) != 1 else selected[0])
        self.status_var.set(f"Selected {len(bids)} building(s)")

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

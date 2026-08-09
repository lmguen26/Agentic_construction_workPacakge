from __future__ import annotations

import json
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

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
        self.geometry("900x620")
        self.portfolio_path = portfolio_path
        self.portfolio = self._load_portfolio()
        self.buildings = self.portfolio.get("buildings", [])
        self.selected_building_id = tk.StringVar()
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

        ttk.Label(wrapper, text="Select building", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")

        choices = [f"{b.get('building_id')} — {b.get('building_name', '')}" for b in self.buildings]
        self.combo = ttk.Combobox(wrapper, values=choices, state="readonly", width=80)
        self.combo.pack(fill="x", pady=(8, 12))
        self.combo.bind("<<ComboboxSelected>>", self._on_select)

        button_row = ttk.Frame(wrapper)
        button_row.pack(fill="x", pady=(0, 12))
        ttk.Button(button_row, text="Validate site", command=self.validate_site).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Build site context", command=self.build_context).pack(side="left", padx=(0, 8))
        ttk.Button(button_row, text="Generate HTML datasheet", command=self.generate_html).pack(side="left")

        self.summary = tk.Text(wrapper, height=24, wrap="word")
        self.summary.pack(fill="both", expand=True)
        self.summary.configure(state="disabled")

        ttk.Label(wrapper, textvariable=self.status_var).pack(anchor="w", pady=(8, 0))

        if choices:
            self.combo.current(0)
            self._on_select()

    def _current_building_id(self) -> str:
        value = self.combo.get().strip()
        return value.split(" — ", 1)[0] if value else ""

    def _write_summary(self, payload):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", json.dumps(payload, indent=2, ensure_ascii=False))
        self.summary.configure(state="disabled")

    def _on_select(self, _event=None):
        bid = self._current_building_id()
        building = next((b for b in self.buildings if b.get("building_id") == bid), {})
        self._write_summary(building)
        self.status_var.set(f"Selected {bid}")

    def validate_site(self):
        bid = self._current_building_id()
        if not bid:
            return
        result = evaluate_site(self.portfolio, bid)
        self._write_summary(result)
        self.status_var.set(f"Data Quality Gate: {result.get('gate_status')}")

    def build_context(self):
        bid = self._current_building_id()
        if not bid:
            return
        quality = evaluate_site(self.portfolio, bid)
        if quality.get("gate_status") == "BLOCKED":
            self._write_summary(quality)
            messagebox.showwarning("Blocked", "This building is blocked by the Data Quality Gate.")
            return
        context = build_site_context(self.portfolio, bid)
        context["data_quality_gate"] = quality
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"{bid}.site_context.json"
        path.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
        self._write_summary(context)
        self.status_var.set(f"Site context written to {path}")

    def generate_html(self):
        bid = self._current_building_id()
        if not bid:
            return
        quality = evaluate_site(self.portfolio, bid)
        if quality.get("gate_status") == "BLOCKED":
            self._write_summary(quality)
            messagebox.showwarning("Blocked", "HTML datasheet not generated because the site is blocked.")
            return
        context = build_site_context(self.portfolio, bid)
        context["data_quality_gate"] = quality
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        context_path = OUTPUT_DIR / f"{bid}.site_context.json"
        context_path.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
        html_path = OUTPUT_DIR / f"{bid}.building_datasheet.html"
        render_building_datasheet(context, html_path)
        self.status_var.set(f"Generated {html_path}")
        webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    SiteSelectorApp().mainloop()

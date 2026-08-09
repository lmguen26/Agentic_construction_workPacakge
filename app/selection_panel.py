from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from src.selection.scope_filter import SelectionScope, filter_buildings


class HierarchicalSelectionPanel(ttk.LabelFrame):
    """Region -> Branch -> Site -> Building cumulative multi-filter selector.

    Each dimension supports multiple selection. Empty selection means all values
    currently available for that dimension. The final selected scope is always a
    set of buildings; higher-level selections only filter which buildings are in scope.
    """

    def __init__(self, master, buildings: list[dict], on_change: Callable[[list[dict]], None] | None = None):
        super().__init__(master, text="Scope filters", padding=10)
        self.buildings = buildings
        self.on_change = on_change
        self._updating = False

        self.region_box = self._make_box("Regions", 0)
        self.branch_box = self._make_box("Branches", 1)
        self.site_box = self._make_box("Sites", 2)
        self.building_box = self._make_box("Buildings", 3, width=34)

        controls = ttk.Frame(self)
        controls.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        ttk.Button(controls, text="Select all buildings", command=self.select_all_buildings).pack(side="left")
        ttk.Button(controls, text="Clear building selection", command=lambda: self.building_box.selection_clear(0, "end")).pack(side="left", padx=6)
        ttk.Button(controls, text="Clear all filters", command=self.clear_all).pack(side="left")
        self.scope_label = ttk.Label(controls, text="")
        self.scope_label.pack(side="right")

        for box in [self.region_box, self.branch_box, self.site_box, self.building_box]:
            box.bind("<<ListboxSelect>>", self._selection_changed)

        for col in range(4):
            self.columnconfigure(col, weight=1)
        self.refresh()

    def _make_box(self, label: str, column: int, width: int = 24):
        frame = ttk.Frame(self)
        frame.grid(row=0, column=column, sticky="nsew", padx=4)
        ttk.Label(frame, text=label).pack(anchor="w")
        box = tk.Listbox(frame, selectmode="extended", exportselection=False, height=8, width=width)
        box.pack(fill="both", expand=True)
        ttk.Label(frame, text="Ctrl/Cmd or Shift for multi-select", foreground="#666666").pack(anchor="w")
        return box

    @staticmethod
    def _selected_values(box: tk.Listbox) -> tuple[str, ...]:
        return tuple(box.get(i).split(" — ", 1)[0] for i in box.curselection())

    def current_scope(self) -> SelectionScope:
        return SelectionScope(
            region_ids=self._selected_values(self.region_box),
            branch_ids=self._selected_values(self.branch_box),
            site_ids=self._selected_values(self.site_box),
            building_ids=self._selected_values(self.building_box),
        )

    def selected_buildings(self) -> list[dict]:
        scope = self.current_scope()
        rows = filter_buildings(self.buildings, scope)
        if scope.building_ids:
            return rows
        # If no explicit building selection, all buildings surviving the higher-level filters are in scope.
        higher_only = SelectionScope(scope.region_ids, scope.branch_ids, scope.site_ids, ())
        return filter_buildings(self.buildings, higher_only)

    def _label_map(self, field: str, name_field: str) -> list[str]:
        values = {}
        for b in self.buildings:
            value = b.get(field)
            if value:
                values[str(value)] = str(b.get(name_field) or value)
        return [f"{k} — {values[k]}" for k in sorted(values)]

    def _replace_values(self, box: tk.Listbox, values: list[str], preserve: set[str]):
        box.delete(0, "end")
        for idx, value in enumerate(values):
            box.insert("end", value)
            if value.split(" — ", 1)[0] in preserve:
                box.selection_set(idx)

    def refresh(self):
        self._updating = True
        try:
            selected_regions = set(self._selected_values(self.region_box))
            selected_branches = set(self._selected_values(self.branch_box))
            selected_sites = set(self._selected_values(self.site_box))
            selected_buildings = set(self._selected_values(self.building_box))

            regions = sorted({str(b.get("region_id")) for b in self.buildings if b.get("region_id")})
            self._replace_values(self.region_box, regions, selected_regions)

            region_scope = SelectionScope(region_ids=tuple(selected_regions))
            region_rows = filter_buildings(self.buildings, region_scope)
            branches = sorted({str(b.get("branch_id")) for b in region_rows if b.get("branch_id")})
            self._replace_values(self.branch_box, branches, selected_branches & set(branches))

            branch_scope = SelectionScope(region_ids=tuple(selected_regions), branch_ids=tuple(selected_branches & set(branches)))
            branch_rows = filter_buildings(self.buildings, branch_scope)
            sites = sorted({str(b.get("site_id")) for b in branch_rows if b.get("site_id")})
            self._replace_values(self.site_box, sites, selected_sites & set(sites))

            site_scope = SelectionScope(
                region_ids=tuple(selected_regions),
                branch_ids=tuple(selected_branches & set(branches)),
                site_ids=tuple(selected_sites & set(sites)),
            )
            site_rows = filter_buildings(self.buildings, site_scope)
            buildings = [f"{b.get('building_id')} — {b.get('building_name', '')}" for b in site_rows]
            valid_ids = {b.get("building_id") for b in site_rows}
            self._replace_values(self.building_box, buildings, selected_buildings & valid_ids)
        finally:
            self._updating = False
        self._notify()

    def _selection_changed(self, _event=None):
        if self._updating:
            return
        self.refresh()

    def _notify(self):
        rows = self.selected_buildings()
        self.scope_label.configure(text=f"{len(rows)} building(s) in scope")
        if self.on_change:
            self.on_change(rows)

    def select_all_buildings(self):
        self.building_box.selection_set(0, "end")
        self._notify()

    def clear_all(self):
        for box in [self.region_box, self.branch_box, self.site_box, self.building_box]:
            box.selection_clear(0, "end")
        self.refresh()

# FinDrawAI main.py — v4  (Powerful UI + Free Local AI mode)
"""
main.py — FinDrawAI Application
Complete desktop whiteboard application with AI shape recognition.

New in v4:
  - Free, offline "Local" recognition mode (local_engine.py) that needs
    NO API key at all — the app is fully usable out of the box.
    Optional "Cloud" mode (ai_engine.py / Claude) still available if the
    user adds their own ANTHROPIC_API_KEY.
  - Select / Move / Delete tool
  - Triangle & Star tools, shape fill toggle
  - Zoom (Ctrl+scroll, +/-, reset) and a toggleable grid
  - Save / Open whiteboard projects (.json) — not just export
"""

import copy
import json
import math
import os
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Optional

from PIL import Image, ImageDraw, ImageGrab, ImageTk

from ai_engine import AIEngine
from local_engine import LocalEngine

# ─────────────────────────── Palette ────────────────────────────
BG        = "#0F172A"   # app background
PANEL     = "#1E293B"   # sidebars / toolbar
SURFACE   = "#0F172A"   # card background
BORDER    = "#334155"   # subtle borders
PRIMARY   = "#3B82F6"   # blue primary action
ACCENT    = "#06B6D4"   # cyan accent
SUCCESS   = "#22C55E"   # green for status ok
WARNING   = "#F59E0B"   # amber warning
DANGER    = "#EF4444"   # red error
FREE      = "#A855F7"   # purple — free/local mode accent
TEXT_HI   = "#F1F5F9"   # primary text
TEXT_MID  = "#94A3B8"   # secondary text
TEXT_DIM  = "#475569"   # dimmed text
CANVAS_BG = "#FFFFFF"   # whiteboard
TOOL_SEL  = "#1D4ED8"   # selected tool highlight
GRID_CLR  = "#E2E8F0"   # grid line colour
SEL_CLR   = "#F59E0B"   # selection outline colour

FONT_MONO  = ("Consolas", 10)
FONT_BODY  = ("Segoe UI", 10)
FONT_BODY_B = ("Segoe UI", 10, "bold")
FONT_H3   = ("Segoe UI", 12, "bold")
FONT_H2   = ("Segoe UI", 14, "bold")
FONT_H1   = ("Segoe UI", 18, "bold")
FONT_SMALL = ("Segoe UI", 9)

TOOLS = [
    ("↖",   "select",    "Select / Move  [V]"),
    ("✏️",  "pen",       "Freehand Pen   [P]"),
    ("⬜",  "rectangle", "Rectangle      [R]"),
    ("⭕",  "circle",    "Circle         [C]"),
    ("🔺",  "triangle",  "Triangle       [Y]"),
    ("⬡",  "diamond",   "Diamond        [D]"),
    ("📏",  "line",      "Line           [L]"),
    ("➡",  "arrow",     "Arrow          [A]"),
    ("⭐",  "star",      "Star           [K]"),
    ("T",   "text",      "Text           [T]"),
    ("🧹",  "eraser",    "Eraser         [E]"),
]

GRID_SPACING = 40


# ──────────────────────────────────────────────────────────────────
# DrawingManager — stores stroke history and manages undo/redo
# ──────────────────────────────────────────────────────────────────
class DrawingManager:
    def __init__(self):
        self.history: list = [([], [])]   # list of (items, shapes) snapshots
        self.index = 0

    def snapshot(self, items: list, shapes: list):
        """Save current canvas item ids + shape records as a checkpoint."""
        self.history = self.history[: self.index + 1]
        self.history.append((list(items), copy.deepcopy(shapes)))
        self.index = len(self.history) - 1

    def undo(self) -> Optional[tuple]:
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        return None

    def redo(self) -> Optional[tuple]:
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        return None

    def can_undo(self) -> bool:
        return self.index > 0

    def can_redo(self) -> bool:
        return self.index < len(self.history) - 1

    def reset(self):
        self.history = [([], [])]
        self.index = 0


# ──────────────────────────────────────────────────────────────────
# Geometry helpers
# ──────────────────────────────────────────────────────────────────
def _norm_bbox(x1, y1, x2, y2):
    return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)


def _star_points(cx, cy, outer_r, inner_r, points=5):
    pts = []
    angle = -math.pi / 2
    step = math.pi / points
    for i in range(points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        pts.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])
        angle += step
    return pts


def _regular_polygon_points(cx, cy, r, n):
    pts = []
    angle = -math.pi / 2
    step = 2 * math.pi / n
    for _ in range(n):
        pts.extend([cx + r * math.cos(angle), cy + r * math.sin(angle)])
        angle += step
    return pts


# ──────────────────────────────────────────────────────────────────
# WhiteboardCanvas — the main drawing surface
# ──────────────────────────────────────────────────────────────────
class WhiteboardCanvas(tk.Canvas):
    def __init__(self, parent, app, **kwargs):
        super().__init__(
            parent,
            bg=CANVAS_BG,
            cursor="crosshair",
            highlightthickness=0,
            **kwargs,
        )
        self.app = app
        self.dm = DrawingManager()

        # Drawing state
        self.tool = "pen"
        self.color = "#1E293B"
        self.brush_size = 3
        self.eraser_size = 18
        self.fill_enabled = False

        self._start_x = 0
        self._start_y = 0
        self._current_stroke: list[int] = []
        self._current_points: list = []
        self._preview_id: Optional[int] = None
        self._text_entry: Optional[tk.Entry] = None

        # Every permanent canvas item id (flat, kept for eraser / legacy undo)
        self._items: list[int] = []
        # Structured, vector shape records — powers local AI, save/load,
        # and the select/move tool.
        self.shapes: list[dict] = []

        # Select tool state
        self._selected_idx: Optional[int] = None
        self._selection_box: Optional[int] = None
        self._drag_last: Optional[tuple] = None

        # Zoom / grid
        self.zoom_level = 1.0
        self.grid_visible = False

        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<B1-Motion>",       self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Control-MouseWheel>", self._on_ctrl_wheel)
        self.bind("<Control-Button-4>", lambda e: self.zoom(1.1, e.x, e.y))
        self.bind("<Control-Button-5>", lambda e: self.zoom(0.9, e.x, e.y))
        self.bind("<Configure>", lambda e: self._draw_grid())

    # ── Tool & colour setters ──────────────────────────────────────

    def set_tool(self, name: str):
        if self.tool == "select" and name != "select":
            self._clear_selection()
        self.tool = name
        cursors = {
            "eraser": "circle",
            "text": "xterm",
            "pen": "crosshair",
            "select": "arrow",
        }
        self.configure(cursor=cursors.get(name, "crosshair"))

    def set_color(self, c: str):
        self.color = c

    def set_brush_size(self, s: int):
        self.brush_size = s

    def set_fill_enabled(self, enabled: bool):
        self.fill_enabled = enabled

    # ── Canvas snapshot helpers ───────────────────────────────────

    def _record_snapshot(self):
        self.dm.snapshot(self._items[:], self.shapes)

    def _mark(self, ids):
        """Register newly created permanent item id(s), tag them for
        zoom/select, and keep _items in sync."""
        if isinstance(ids, (list, tuple)):
            for i in ids:
                self.addtag_withtag("shape", i)
                self._items.append(i)
        else:
            self.addtag_withtag("shape", ids)
            self._items.append(ids)

    # ── Input event handlers ──────────────────────────────────────

    def _on_press(self, event):
        self._start_x, self._start_y = event.x, event.y
        self._current_stroke = []
        self._current_points = [(event.x, event.y)]
        if self._preview_id:
            self.delete(self._preview_id)
            self._preview_id = None

        if self.tool == "text":
            self._start_text_input(event.x, event.y)
        elif self.tool == "select":
            self._select_at(event.x, event.y)
            self._drag_last = (event.x, event.y)

    def _on_drag(self, event):
        x, y = event.x, event.y
        sx, sy = self._start_x, self._start_y

        if self.tool == "pen":
            self._current_points.append((x, y))
            if self._current_stroke:
                prev_id = self._current_stroke[-1]
                coords = self.coords(prev_id)
                if coords:
                    lx, ly = coords[-2], coords[-1]
                    seg = self.create_line(
                        lx, ly, x, y,
                        fill=self.color,
                        width=self.brush_size,
                        capstyle=tk.ROUND,
                        joinstyle=tk.ROUND,
                        smooth=True,
                    )
                    self._current_stroke.append(seg)
            else:
                seg = self.create_line(
                    sx, sy, x, y,
                    fill=self.color,
                    width=self.brush_size,
                    capstyle=tk.ROUND,
                    smooth=True,
                )
                self._current_stroke.append(seg)

        elif self.tool == "eraser":
            self._erase_at(x, y)

        elif self.tool == "select":
            if self._selected_idx is not None and self._drag_last is not None:
                dx, dy = x - self._drag_last[0], y - self._drag_last[1]
                self._move_selected(dx, dy)
                self._drag_last = (x, y)

        else:
            if self._preview_id:
                self.delete(self._preview_id)
            self._preview_id = self._draw_shape_preview(sx, sy, x, y)

    def _on_release(self, event):
        x, y = event.x, event.y
        sx, sy = self._start_x, self._start_y

        if self.tool == "pen":
            if self._current_stroke:
                for sid in self._current_stroke:
                    self.addtag_withtag("shape", sid)
                    self._items.append(sid)
                if len(self._current_points) >= 2:
                    self.shapes.append({
                        "kind": "freehand",
                        "points": list(self._current_points),
                        "color": self.color,
                        "width": self.brush_size,
                        "canvas_ids": list(self._current_stroke),
                    })
                self._record_snapshot()
                self._current_stroke = []
                self._current_points = []

        elif self.tool == "eraser":
            self._record_snapshot()

        elif self.tool == "text":
            pass  # handled by text entry

        elif self.tool == "select":
            if self._selected_idx is not None and self._drag_last != (self._start_x, self._start_y):
                self._record_snapshot()
            self._drag_last = None

        else:
            if self._preview_id:
                self.delete(self._preview_id)
                self._preview_id = None
            item_id, coords = self._draw_shape_final(sx, sy, x, y)
            if item_id:
                self._mark(item_id)
                self.shapes.append({
                    "kind": self.tool,
                    "coords": coords,
                    "color": self.color,
                    "width": self.brush_size,
                    "fill": bool(self.fill_enabled),
                    "canvas_ids": item_id if isinstance(item_id, list) else [item_id],
                })
                self._record_snapshot()

    def _draw_shape_preview(self, x1, y1, x2, y2) -> Optional[int]:
        rect_opts = dict(outline="#94A3B8", fill="", width=1, dash=(4, 4))
        t = self.tool
        if t == "rectangle":
            return self.create_rectangle(x1, y1, x2, y2, **rect_opts)
        if t == "circle":
            return self.create_oval(x1, y1, x2, y2, **rect_opts)
        if t == "diamond":
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            return self.create_polygon(mx, y1, x2, my, mx, y2, x1, my,
                                       outline="#94A3B8", fill="", width=1, dash=(4, 4))
        if t == "triangle":
            return self.create_polygon((x1 + x2) // 2, y1, x1, y2, x2, y2,
                                       outline="#94A3B8", fill="", width=1, dash=(4, 4))
        if t == "star":
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            outer = max(8, min(abs(x2 - x1), abs(y2 - y1)) / 2)
            return self.create_polygon(*_star_points(cx, cy, outer, outer * 0.42),
                                       outline="#94A3B8", fill="", width=1, dash=(4, 4))
        if t == "line":
            return self.create_line(x1, y1, x2, y2, fill="#94A3B8", width=1, dash=(4, 4))
        if t == "arrow":
            return self.create_line(x1, y1, x2, y2, fill="#94A3B8", width=1,
                                    arrow=tk.LAST, dash=(4, 4))
        return None

    def _draw_shape_final(self, x1, y1, x2, y2):
        """Returns (canvas_id_or_ids, coords) for the finished shape."""
        c, w = self.color, self.brush_size
        fill = c if self.fill_enabled else ""
        t = self.tool
        if t == "rectangle":
            bbox = _norm_bbox(x1, y1, x2, y2)
            return self.create_rectangle(x1, y1, x2, y2, outline=c, fill=fill, width=w), list(bbox)
        if t == "circle":
            bbox = _norm_bbox(x1, y1, x2, y2)
            return self.create_oval(x1, y1, x2, y2, outline=c, fill=fill, width=w), list(bbox)
        if t == "diamond":
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            return self.create_polygon(mx, y1, x2, my, mx, y2, x1, my,
                                       outline=c, fill=fill, width=w), list(_norm_bbox(x1, y1, x2, y2))
        if t == "triangle":
            return self.create_polygon((x1 + x2) // 2, y1, x1, y2, x2, y2,
                                       outline=c, fill=fill, width=w), list(_norm_bbox(x1, y1, x2, y2))
        if t == "star":
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            outer = max(8, min(abs(x2 - x1), abs(y2 - y1)) / 2)
            return self.create_polygon(*_star_points(cx, cy, outer, outer * 0.42),
                                       outline=c, fill=fill, width=w), list(_norm_bbox(x1, y1, x2, y2))
        if t == "line":
            return self.create_line(x1, y1, x2, y2, fill=c, width=w,
                                    capstyle=tk.ROUND), [x1, y1, x2, y2]
        if t == "arrow":
            return self.create_line(x1, y1, x2, y2, fill=c, width=w,
                                    arrow=tk.LAST, arrowshape=(12, 15, 5)), [x1, y1, x2, y2]
        return None, None

    def _erase_at(self, x, y):
        r = self.eraser_size // 2
        overlapping = self.find_overlapping(x - r, y - r, x + r, y + r)
        for item in overlapping:
            if item in self._items:
                self.delete(item)
                self._items.remove(item)
                self.shapes = [
                    s for s in self.shapes
                    if item not in s.get("canvas_ids", [])
                ]
        tmp = self.create_oval(x - r, y - r, x + r, y + r,
                               outline=BORDER, fill="#F0F0F0", width=1)
        self.after(50, lambda: self.delete(tmp))

    # ── Select / Move / Delete ──────────────────────────────────────

    def _shape_bbox(self, rec: dict):
        if rec["kind"] == "freehand":
            xs = [p[0] for p in rec["points"]]
            ys = [p[1] for p in rec["points"]]
            return min(xs), min(ys), max(xs), max(ys)
        if rec["kind"] == "text":
            x, y = rec["coords"]
            return x, y, x + 100, y + 24
        x1, y1, x2, y2 = rec["coords"]
        return _norm_bbox(x1, y1, x2, y2)

    def _select_at(self, x, y):
        self._clear_selection()
        hits = self.find_overlapping(x - 3, y - 3, x + 3, y + 3)
        hit_ids = set(hits)
        for idx in range(len(self.shapes) - 1, -1, -1):
            rec = self.shapes[idx]
            if hit_ids.intersection(rec.get("canvas_ids", [])):
                self._selected_idx = idx
                self._draw_selection_box(rec)
                if hasattr(self.app, "status_msg"):
                    self.app.status_msg.configure(text=f"Selected {rec['kind']} — drag to move, Delete to remove")
                return
        if hasattr(self.app, "status_msg"):
            self.app.status_msg.configure(text="Tool: Select  |  Click a shape to select it")

    def _draw_selection_box(self, rec: dict):
        x1, y1, x2, y2 = self._shape_bbox(rec)
        pad = 6
        self._selection_box = self.create_rectangle(
            x1 - pad, y1 - pad, x2 + pad, y2 + pad,
            outline=SEL_CLR, width=2, dash=(5, 3),
        )

    def _clear_selection(self):
        if self._selection_box:
            self.delete(self._selection_box)
            self._selection_box = None
        self._selected_idx = None

    def _move_selected(self, dx, dy):
        if self._selected_idx is None:
            return
        rec = self.shapes[self._selected_idx]
        for cid in rec.get("canvas_ids", []):
            self.move(cid, dx, dy)
        if rec["kind"] == "freehand":
            rec["points"] = [(px + dx, py + dy) for px, py in rec["points"]]
        elif rec["kind"] == "text":
            rec["coords"] = [rec["coords"][0] + dx, rec["coords"][1] + dy]
        else:
            x1, y1, x2, y2 = rec["coords"]
            rec["coords"] = [x1 + dx, y1 + dy, x2 + dx, y2 + dy]
        if self._selection_box:
            self.move(self._selection_box, dx, dy)

    def delete_selected(self):
        if self._selected_idx is None:
            return
        rec = self.shapes.pop(self._selected_idx)
        for cid in rec.get("canvas_ids", []):
            self.delete(cid)
            if cid in self._items:
                self._items.remove(cid)
        self._clear_selection()
        self._record_snapshot()
        if hasattr(self.app, "status_msg"):
            self.app.status_msg.configure(text="Shape deleted")

    # ── Text input ────────────────────────────────────────────────

    def _start_text_input(self, x, y):
        if self._text_entry:
            self._commit_text()
        var = tk.StringVar()
        entry = tk.Entry(self, textvariable=var, font=("Segoe UI", 14),
                         fg=self.color, bg=CANVAS_BG,
                         relief="flat", highlightthickness=1,
                         highlightcolor=PRIMARY, width=20)
        self.create_window(x, y, window=entry, anchor="nw", tags="text_entry_win")
        entry.focus_set()
        entry.bind("<Return>", lambda e: self._commit_text(x, y, var.get()))
        entry.bind("<Escape>", lambda e: self._cancel_text())
        self._text_entry = entry
        self._text_pos = (x, y)

    def _commit_text(self, x=None, y=None, text=None):
        if self._text_entry is None:
            return
        if text is None:
            text = self._text_entry.get()
        if x is None:
            x, y = self._text_pos
        self._text_entry.destroy()
        self.delete("text_entry_win")
        self._text_entry = None
        if text.strip():
            tid = self.create_text(x, y, text=text, fill=self.color,
                                   font=("Segoe UI", 14), anchor="nw")
            self._mark(tid)
            self.shapes.append({
                "kind": "text",
                "coords": [x, y],
                "text": text,
                "color": self.color,
                "width": 1,
                "canvas_ids": [tid],
            })
            self._record_snapshot()

    def _cancel_text(self):
        if self._text_entry:
            self._text_entry.destroy()
            self.delete("text_entry_win")
            self._text_entry = None

    # ── History ───────────────────────────────────────────────────

    def undo(self):
        snapshot = self.dm.undo()
        if snapshot is not None:
            self._restore_snapshot(snapshot)

    def redo(self):
        snapshot = self.dm.redo()
        if snapshot is not None:
            self._restore_snapshot(snapshot)

    def _restore_snapshot(self, snapshot: tuple):
        items_snap, shapes_snap = snapshot
        self._clear_selection()
        current = set(self._items)
        keep = set(items_snap)
        for item in current - keep:
            try:
                self.delete(item)
            except Exception:
                pass
        self._items = [i for i in items_snap if self.find_withtag(i)]
        alive = set(self._items)
        self.shapes = [
            s for s in shapes_snap
            if not s.get("canvas_ids") or alive.intersection(s["canvas_ids"])
        ]

    def clear(self):
        self.delete("shape")
        self.delete("text_entry_win")
        self._items = []
        self.shapes = []
        self._clear_selection()
        self.dm.reset()

    # ── Zoom ─────────────────────────────────────────────────────

    def zoom(self, factor, cx=None, cy=None):
        new_level = self.zoom_level * factor
        if new_level < 0.25 or new_level > 4.0:
            return
        if cx is None:
            cx = self.winfo_width() / 2
        if cy is None:
            cy = self.winfo_height() / 2
        self.scale("shape", cx, cy, factor, factor)
        if self._selection_box:
            self.scale(self._selection_box, cx, cy, factor, factor)
        self.zoom_level = new_level
        if hasattr(self.app, "_update_zoom_label"):
            self.app._update_zoom_label()

    def reset_zoom(self):
        if self.zoom_level != 1.0:
            self.zoom(1.0 / self.zoom_level)

    def _on_ctrl_wheel(self, event):
        factor = 1.1 if event.delta > 0 else (1 / 1.1)
        self.zoom(factor, event.x, event.y)

    # ── Grid ─────────────────────────────────────────────────────

    def toggle_grid(self):
        self.grid_visible = not self.grid_visible
        self._draw_grid()
        return self.grid_visible

    def _draw_grid(self):
        self.delete("grid")
        if not self.grid_visible:
            return
        w = max(self.winfo_width(), 800)
        h = max(self.winfo_height(), 600)
        step = GRID_SPACING * self.zoom_level
        if step < 8:
            return
        x = 0.0
        while x < w:
            self.create_line(x, 0, x, h, fill=GRID_CLR, tags="grid")
            x += step
        y = 0.0
        while y < h:
            self.create_line(0, y, w, y, fill=GRID_CLR, tags="grid")
            y += step
        self.tag_lower("grid")

    # ── AI overlay rendering ──────────────────────────────────────

    def render_ai_result(self, result: dict):
        """Render the recognised clean shapes onto the canvas (works for
        both the Cloud and the Free Local engine — they share a schema)."""
        if not result.get("success"):
            return
        elements = result.get("elements", [])
        connections = result.get("connections", [])
        elem_centers: dict[int, tuple] = {}
        new_ids = []

        for el in elements:
            eid = el.get("id", 0)
            t = el.get("type", "rectangle")
            lbl = el.get("label", "")
            c = PRIMARY
            w = 2

            if t in ("rectangle", "rounded_rectangle"):
                x, y = el.get("x", 100), el.get("y", 100)
                ww, hh = el.get("width", 120), el.get("height", 60)
                new_ids += self._draw_clean_rect(x, y, ww, hh, lbl, c, w, rounded=(t == "rounded_rectangle"))
                elem_centers[eid] = (x + ww // 2, y + hh // 2)

            elif t in ("circle", "ellipse"):
                cx = el.get("cx", el.get("x", 200) + el.get("width", 100) // 2)
                cy = el.get("cy", el.get("y", 200) + el.get("height", 100) // 2)
                rx = el.get("rx", el.get("width", 100) // 2)
                ry = el.get("ry", el.get("height", 80) // 2)
                new_ids += self._draw_clean_ellipse(cx, cy, rx, ry, lbl, c, w)
                elem_centers[eid] = (cx, cy)

            elif t == "diamond":
                x, y = el.get("x", 200), el.get("y", 200)
                ww, hh = el.get("width", 140), el.get("height", 80)
                mx, my = x + ww // 2, y + hh // 2
                pts = [mx, y, x + ww, my, mx, y + hh, x, my]
                new_ids.append(self.create_polygon(*pts, outline=c, fill="", width=w))
                if lbl:
                    new_ids.append(self.create_text(mx, my, text=lbl, fill=c, font=FONT_BODY_B))
                elem_centers[eid] = (mx, my)

            elif t == "triangle":
                x, y = el.get("x", 200), el.get("y", 100)
                ww, hh = el.get("width", 120), el.get("height", 100)
                pts = [x + ww // 2, y, x, y + hh, x + ww, y + hh]
                new_ids.append(self.create_polygon(*pts, outline=c, fill="", width=w))
                if lbl:
                    new_ids.append(self.create_text(x + ww // 2, y + hh * 2 // 3, text=lbl, fill=c, font=FONT_BODY_B))
                elem_centers[eid] = (x + ww // 2, y + hh // 2)

            elif t in ("pentagon", "hexagon", "star"):
                x, y = el.get("x", 200), el.get("y", 100)
                ww, hh = el.get("width", 120), el.get("height", 120)
                cx, cy = x + ww / 2, y + hh / 2
                r = min(ww, hh) / 2
                if t == "star":
                    pts = _star_points(cx, cy, r, r * 0.42)
                else:
                    pts = _regular_polygon_points(cx, cy, r, 5 if t == "pentagon" else 6)
                new_ids.append(self.create_polygon(*pts, outline=c, fill="", width=w))
                if lbl:
                    new_ids.append(self.create_text(cx, cy, text=lbl, fill=c, font=FONT_BODY_B))
                elem_centers[eid] = (cx, cy)

            elif t in ("line", "arrow"):
                x1 = el.get("x1", el.get("x", 100))
                y1 = el.get("y1", el.get("y", 100))
                x2 = el.get("x2", x1 + el.get("width", 100))
                y2 = el.get("y2", y1)
                arrow = tk.LAST if t == "arrow" else None
                new_ids.append(self.create_line(x1, y1, x2, y2, fill=c, width=w,
                                 arrow=arrow, arrowshape=(12, 15, 5)))
                elem_centers[eid] = ((x1 + x2) // 2, (y1 + y2) // 2)

            elif t == "text":
                tx, ty = el.get("x", 200), el.get("y", 200)
                if lbl:
                    new_ids.append(self.create_text(tx, ty, text=lbl, fill="#0F172A", font=FONT_H3))
                elem_centers[eid] = (tx, ty)

            elif t == "cylinder":
                x, y = el.get("x", 200), el.get("y", 100)
                ww, hh = el.get("width", 100), el.get("height", 140)
                ry = max(10, hh // 8)
                new_ids.append(self.create_oval(x, y, x + ww, y + ry * 2, outline=c, fill="", width=w))
                new_ids.append(self.create_rectangle(x, y + ry, x + ww, y + hh, outline=c, fill="", width=w))
                new_ids.append(self.create_arc(x, y + hh - ry * 2, x + ww, y + hh, start=0, extent=-180,
                                outline=c, style=tk.ARC, width=w))
                if lbl:
                    new_ids.append(self.create_text(x + ww // 2, y + hh // 2, text=lbl, fill=c, font=FONT_BODY_B))
                elem_centers[eid] = (x + ww // 2, y + hh // 2)

        for conn in connections:
            frm_id = conn.get("from")
            to_id  = conn.get("to")
            if frm_id in elem_centers and to_id in elem_centers:
                x1, y1 = elem_centers[frm_id]
                x2, y2 = elem_centers[to_id]
                ctype = conn.get("type", "arrow")
                arrow = tk.LAST if ctype == "arrow" else None
                new_ids.append(self.create_line(x1, y1, x2, y2, fill=ACCENT, width=2,
                                 arrow=arrow, arrowshape=(12, 15, 5), smooth=True))
                clbl = conn.get("label", "")
                if clbl:
                    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                    new_ids.append(self.create_text(mx, my, text=clbl, fill=ACCENT,
                                     font=FONT_SMALL, tags="shape"))

        for i in new_ids:
            self.addtag_withtag("shape", i)
            self._items.append(i)
        self._record_snapshot()

    def _draw_clean_rect(self, x, y, w, h, label, color, line_w, rounded=False):
        ids = []
        if rounded:
            r = min(12, w // 6, h // 4)
            pts = [
                x + r, y,  x + w - r, y,
                x + w, y + r,  x + w, y + h - r,
                x + w - r, y + h,  x + r, y + h,
                x, y + h - r,  x, y + r,
            ]
            ids.append(self.create_polygon(*pts, outline=color, fill="", width=line_w, smooth=True))
        else:
            ids.append(self.create_rectangle(x, y, x + w, y + h, outline=color, fill="", width=line_w))
        if label:
            ids.append(self.create_text(x + w // 2, y + h // 2, text=label,
                             fill=color, font=FONT_BODY_B))
        return ids

    def _draw_clean_ellipse(self, cx, cy, rx, ry, label, color, line_w):
        ids = [self.create_oval(cx - rx, cy - ry, cx + rx, cy + ry,
                         outline=color, fill="", width=line_w)]
        if label:
            ids.append(self.create_text(cx, cy, text=label, fill=color, font=FONT_BODY_B))
        return ids

    # ── Export / persistence helpers ────────────────────────────────

    def get_pil_image(self) -> Image.Image:
        """Capture canvas content as a PIL Image."""
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        try:
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        except Exception:
            img = Image.new("RGB", (w, h), "white")
        return img

    def to_project_dict(self) -> dict:
        """Serialize the current whiteboard to a plain-data project file."""
        clean_shapes = []
        for s in self.shapes:
            rec = {k: v for k, v in s.items() if k != "canvas_ids"}
            clean_shapes.append(rec)
        return {"format": "findrawai-project", "version": 1, "shapes": clean_shapes}

    def load_project_dict(self, data: dict):
        """Rebuild the canvas from a saved project file."""
        self.clear()
        for rec in data.get("shapes", []):
            kind = rec.get("kind")
            color = rec.get("color", "#1E293B")
            width = rec.get("width", 2)
            fill = color if rec.get("fill") else ""
            ids = []
            if kind == "freehand":
                pts = rec.get("points", [])
                flat_ids = []
                for i in range(len(pts) - 1):
                    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
                    flat_ids.append(self.create_line(x1, y1, x2, y2, fill=color, width=width,
                                                      capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True))
                ids = flat_ids
            elif kind == "text":
                x, y = rec.get("coords", [100, 100])
                ids = [self.create_text(x, y, text=rec.get("text", ""), fill=color,
                                        font=("Segoe UI", 14), anchor="nw")]
            elif kind in ("rectangle", "circle", "diamond", "triangle", "star"):
                x1, y1, x2, y2 = rec.get("coords", [100, 100, 200, 200])
                if kind == "rectangle":
                    ids = [self.create_rectangle(x1, y1, x2, y2, outline=color, fill=fill, width=width)]
                elif kind == "circle":
                    ids = [self.create_oval(x1, y1, x2, y2, outline=color, fill=fill, width=width)]
                elif kind == "diamond":
                    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                    ids = [self.create_polygon(mx, y1, x2, my, mx, y2, x1, my,
                                               outline=color, fill=fill, width=width)]
                elif kind == "triangle":
                    ids = [self.create_polygon((x1 + x2) // 2, y1, x1, y2, x2, y2,
                                               outline=color, fill=fill, width=width)]
                elif kind == "star":
                    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                    outer = max(8, min(abs(x2 - x1), abs(y2 - y1)) / 2)
                    ids = [self.create_polygon(*_star_points(cx, cy, outer, outer * 0.42),
                                               outline=color, fill=fill, width=width)]
            elif kind in ("line", "arrow"):
                x1, y1, x2, y2 = rec.get("coords", [100, 100, 200, 100])
                arrow = tk.LAST if kind == "arrow" else None
                ids = [self.create_line(x1, y1, x2, y2, fill=color, width=width,
                                        arrow=arrow, arrowshape=(12, 15, 5) if arrow else None,
                                        capstyle=tk.ROUND)]
            if ids:
                self._mark(ids)
                rec2 = dict(rec)
                rec2["canvas_ids"] = ids
                self.shapes.append(rec2)
        self._record_snapshot()


# ──────────────────────────────────────────────────────────────────
# ExportManager
# ──────────────────────────────────────────────────────────────────
class ExportManager:
    def __init__(self, canvas: WhiteboardCanvas):
        self.canvas = canvas

    def export_png(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialfile="fin_draw_export",
            title="Export Whiteboard as PNG",
        )
        if not path:
            return
        try:
            img = self.canvas.get_pil_image()
            img.save(path, "PNG")
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def export_json(self, ai_result: Optional[dict]):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON File", "*.json")],
            initialfile="fin_draw_diagram",
            title="Export Diagram JSON",
        )
        if not path:
            return
        data = ai_result or {"note": "No AI analysis performed yet."}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Export Complete", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def save_project(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("FinDrawAI Project", "*.json")],
            initialfile="fin_draw_project",
            title="Save Whiteboard Project",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.canvas.to_project_dict(), f, indent=2)
            messagebox.showinfo("Project Saved", f"Saved:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Failed", str(e))

    def open_project(self):
        path = filedialog.askopenfilename(
            filetypes=[("FinDrawAI Project", "*.json"), ("All files", "*.*")],
            title="Open Whiteboard Project",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.canvas.load_project_dict(data)
            messagebox.showinfo("Project Loaded", f"Loaded:\n{path}")
        except Exception as e:
            messagebox.showerror("Open Failed", str(e))


# ──────────────────────────────────────────────────────────────────
# AIAnalysisPanel — right sidebar
# ──────────────────────────────────────────────────────────────────
class AIAnalysisPanel(tk.Frame):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, bg=PANEL, width=250, **kwargs)
        self.app = app
        self.pack_propagate(False)
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=PANEL)
        hdr.pack(fill="x", padx=14, pady=(16, 4))
        tk.Label(hdr, text="AI ANALYSIS", font=FONT_H3,
                 fg=TEXT_HI, bg=PANEL).pack(anchor="w")
        self.engine_label = tk.Label(hdr, text="", font=FONT_SMALL, fg=FREE, bg=PANEL)
        self.engine_label.pack(anchor="w")
        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=14, pady=4)

        status_row = tk.Frame(self, bg=PANEL)
        status_row.pack(fill="x", padx=14, pady=6)
        self.status_dot = tk.Label(status_row, text="●", fg=SUCCESS,
                                   bg=PANEL, font=("Segoe UI", 12))
        self.status_dot.pack(side="left")
        self.status_label = tk.Label(status_row, text=" AI Ready",
                                     fg=TEXT_MID, bg=PANEL, font=FONT_BODY)
        self.status_label.pack(side="left")

        sep2 = tk.Frame(self, bg=BORDER, height=1)
        sep2.pack(fill="x", padx=14, pady=4)

        info = tk.Frame(self, bg=PANEL)
        info.pack(fill="x", padx=14, pady=4)

        self.detected_val = self._add_info_row(info, "Detected:", "—")
        self.confidence_val = self._add_info_row(info, "Confidence:", "—")

        sep3 = tk.Frame(self, bg=BORDER, height=1)
        sep3.pack(fill="x", padx=14, pady=4)

        tk.Label(self, text="Description", font=FONT_BODY_B,
                 fg=TEXT_MID, bg=PANEL).pack(anchor="w", padx=14)
        self.desc_label = tk.Label(
            self, text="Draw something and click\n✨ Recognize Drawing",
            font=FONT_BODY, fg=TEXT_DIM, bg=PANEL,
            wraplength=220, justify="left",
        )
        self.desc_label.pack(anchor="w", padx=14, pady=4)

        sep4 = tk.Frame(self, bg=BORDER, height=1)
        sep4.pack(fill="x", padx=14, pady=4)

        tk.Label(self, text="Elements", font=FONT_BODY_B,
                 fg=TEXT_MID, bg=PANEL).pack(anchor="w", padx=14)
        self.stats_label = tk.Label(self, text="—", font=FONT_BODY,
                                    fg=TEXT_DIM, bg=PANEL, justify="left")
        self.stats_label.pack(anchor="w", padx=14, pady=2)

        sep5 = tk.Frame(self, bg=BORDER, height=1)
        sep5.pack(fill="x", padx=14, pady=6)

        tk.Label(self, text="AI Suggestions", font=FONT_BODY_B,
                 fg=TEXT_MID, bg=PANEL).pack(anchor="w", padx=14)
        self.suggestions_frame = tk.Frame(self, bg=PANEL)
        self.suggestions_frame.pack(fill="x", padx=14, pady=4)
        self.no_sug_label = tk.Label(self.suggestions_frame, text="None yet",
                                     fg=TEXT_DIM, bg=PANEL, font=FONT_SMALL)
        self.no_sug_label.pack(anchor="w")

        sep6 = tk.Frame(self, bg=BORDER, height=1)
        sep6.pack(fill="x", padx=14, pady=6)

        self.apply_btn = tk.Button(
            self,
            text="✨  Apply AI Cleanup",
            font=FONT_BODY_B,
            fg=TEXT_HI, bg=PRIMARY,
            activebackground=TOOL_SEL,
            activeforeground=TEXT_HI,
            relief="flat", bd=0,
            cursor="hand2",
            state="disabled",
            command=self.app.apply_ai_cleanup,
            pady=8,
        )
        self.apply_btn.pack(fill="x", padx=14, pady=4)

        self.pack_propagate(False)
        bottom = tk.Frame(self, bg=PANEL)
        bottom.pack(side="bottom", fill="x", padx=14, pady=10)
        tk.Frame(bottom, bg=BORDER, height=1).pack(fill="x", pady=6)
        tk.Label(bottom, text="WHITEBOARD", font=FONT_SMALL,
                 fg=TEXT_DIM, bg=PANEL).pack(anchor="w")
        tk.Label(bottom, text="● Local Session", font=FONT_SMALL,
                 fg=TEXT_MID, bg=PANEL).pack(anchor="w")

    def _add_info_row(self, parent, key: str, value: str) -> tk.Label:
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=key, font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack(anchor="w")
        val_lbl = tk.Label(row, text=value, font=FONT_BODY_B, fg=TEXT_HI, bg=PANEL)
        val_lbl.pack(anchor="w")
        return val_lbl

    # ── Public update methods ─────────────────────────────────────

    def set_status(self, status: str, text: str):
        colors = {"ready": SUCCESS, "processing": WARNING, "error": DANGER, "done": SUCCESS}
        dots   = {"ready": "●", "processing": "◌", "error": "●", "done": "✓"}
        self.status_dot.configure(fg=colors.get(status, TEXT_MID),
                                  text=dots.get(status, "●"))
        self.status_label.configure(text=f" {text}")

    def update_result(self, result: dict):
        engine = result.get("engine", "cloud")
        self.engine_label.configure(
            text="🆓 Free Local Engine" if engine == "local" else "☁ Cloud (Claude) Engine",
            fg=FREE if engine == "local" else ACCENT,
        )

        success = result.get("success", False)
        if not success:
            self.set_status("error", "Recognition Failed")
            self.desc_label.configure(text=result.get("description", "Unknown error"), fg=DANGER)
            self.detected_val.configure(text="—")
            self.confidence_val.configure(text="—")
            self.stats_label.configure(text="—")
            self._update_suggestions(result.get("suggestions", []))
            self.apply_btn.configure(state="disabled")
            return

        dtype = result.get("drawing_type", "unknown").replace("_", " ").title()
        conf = result.get("confidence", 0.0)
        conf_pct = f"{int(conf * 100)}%"
        desc = result.get("description", "")
        elements = result.get("elements", [])
        connections = result.get("connections", [])

        self.detected_val.configure(text=dtype)
        self.confidence_val.configure(text=conf_pct)
        self.desc_label.configure(text=desc or "—", fg=TEXT_MID)
        self.stats_label.configure(
            text=f"{len(elements)} Node{'s' if len(elements) != 1 else ''}, "
                 f"{len(connections)} Connection{'s' if len(connections) != 1 else ''}"
        )
        self._update_suggestions(result.get("suggestions", []))
        self.apply_btn.configure(state="normal")
        self.set_status("done", "Analysis Complete")

    def _update_suggestions(self, suggestions: list):
        for w in self.suggestions_frame.winfo_children():
            w.destroy()
        if not suggestions:
            tk.Label(self.suggestions_frame, text="None yet",
                     fg=TEXT_DIM, bg=PANEL, font=FONT_SMALL).pack(anchor="w")
            return
        for sug in suggestions[:6]:
            tk.Label(self.suggestions_frame, text=f"✓  {sug}",
                     fg=ACCENT, bg=PANEL, font=FONT_SMALL,
                     wraplength=210, justify="left").pack(anchor="w", pady=1)


# ──────────────────────────────────────────────────────────────────
# FinDrawApp — root application
# ──────────────────────────────────────────────────────────────────
class FinDrawApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FinDrawAI")
        self.geometry("1440x820")
        self.minsize(1180, 680)
        self.configure(bg=BG)

        self.ai = AIEngine()          # optional Cloud (Claude) engine
        self.local_ai = LocalEngine()  # always-available Free engine
        # Default to Free mode so the app works with zero setup / no API key.
        self.ai_mode = "local"
        self.last_ai_result: Optional[dict] = None
        self._current_tool = "select"

        self._setup_styles()
        self._build_ui()
        self._bind_shortcuts()
        self._update_ai_connection_indicator()

    # ── Styles ────────────────────────────────────────────────────

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TScale", background=PANEL, troughcolor=BORDER,
                        sliderlength=16, sliderrelief="flat")

    # ── UI construction ───────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=0, pady=0)

        self.toolbar = self._build_toolbar(main)
        self.toolbar.pack(side="left", fill="y", padx=(8, 4), pady=8)

        canvas_wrap = tk.Frame(main, bg=BORDER, bd=1, relief="flat")
        canvas_wrap.pack(side="left", fill="both", expand=True, padx=4, pady=8)

        self.canvas = WhiteboardCanvas(canvas_wrap, app=self)
        self.canvas.pack(fill="both", expand=True)
        self.export_mgr = ExportManager(self.canvas)

        self.ai_panel = AIAnalysisPanel(main, app=self)
        self.ai_panel.pack(side="right", fill="y", padx=(4, 8), pady=8)

        self._build_statusbar()
        self._select_tool("select")

    def _build_header(self):
        hdr = tk.Frame(self, bg=PANEL, height=64)
        hdr.pack(fill="x", padx=0, pady=0)
        hdr.pack_propagate(False)

        inner = tk.Frame(hdr, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=16, pady=0)

        logo_block = tk.Frame(inner, bg=PANEL)
        logo_block.pack(side="left", fill="y")
        tk.Label(logo_block, text="Fin", font=("Segoe UI", 20, "bold"),
                 fg=PRIMARY, bg=PANEL).pack(side="left", pady=12)
        tk.Label(logo_block, text="Draw", font=("Segoe UI", 20, "bold"),
                 fg=TEXT_HI, bg=PANEL).pack(side="left", pady=12)
        tk.Label(logo_block, text="AI", font=("Segoe UI", 20, "bold"),
                 fg=ACCENT, bg=PANEL).pack(side="left", pady=12)
        tk.Label(logo_block, text="  AI-Powered Intelligent Whiteboard",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack(side="left", pady=14)

        right = tk.Frame(inner, bg=PANEL)
        right.pack(side="right", fill="y")

        # ── AI mode segmented toggle ──
        mode_frame = tk.Frame(right, bg=SURFACE)
        mode_frame.pack(side="left", padx=(0, 10), pady=16)
        self.mode_btn_local = tk.Button(
            mode_frame, text="🆓 Free", font=FONT_SMALL, fg=TEXT_HI, bg=FREE,
            relief="flat", bd=0, padx=8, pady=5, cursor="hand2",
            command=lambda: self._set_ai_mode("local"))
        self.mode_btn_local.pack(side="left")
        self.mode_btn_cloud = tk.Button(
            mode_frame, text="☁ Cloud", font=FONT_SMALL, fg=TEXT_MID, bg=SURFACE,
            relief="flat", bd=0, padx=8, pady=5, cursor="hand2",
            command=lambda: self._set_ai_mode("cloud"))
        self.mode_btn_cloud.pack(side="left")

        self.api_status_label = tk.Label(right, text="● Checking…",
                                         font=FONT_SMALL, fg=WARNING, bg=PANEL)
        self.api_status_label.pack(side="left", padx=(0, 14), pady=20)

        buttons = [
            ("↩",  self.undo,          PANEL, "Undo  [Ctrl+Z]"),
            ("↪",  self.redo,          PANEL, "Redo  [Ctrl+Y]"),
            ("▦",  self.toggle_grid,   PANEL, "Toggle Grid  [G]"),
            ("－",  self.zoom_out,      PANEL, "Zoom Out  [-]"),
            ("＋",  self.zoom_in,       PANEL, "Zoom In  [+]"),
            ("💾", self.save_project,  PANEL, "Save Project  [Ctrl+Shift+S]"),
            ("📂", self.open_project,  PANEL, "Open Project  [Ctrl+O]"),
            ("🖼 Export",  self._show_export,  PANEL, "Export PNG/JSON  [Ctrl+S]"),
            ("✨ Recognize", self.recognize_drawing, PRIMARY, "Recognize Drawing"),
            ("✕ Clear",   self.clear_canvas,  DANGER, "Clear Canvas"),
        ]
        for txt, cmd, col, tip in buttons:
            fg = TEXT_HI if col != PANEL else TEXT_MID
            btn = tk.Button(right, text=txt, font=FONT_BODY_B,
                            fg=fg, bg=col,
                            activebackground=TOOL_SEL, activeforeground=TEXT_HI,
                            relief="flat", bd=0, padx=10, pady=6,
                            cursor="hand2", command=cmd)
            btn.pack(side="left", padx=2, pady=16)
            self._add_tooltip(btn, tip)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

    def _build_toolbar(self, parent) -> tk.Frame:
        tb = tk.Frame(parent, bg=PANEL, width=76)
        tb.pack_propagate(False)

        tk.Label(tb, text="TOOLS", font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack(pady=(10, 4))
        tk.Frame(tb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=2)

        self._tool_buttons: dict[str, tk.Button] = {}
        for icon, name, tip in TOOLS:
            btn = tk.Button(
                tb, text=icon, font=("Segoe UI", 15),
                fg=TEXT_MID, bg=PANEL,
                activebackground=TOOL_SEL, activeforeground=TEXT_HI,
                relief="flat", bd=0, width=3, pady=7,
                cursor="hand2",
                command=lambda n=name: self._select_tool(n),
            )
            btn.pack(fill="x", padx=6, pady=1)
            self._tool_buttons[name] = btn
            self._add_tooltip(btn, tip)

        self._tool_buttons["select"].configure(bg=TOOL_SEL, fg=TEXT_HI)

        tk.Frame(tb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=8)

        # Fill toggle
        self.fill_var = tk.BooleanVar(value=False)
        fill_chk = tk.Checkbutton(
            tb, text="Fill", variable=self.fill_var, font=FONT_SMALL,
            fg=TEXT_MID, bg=PANEL, selectcolor=SURFACE,
            activebackground=PANEL, activeforeground=TEXT_HI,
            command=lambda: self.canvas.set_fill_enabled(self.fill_var.get()),
        )
        fill_chk.pack(pady=2)
        self._add_tooltip(fill_chk, "Fill shapes with colour  [F]")

        tk.Frame(tb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=8)

        tk.Label(tb, text="COLOR", font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack()
        self.color_preview = tk.Canvas(tb, width=36, height=36,
                                       bg="#1E293B", highlightthickness=1,
                                       highlightbackground=BORDER, cursor="hand2")
        self.color_preview.pack(pady=4)
        self._draw_color_swatch("#1E293B")
        self.color_preview.bind("<Button-1>", lambda e: self._pick_color())

        presets_frame = tk.Frame(tb, bg=PANEL)
        presets_frame.pack(pady=4)
        presets = ["#1E293B", "#3B82F6", "#EF4444", "#22C55E",
                   "#F59E0B", "#A855F7", "#06B6D4", "#000000"]
        for i, pc in enumerate(presets):
            c = tk.Canvas(presets_frame, width=14, height=14, bg=pc,
                          highlightthickness=0, cursor="hand2")
            c.grid(row=i // 2, column=i % 2, padx=2, pady=2)
            c.bind("<Button-1>", lambda e, p=pc: self._set_color(p))

        tk.Frame(tb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=8)

        tk.Label(tb, text="SIZE", font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack()
        self.size_scale = tk.Scale(
            tb, from_=1, to=20, orient="vertical",
            bg=PANEL, fg=TEXT_MID, troughcolor=BORDER,
            highlightthickness=0, relief="flat",
            sliderlength=16, length=80,
            command=self._on_size_change,
        )
        self.size_scale.set(3)
        self.size_scale.pack(pady=2)

        tk.Frame(tb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=8)

        tk.Label(tb, text="ZOOM", font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack()
        self.zoom_label = tk.Label(tb, text="100%", font=FONT_BODY_B, fg=TEXT_HI, bg=PANEL)
        self.zoom_label.pack(pady=2)

        return tb

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=PANEL, height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", side="bottom")
        self.status_msg = tk.Label(bar, text="Ready  |  Draw with mouse  |  Click ✨ Recognize to analyse",
                                   font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL, anchor="w")
        self.status_msg.pack(side="left", padx=12)
        self.coord_label = tk.Label(bar, text="", font=FONT_MONO, fg=TEXT_DIM, bg=PANEL)
        self.coord_label.pack(side="right", padx=12)
        self.canvas.bind("<Motion>", self._on_mouse_move)

    # ── Tool management ───────────────────────────────────────────

    def _select_tool(self, name: str):
        self._current_tool = name
        if hasattr(self, 'canvas'):
            self.canvas.set_tool(name)
        for n, btn in self._tool_buttons.items():
            btn.configure(
                bg=TOOL_SEL if n == name else PANEL,
                fg=TEXT_HI if n == name else TEXT_MID,
            )
        if hasattr(self, 'status_msg'):
            hint = "Click a shape to select it, drag to move, Delete to remove" if name == "select" \
                   else "Click ✨ Recognize to analyse"
            self.status_msg.configure(
                text=f"Tool: {name.replace('_', ' ').title()}  |  {hint}"
            )

    def _pick_color(self):
        result = colorchooser.askcolor(color=self.canvas.color, title="Choose Colour")
        if result and result[1]:
            self._set_color(result[1])

    def _set_color(self, color: str):
        self.canvas.set_color(color)
        self._draw_color_swatch(color)

    def _draw_color_swatch(self, color: str):
        self.color_preview.delete("all")
        self.color_preview.configure(bg=color)
        self.color_preview.create_text(18, 18, text="✎", fill="#FFFFFF", font=("Segoe UI", 14))

    def _on_size_change(self, val):
        size = int(float(val))
        self.canvas.set_brush_size(size)
        if self._current_tool == "eraser":
            self.canvas.eraser_size = max(8, size * 3)

    def _on_mouse_move(self, event):
        self.coord_label.configure(text=f"x:{event.x}  y:{event.y}")

    # ── Canvas actions ────────────────────────────────────────────

    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas",
                               "Clear the entire whiteboard?",
                               icon="warning"):
            self.canvas.clear()
            self.last_ai_result = None
            self.ai_panel.set_status("ready", "AI Ready")
            self.ai_panel.desc_label.configure(
                text="Draw something and click\n✨ Recognize Drawing", fg=TEXT_DIM
            )
            self.ai_panel.detected_val.configure(text="—")
            self.ai_panel.confidence_val.configure(text="—")
            self.ai_panel.stats_label.configure(text="—")
            self.ai_panel.apply_btn.configure(state="disabled")
            self.status_msg.configure(text="Canvas cleared")

    def undo(self):
        self.canvas.undo()
        self.status_msg.configure(text="Undo")

    def redo(self):
        self.canvas.redo()
        self.status_msg.configure(text="Redo")

    def toggle_grid(self):
        visible = self.canvas.toggle_grid()
        self.status_msg.configure(text=f"Grid {'shown' if visible else 'hidden'}")

    def zoom_in(self):
        self.canvas.zoom(1.15)

    def zoom_out(self):
        self.canvas.zoom(1 / 1.15)

    def reset_zoom(self):
        self.canvas.reset_zoom()

    def _update_zoom_label(self):
        self.zoom_label.configure(text=f"{int(self.canvas.zoom_level * 100)}%")

    def save_project(self):
        self.export_mgr.save_project()

    def open_project(self):
        self.export_mgr.open_project()

    # ── AI mode ──────────────────────────────────────────────────

    def _set_ai_mode(self, mode: str):
        self.ai_mode = mode
        self.mode_btn_local.configure(
            bg=FREE if mode == "local" else SURFACE,
            fg=TEXT_HI if mode == "local" else TEXT_MID,
        )
        self.mode_btn_cloud.configure(
            bg=PRIMARY if mode == "cloud" else SURFACE,
            fg=TEXT_HI if mode == "cloud" else TEXT_MID,
        )
        self._update_ai_connection_indicator()
        label = "Free local recognizer — no API key needed" if mode == "local" \
                else "Cloud (Claude) recognizer selected"
        self.status_msg.configure(text=label)

    # ── AI recognition ────────────────────────────────────────────

    def recognize_drawing(self):
        if not self.canvas.shapes:
            messagebox.showinfo("Empty Canvas",
                                "Please draw something before recognising.")
            return

        if self.ai_mode == "cloud" and not self.ai.is_connected():
            st = self.ai.get_status()
            switch = messagebox.askyesno(
                "Cloud AI Unavailable",
                f"Cannot connect to the Cloud AI engine.\n\n{st['message']}\n\n"
                "Add your ANTHROPIC_API_KEY to the .env file to use Cloud mode.\n\n"
                "Switch to Free (local, no API key) mode now and recognise anyway?",
            )
            if switch:
                self._set_ai_mode("local")
            else:
                return

        self.ai_panel.set_status("processing", "Analysing drawing…")
        self.status_msg.configure(text="Analysing…")
        self.update_idletasks()

        if self.ai_mode == "cloud":
            img = self.canvas.get_pil_image()
            result = self.ai.recognize(img)
        else:
            result = self.local_ai.recognize(self.canvas.shapes)

        self.last_ai_result = result
        self.ai_panel.update_result(result)

        if result.get("success"):
            n = len(result.get("elements", []))
            c = len(result.get("connections", []))
            self.status_msg.configure(
                text=f"AI found {n} element{'s' if n != 1 else ''} "
                     f"and {c} connection{'s' if c != 1 else ''}  |  Click Apply to render clean version"
            )
        else:
            self.status_msg.configure(text="Recognition failed — see AI panel for details")

    def apply_ai_cleanup(self):
        if not self.last_ai_result or not self.last_ai_result.get("success"):
            return
        self.canvas.render_ai_result(self.last_ai_result)
        self.status_msg.configure(text="AI clean version applied to canvas")
        self.ai_panel.set_status("done", "Cleanup Applied")

    # ── Export ────────────────────────────────────────────────────

    def _show_export(self):
        win = tk.Toplevel(self)
        win.title("Export")
        win.geometry("300x220")
        win.configure(bg=PANEL)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Export Whiteboard", font=FONT_H2,
                 fg=TEXT_HI, bg=PANEL).pack(pady=(18, 8))
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=16)

        btn_frame = tk.Frame(win, bg=PANEL)
        btn_frame.pack(pady=16)

        def _png():
            win.destroy()
            self.export_mgr.export_png()

        def _json():
            win.destroy()
            self.export_mgr.export_json(self.last_ai_result)

        def _project():
            win.destroy()
            self.export_mgr.save_project()

        tk.Button(btn_frame, text="📷  Export as PNG", font=FONT_BODY_B,
                  fg=TEXT_HI, bg=PRIMARY, relief="flat", bd=0,
                  padx=14, pady=8, cursor="hand2", command=_png).pack(pady=4)
        tk.Button(btn_frame, text="{ }  Export AI Diagram JSON", font=FONT_BODY_B,
                  fg=TEXT_HI, bg=SURFACE, relief="flat", bd=0,
                  padx=14, pady=8, cursor="hand2", command=_json).pack(pady=4)
        tk.Button(btn_frame, text="💾  Save Full Project", font=FONT_BODY_B,
                  fg=TEXT_HI, bg=SURFACE, relief="flat", bd=0,
                  padx=14, pady=8, cursor="hand2", command=_project).pack(pady=4)

    # ── Keyboard shortcuts ────────────────────────────────────────

    def _bind_shortcuts(self):
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<Control-s>", lambda e: self.export_mgr.export_png())
        self.bind("<Control-Shift-S>", lambda e: self.save_project())
        self.bind("<Control-o>", lambda e: self.open_project())
        self.bind("<Delete>",    lambda e: self.canvas.delete_selected())
        self.bind("<BackSpace>", lambda e: self.canvas.delete_selected()
                  if self._current_tool == "select" else None)
        self.bind("v",           lambda e: self._select_tool("select"))
        self.bind("p",           lambda e: self._select_tool("pen"))
        self.bind("e",           lambda e: self._select_tool("eraser"))
        self.bind("r",           lambda e: self._select_tool("rectangle"))
        self.bind("c",           lambda e: self._select_tool("circle"))
        self.bind("y",           lambda e: self._select_tool("triangle"))
        self.bind("l",           lambda e: self._select_tool("line"))
        self.bind("a",           lambda e: self._select_tool("arrow"))
        self.bind("k",           lambda e: self._select_tool("star"))
        self.bind("d",           lambda e: self._select_tool("diamond"))
        self.bind("t",           lambda e: self._select_tool("text"))
        self.bind("g",           lambda e: self.toggle_grid())
        self.bind("f",           lambda e: self._toggle_fill_key())
        self.bind("<plus>",      lambda e: self.zoom_in())
        self.bind("<equal>",     lambda e: self.zoom_in())
        self.bind("<minus>",     lambda e: self.zoom_out())
        self.bind("0",           lambda e: self.reset_zoom())

    def _toggle_fill_key(self):
        self.fill_var.set(not self.fill_var.get())
        self.canvas.set_fill_enabled(self.fill_var.get())

    # ── Tooltip helper ────────────────────────────────────────────

    def _add_tooltip(self, widget, text: str):
        tip_win = None

        def show(e):
            nonlocal tip_win
            tip_win = tk.Toplevel(widget)
            tip_win.wm_overrideredirect(True)
            tip_win.wm_geometry(f"+{e.x_root + 16}+{e.y_root + 4}")
            lbl = tk.Label(tip_win, text=text, font=FONT_SMALL,
                           fg=TEXT_HI, bg="#1E293B",
                           relief="flat", padx=6, pady=3)
            lbl.pack()

        def hide(e):
            nonlocal tip_win
            if tip_win:
                tip_win.destroy()
                tip_win = None

        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    # ── Connection indicator ──────────────────────────────────────

    def _update_ai_connection_indicator(self):
        if self.ai_mode == "local":
            self.api_status_label.configure(text="● Free Mode — No Key Needed", fg=FREE)
            return
        st = self.ai.get_status()
        if st["status"] == "ready":
            self.api_status_label.configure(text="● Cloud API Connected", fg=SUCCESS)
        elif st["status"] == "no_key":
            self.api_status_label.configure(text="● No API Key — using Cloud mode will fail", fg=WARNING)
        else:
            self.api_status_label.configure(text="● Cloud API Error", fg=DANGER)


# ──────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = FinDrawApp()
    app.mainloop()
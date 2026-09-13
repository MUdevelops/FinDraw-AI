"""
local_engine.py — FinDrawAI Free Local Recognition Engine
Offline, heuristic shape/diagram recognizer that needs NO API key,
NO internet connection, and NO account. It works directly on the
vector shape records the canvas already keeps (exact coordinates for
tool-drawn shapes, raw point paths for freehand strokes) instead of
calling any cloud AI.

It is intentionally simple and explainable geometry, not a neural
model — so it will never be as flexible as the optional Cloud
(Claude) engine in ai_engine.py, but it makes the app fully usable
for free, out of the box, by anyone with no setup at all.
"""

import math
from typing import Optional


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _bbox(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _point_line_distance(p, a, b):
    if a == b:
        return _dist(p, a)
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def _rdp(points, epsilon):
    """Ramer–Douglas–Peucker polyline simplification."""
    if len(points) < 3:
        return points
    dmax, index = 0.0, 0
    for i in range(1, len(points) - 1):
        d = _point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index, dmax = i, d
    if dmax > epsilon:
        left = _rdp(points[: index + 1], epsilon)
        right = _rdp(points[index:], epsilon)
        return left[:-1] + right
    return [points[0], points[-1]]


class LocalEngine:
    """Heuristic, offline stand-in for AIEngine. Same result shape,
    zero external dependencies, zero cost, zero API key."""

    def is_connected(self) -> bool:
        return True

    def get_status(self) -> dict:
        return {"status": "ready", "message": "Free local recognizer — no API key needed"}

    # ── Public entry point ──────────────────────────────────────────

    def recognize(self, shapes: list) -> dict:
        elements = []
        used_text_idx = set()

        # Pass 1: classify every non-text shape.
        for idx, rec in enumerate(shapes):
            if rec.get("kind") == "text":
                continue
            el = self._classify(rec, idx)
            if el:
                elements.append(el)

        # Pass 2: attach nearby text records as labels; anything left
        # over becomes its own standalone text element.
        for idx, rec in enumerate(shapes):
            if rec.get("kind") != "text":
                continue
            label = rec.get("text", "")
            attached = self._attach_label(elements, rec)
            if not attached:
                elements.append({
                    "id": len(elements),
                    "type": "text",
                    "label": label,
                    "x": rec["coords"][0],
                    "y": rec["coords"][1],
                    "width": max(40, len(label) * 8),
                    "height": 24,
                    "style": "normal",
                })
            used_text_idx.add(idx)

        # Re-number ids sequentially (attach_label may leave gaps).
        for i, el in enumerate(elements):
            el["id"] = i

        connections = self._infer_connections(shapes, elements)
        drawing_type = self._guess_drawing_type(elements, connections)
        suggestions = self._suggestions(elements, connections)

        success = len(elements) > 0
        return {
            "success": success,
            "drawing_type": drawing_type,
            "confidence": 0.78 if success else 0.0,
            "description": (
                f"Locally recognised {len(elements)} element(s) and "
                f"{len(connections)} connection(s) — free offline mode, no API key used."
                if success else
                "Couldn't make out a clear shape locally. Try drawing something more "
                "defined, or switch to Cloud mode for stronger recognition."
            ),
            "elements": elements,
            "connections": connections,
            "suggestions": suggestions,
            "engine": "local",
        }

    # ── Classification ──────────────────────────────────────────────

    def _classify(self, rec: dict, idx: int) -> Optional[dict]:
        kind = rec.get("kind")
        color = rec.get("color", "#1E293B")

        # Tool-drawn shapes already know exactly what they are.
        if kind in ("rectangle", "diamond", "triangle", "star"):
            x1, y1, x2, y2 = rec["coords"]
            return {
                "id": idx, "type": kind, "label": "",
                "x": min(x1, x2), "y": min(y1, y2),
                "width": abs(x2 - x1), "height": abs(y2 - y1),
                "style": "normal",
            }
        if kind == "circle":
            x1, y1, x2, y2 = rec["coords"]
            return {
                "id": idx, "type": "circle", "label": "",
                "cx": (x1 + x2) / 2, "cy": (y1 + y2) / 2,
                "rx": abs(x2 - x1) / 2, "ry": abs(y2 - y1) / 2,
                "x": min(x1, x2), "y": min(y1, y2),
                "width": abs(x2 - x1), "height": abs(y2 - y1),
            }
        if kind in ("line", "arrow"):
            x1, y1, x2, y2 = rec["coords"]
            return {
                "id": idx, "type": kind, "label": "",
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
            }
        if kind == "freehand":
            return self._classify_freehand(rec, idx)
        return None

    def _classify_freehand(self, rec: dict, idx: int) -> Optional[dict]:
        points = rec.get("points", [])
        if len(points) < 3:
            return None
        x1, y1, x2, y2 = _bbox(points)
        w, h = max(1.0, x2 - x1), max(1.0, y2 - y1)
        diag = math.hypot(w, h)
        if diag < 6:
            return None

        start, end = points[0], points[-1]
        closed = _dist(start, end) < 0.22 * diag

        simplified = _rdp(points, epsilon=max(2.0, 0.045 * diag))
        corners = len(simplified) - (2 if closed else 1)
        corners = max(corners, 1)

        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        radii = [_dist(p, (cx, cy)) for p in points]
        mean_r = sum(radii) / len(radii)
        var_r = sum((r - mean_r) ** 2 for r in radii) / len(radii)
        roundness = (var_r ** 0.5) / mean_r if mean_r else 1.0

        if closed and roundness < 0.28 and corners >= 6:
            shape_type = "circle" if 0.75 < w / h < 1.33 else "ellipse"
            return {
                "id": idx, "type": shape_type, "label": "",
                "cx": cx, "cy": cy, "rx": w / 2, "ry": h / 2,
                "x": x1, "y": y1, "width": w, "height": h,
            }
        if closed and corners == 3:
            return {"id": idx, "type": "triangle", "label": "",
                    "x": x1, "y": y1, "width": w, "height": h}
        if closed and corners == 4:
            return {"id": idx, "type": "rectangle", "label": "",
                    "x": x1, "y": y1, "width": w, "height": h}
        if closed and corners == 5:
            return {"id": idx, "type": "pentagon", "label": "",
                    "x": x1, "y": y1, "width": w, "height": h}
        if closed and corners >= 6:
            return {"id": idx, "type": "hexagon", "label": "",
                    "x": x1, "y": y1, "width": w, "height": h}
        if not closed and corners <= 2:
            return {"id": idx, "type": "line", "label": "",
                    "x1": start[0], "y1": start[1], "x2": end[0], "y2": end[1]}
        # Fell through: keep it as a generic freeform sketch shape.
        return {"id": idx, "type": "rectangle", "label": "", "style": "sketch",
                "x": x1, "y": y1, "width": w, "height": h}

    # ── Labels ───────────────────────────────────────────────────────

    def _attach_label(self, elements: list, text_rec: dict) -> bool:
        tx, ty = text_rec["coords"]
        for el in elements:
            ex = el.get("x", el.get("cx", 0) - el.get("rx", 0))
            ey = el.get("y", el.get("cy", 0) - el.get("ry", 0))
            ew = el.get("width", el.get("rx", 0) * 2 or 40)
            eh = el.get("height", el.get("ry", 0) * 2 or 40)
            pad = 14
            if (ex - pad <= tx <= ex + ew + pad) and (ey - pad <= ty <= ey + eh + pad):
                if not el.get("label"):
                    el["label"] = text_rec.get("text", "")
                    return True
        return False

    # ── Connections ─────────────────────────────────────────────────

    def _infer_connections(self, shapes: list, elements: list) -> list:
        connections = []
        node_els = [e for e in elements if e["type"] not in ("line", "arrow", "text")]

        def bbox_of(el):
            if "cx" in el:
                return (el["cx"] - el["rx"], el["cy"] - el["ry"],
                        el["cx"] + el["rx"], el["cy"] + el["ry"])
            x, y = el.get("x", 0), el.get("y", 0)
            w, h = el.get("width", 0), el.get("height", 0)
            return (x, y, x + w, y + h)

        for el in elements:
            if el["type"] not in ("line", "arrow"):
                continue
            p1, p2 = (el["x1"], el["y1"]), (el["x2"], el["y2"])
            frm = self._nearest_node(p1, node_els, bbox_of)
            to = self._nearest_node(p2, node_els, bbox_of)
            if frm is not None and to is not None and frm != to:
                connections.append({
                    "from": frm, "to": to,
                    "type": el["type"], "label": "",
                })
        return connections

    def _nearest_node(self, point, node_els, bbox_of, max_dist=45):
        """Nearest element whose bounding box (padded by max_dist) contains
        or is close to the given point — used to snap arrow/line endpoints
        to the shapes they were drawn to touch."""
        best_id, best_d = None, max_dist
        px, py = point
        for el in node_els:
            x1, y1, x2, y2 = bbox_of(el)
            dx = max(x1 - px, 0, px - x2)
            dy = max(y1 - py, 0, py - y2)
            d = math.hypot(dx, dy)
            if d < best_d:
                best_id, best_d = el["id"], d
        return best_id

    # ── Summary heuristics ────────────────────────────────────────────

    def _guess_drawing_type(self, elements: list, connections: list) -> str:
        if not elements:
            return "unknown"
        types = {e["type"] for e in elements}
        if connections and ("diamond" in types or "rectangle" in types):
            return "flowchart"
        if len(elements) == 1:
            return "shapes"
        if connections:
            return "diagram"
        return "shapes"

    def _suggestions(self, elements: list, connections: list) -> list:
        tips = []
        if not elements:
            return ["Try drawing a clear, closed shape", "Use distinct, deliberate strokes"]
        if len(elements) > 1 and not connections:
            tips.append("Draw a line or arrow tool between shapes to link them")
        if any(e["type"] == "rectangle" and e.get("style") == "sketch" for e in elements):
            tips.append("Close your freehand shapes fully for more reliable recognition")
        tips.append("Switch to Cloud mode for messier or more complex sketches")
        return tips[:4]

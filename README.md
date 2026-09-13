# FinDrawAI

**AI-Powered Intelligent Whiteboard** — draw rough sketches and let AI recognise and clean them up.

Works **completely free, out of the box, with no API key** using the built-in
Local recognizer. An optional Cloud (Claude) mode is available if you add
your own `ANTHROPIC_API_KEY` for stronger recognition on messy sketches.

---

## Features

- **Two AI engines, switchable anytime, in the header:**
  - 🆓 **Free (Local)** — default. An offline, geometry-based recognizer
    (`local_engine.py`) that reads the exact shapes you drew (or classifies
    freehand strokes by their geometry) and needs **zero setup, zero cost,
    zero internet**.
  - ☁ **Cloud (Claude)** — optional. Sends a screenshot of the canvas to the
    Claude API (`ai_engine.py`) for more flexible recognition of messy or
    complex sketches. Requires your own `ANTHROPIC_API_KEY`.
- **Freehand drawing** with smooth strokes
- **Shape tools** — rectangle, circle, triangle, diamond, star, line, arrow, text
- **Select / Move / Delete tool** — click a shape to select it, drag to move,
  `Delete` to remove
- **Fill toggle** — outline-only or filled shapes
- **Zoom** — `Ctrl` + scroll, `+` / `-`, or `0` to reset
- **Toggleable grid**
- **Eraser** with adjustable size
- **Undo / Redo** (unlimited, `Ctrl+Z` / `Ctrl+Y`)
- **AI Recognition** — structured JSON output (elements + connections) from
  whichever engine is active
- **AI Cleanup** — renders the recognised clean shapes over your rough sketch
- **Export** — PNG and AI-diagram JSON
- **Save / Open whole projects** (`.json`) — reopen and keep editing later

---

## Architecture

```
FinDrawAI/
├── main.py           # UI, canvas, tools, AI panel, export
│   ├── DrawingManager      — undo/redo snapshot stack (items + shape records)
│   ├── WhiteboardCanvas    — Tkinter canvas + drawing/select/zoom/grid engine
│   ├── ExportManager       — PNG / JSON export + project save/open
│   ├── AIAnalysisPanel     — right sidebar with results (shows active engine)
│   └── FinDrawApp          — root Tk window + layout
│
├── ai_engine.py      # Optional Cloud engine — Claude API integration
│   └── AIEngine            — prompt, request, parse, validate
│
├── local_engine.py   # Default Free engine — no API key required
│   └── LocalEngine         — geometry heuristics, offline, instant
│
├── requirements.txt
├── .env.example       # only needed if you want to use Cloud mode
├── .gitignore
└── README.md
```

---

## Installation

```bash
git clone <repository-url>
cd FinDrawAI

python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

---

## Running

```bash
python main.py
```

The app opens in **Free mode** by default — draw and click **✨ Recognize**
right away, no configuration needed.

---

## (Optional) Cloud Mode API Key Setup

Only needed if you want to switch to ☁ Cloud mode for tougher sketches:

1. Get your key from https://console.anthropic.com
2. Copy `.env.example` → `.env`
3. Add your key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

4. Click **☁ Cloud** in the header to switch engines.

> Note: Anthropic doesn't provide a shared/free API key that can be baked
> into an app — each Cloud user needs their own key from the console link
> above. That's exactly why Free (Local) mode exists: it gives you real,
> useful recognition with no key and no cost, and Cloud is there as an
> optional upgrade.

---

## Usage

1. **Select a tool** from the left toolbar (or press its keyboard shortcut).
2. **Draw** on the white canvas area.
3. Click **✨ Recognize** in the header — uses whichever engine (🆓 Free /
   ☁ Cloud) is currently selected.
4. View the **AI Analysis** panel on the right for results.
5. Click **✨ Apply AI Cleanup** to render the clean version.
6. Click **🖼 Export** to save PNG / JSON, or **💾 Save** a full project.

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `V` | Select / Move |
| `P` | Pen |
| `E` | Eraser |
| `R` | Rectangle |
| `C` | Circle |
| `Y` | Triangle |
| `D` | Diamond |
| `L` | Line |
| `A` | Arrow |
| `K` | Star |
| `T` | Text |
| `F` | Toggle fill |
| `G` | Toggle grid |
| `+` / `-` / `0` | Zoom in / out / reset |
| `Delete` | Delete selected shape |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Ctrl+S` | Export PNG |
| `Ctrl+Shift+S` | Save project |
| `Ctrl+O` | Open project |

---

## Recognised Drawing Types

- Basic shapes: circle, ellipse, rectangle, diamond, triangle, star, pentagon, hexagon
- Flowchart elements: nodes, decision diamonds, arrows/connections
- System diagrams: boxes, cylinders (databases), arrows *(Cloud mode)*
- Labels and text blocks
- Mixed diagrams

---

## How Free (Local) mode works

Every shape you draw with a tool (rectangle, circle, etc.) is already known
exactly — no guessing needed. For **freehand** pen strokes, the local
engine:

1. Simplifies the stroke's path (Douglas–Peucker) to count corners.
2. Checks whether the stroke is closed and how "round" it is.
3. Classifies it as a circle/ellipse, triangle, rectangle, pentagon,
   hexagon, or a generic sketch shape based on those measurements.
4. Snaps nearby text to the closest shape as its label, and snaps
   line/arrow endpoints to nearby shapes to build connections.

It's simple, explainable geometry — not a neural network — so very messy
or ambiguous sketches are better served by Cloud mode. But for clean
flowcharts, wireframes, and basic diagrams it works well with **no API
key at all**.

---

## Limitations

- Cloud recognition requires internet access and your own valid API key.
- Free (Local) mode classifies freehand strokes with geometry heuristics,
  not a trained model — very messy or ambiguous sketches may be missed.
- The canvas PNG capture (Cloud mode) uses a screen grab — virtual/remote
  desktops may need adjustment.
- Auto-Recognize mode is not included; recognition is on-demand only.

---

## Future Improvements

- Real-time collaborative sessions via WebSocket
- Auto-Recognize with debounce timer
- Layer system
- SVG export
- Template library (flowchart, UML, ERD)

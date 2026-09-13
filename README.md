<div align="center">

# 🎨 FinDrawAI

### AI-Powered Intelligent Whiteboard

**Draw naturally. Let AI understand your sketch. Transform rough ideas into clean, structured diagrams.**

<br>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/UI-Tkinter-FF6F00?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![AI](https://img.shields.io/badge/AI-Computer%20Vision-8B5CF6?style=for-the-badge)](#-ai-engines)
[![Claude](https://img.shields.io/badge/Cloud-Claude-D97706?style=for-the-badge)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

<br>

**A lightweight desktop whiteboard designed for developers, students, designers, architects, and anyone who thinks visually.**

</div>

---

## ✨ Overview

**FinDrawAI** is an intelligent desktop whiteboard that allows you to sketch diagrams, flowcharts, system architectures, wireframes, and ideas naturally.

Instead of manually recreating your rough drawing, FinDrawAI can **recognize the drawing, understand its structure, and generate a cleaner representation**.

The application provides two recognition engines:

* 🆓 **Free Local Engine** — completely offline, free, and requires no API key.
* ☁️ **Cloud Claude Engine** — optional AI-powered recognition for more complex and messy sketches.

This makes FinDrawAI useful both as a **zero-configuration offline tool** and as an **AI-enhanced diagramming application**.

---

## 🚀 Why FinDrawAI?

Traditional diagramming tools often require users to manually create every shape and connection.

FinDrawAI takes a different approach:

```text
        ✏️ Your Rough Sketch
                 │
                 ▼
        ┌─────────────────┐
        │   FinDrawAI     │
        │  AI Recognition │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
   🆓 Local Engine   ☁️ Claude AI
        │                 │
        └────────┬────────┘
                 ▼
       🧠 Structured Result
                 │
                 ▼
        ✨ Clean Diagram
                 │
          ┌──────┴──────┐
          ▼             ▼
        PNG            JSON
```

---

# 🌟 Features

## 🎨 Powerful Drawing Tools

Create diagrams directly on the interactive canvas.

* ✏️ Freehand Pen
* ▭ Rectangle
* ⚪ Circle / Ellipse
* 🔺 Triangle
* ◆ Diamond
* ⭐ Star
* ⬡ Polygon shapes
* ➖ Line
* ➡️ Arrow
* 🔤 Text
* 🖱️ Select / Move
* 🧹 Eraser

---

## 🤖 Dual AI Recognition

FinDrawAI supports two recognition modes.

### 🆓 Free Local Mode

The default engine requires:

* ❌ No API key
* ❌ No internet connection
* ❌ No cloud service
* ❌ No subscription
* ✅ Completely free
* ✅ Instant recognition

The local engine uses **geometry-based recognition** rather than a neural network.

It analyzes characteristics such as:

* Stroke paths
* Corners
* Shape closure
* Roundness
* Polygon structure
* Proximity between objects
* Text placement
* Connections between shapes

This makes the local engine particularly useful for clean diagrams, flowcharts, wireframes, and basic shapes.

---

### ☁️ Cloud Claude Mode

For more complicated or messy sketches, FinDrawAI can optionally use the **Claude API**.

Cloud mode can provide more flexible recognition for:

* Messy sketches
* Complex diagrams
* System architecture
* Mixed visual elements
* Flowcharts
* Hand-drawn concepts

Cloud mode requires your own:

```env
ANTHROPIC_API_KEY=your_api_key
```

Your API key is never included in the project.

---

# 🧠 AI Recognition Pipeline

FinDrawAI transforms a rough drawing into structured information.

```text
Drawing
   │
   ▼
Canvas Capture
   │
   ▼
Recognition Engine
   │
   ├───────────────┐
   ▼               ▼
Local Engine    Claude API
   │               │
   └───────┬───────┘
           ▼
    Structured JSON
           │
           ▼
      AI Analysis
           │
           ▼
    Cleaned Diagram
```

The application can identify elements such as:

* Circles
* Ellipses
* Rectangles
* Diamonds
* Triangles
* Stars
* Polygons
* Nodes
* Arrows
* Connections
* Labels
* Text blocks
* Database-style cylinders
* Mixed diagrams

---

# ✨ AI Cleanup

Recognition is only the beginning.

After FinDrawAI understands your drawing, you can use:

### `✨ Apply AI Cleanup`

to render a cleaner representation of the recognized diagram.

This makes rough ideas easier to understand and present.

---

# 🖼️ Screenshots

## Main Application

> Screenshots below are loaded directly from the repository's `Screenshots` directory.

<div align="center">

<img src="./Screenshots/1.png" width="48%" alt="FinDrawAI Main Interface">
<img src="./Screenshots/2.png" width="48%" alt="FinDrawAI Whiteboard">

</div>

<br>

## ✏️ Drawing & Diagram Creation

<div align="center">

<img src="./Screenshots/3.png" width="48%" alt="Drawing Tools">
<img src="./Screenshots/4.png" width="48%" alt="Diagram Creation">

</div>

<br>

## 🤖 AI Recognition

<div align="center">

<img src="./Screenshots/5.png" width="48%" alt="AI Recognition">
<img src="./Screenshots/6.png" width="48%" alt="AI Analysis">

</div>

<br>

## ✨ AI Cleanup

<div align="center">

<img src="./Screenshots/7.png" width="48%" alt="AI Cleanup">
<img src="./Screenshots/8.png" width="48%" alt="Clean Diagram">

</div>

<br>

## 📤 Export & Project Management

<div align="center">

<img src="./Screenshots/9.png" width="48%" alt="Export">
<img src="./Screenshots/10.png" width="48%" alt="Project Management">

</div>

> **Note:** Replace the numbered filenames above with the exact filenames in your `Screenshots` folder if they differ.

---

# 🛠️ Technology Stack

| Technology               | Purpose                          |
| ------------------------ | -------------------------------- |
| 🐍 Python                | Core application                 |
| 🖼️ Tkinter              | Desktop graphical interface      |
| 🤖 Local Geometry Engine | Offline recognition              |
| ☁️ Claude API            | Optional cloud recognition       |
| 📦 JSON                  | Structured AI results & projects |
| 🖼️ PNG                  | Diagram export                   |
| 🔐 `.env`                | API configuration                |

---

# 🏗️ Project Architecture

```text
FinDraw-AI/
│
├── 📁 Screenshots/
│   └── Application screenshots
│
├── 🐍 main.py
│   ├── DrawingManager
│   ├── WhiteboardCanvas
│   ├── ExportManager
│   ├── AIAnalysisPanel
│   └── FinDrawApp
│
├── 🤖 ai_engine.py
│   └── AIEngine
│       ├── Prompt handling
│       ├── Claude API request
│       ├── Response parsing
│       └── Validation
│
├── 🧠 local_engine.py
│   └── LocalEngine
│       ├── Geometry analysis
│       ├── Shape classification
│       ├── Text association
│       └── Connection detection
│
├── 📦 requirements.txt
├── 📜 LICENSE
└── 📖 README.md
```

---

# ⚡ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/MUdevelops/FinDraw-AI.git
```

```bash
cd FinDraw-AI
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run FinDrawAI

Start the application with:

```bash
python main.py
```

The application starts in:

### 🆓 Free Local Mode

No API key or additional configuration is required.

Simply:

```text
Launch
  ↓
Draw
  ↓
Recognize
  ↓
Analyze
  ↓
Apply Cleanup
  ↓
Export
```

---

# ☁️ Optional Cloud Mode

If you want to use Claude for more advanced recognition:

### 1. Create an environment file

Copy:

```text
.env.example
```

to:

```text
.env
```

### 2. Add your Anthropic API key

```env
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 3. Launch FinDrawAI

```bash
python main.py
```

### 4. Select

```text
☁ Cloud
```

from the application header.

> **Security:** Never commit your `.env` file or expose your API key publicly.

---

# 🎮 How to Use

### Step 1 — Select a Tool

Choose a drawing tool from the left toolbar.

### Step 2 — Draw

Create your rough diagram on the whiteboard.

### Step 3 — Recognize

Click:

```text
✨ Recognize
```

### Step 4 — Analyze

Review the results in the AI Analysis panel.

### Step 5 — Clean

Click:

```text
✨ Apply AI Cleanup
```

### Step 6 — Export

Export your work as:

* 🖼️ PNG
* 📄 AI Diagram JSON
* 💾 Full FinDraw project

---

# ⌨️ Keyboard Shortcuts

| Shortcut           | Action                |
| ------------------ | --------------------- |
| `V`                | Select / Move         |
| `P`                | Pen                   |
| `E`                | Eraser                |
| `R`                | Rectangle             |
| `C`                | Circle                |
| `Y`                | Triangle              |
| `D`                | Diamond               |
| `L`                | Line                  |
| `A`                | Arrow                 |
| `K`                | Star                  |
| `T`                | Text                  |
| `F`                | Toggle Fill           |
| `G`                | Toggle Grid           |
| `+` / `-`          | Zoom                  |
| `0`                | Reset Zoom            |
| `Delete`           | Delete Selected Shape |
| `Ctrl + Z`         | Undo                  |
| `Ctrl + Y`         | Redo                  |
| `Ctrl + S`         | Export PNG            |
| `Ctrl + Shift + S` | Save Project          |
| `Ctrl + O`         | Open Project          |

---

# 📦 Export & Persistence

FinDrawAI supports multiple ways to preserve your work.

### 🖼️ PNG Export

Export your final diagram as an image.

### 📄 AI Diagram JSON

Export structured recognition data for further processing.

### 💾 Project Files

Save the complete project and reopen it later for continued editing.

---

# 🧪 Local Recognition Technology

The local engine uses explainable geometric analysis.

For freehand drawings, the process roughly follows:

```text
Freehand Stroke
      │
      ▼
Path Simplification
      │
      ▼
Corner Detection
      │
      ▼
Closed / Open Analysis
      │
      ▼
Roundness Analysis
      │
      ▼
Shape Classification
      │
      ▼
Text & Connection Association
```

The approach uses geometric heuristics rather than a trained neural network.

This provides a major advantage:

### ⚡ No Model Download Required

The application can perform basic recognition immediately after installation.

---

# 🔐 Privacy

FinDrawAI provides an important privacy advantage through its local engine.

### Local Mode

Your drawings can remain:

```text
Your Computer
      ↓
Local Recognition
      ↓
Local Result
```

No cloud API is required.

### Cloud Mode

When using Claude:

```text
Your Drawing
      ↓
Canvas Capture
      ↓
Claude API
      ↓
Recognition Result
```

Use Cloud mode only when you are comfortable sending the relevant canvas image to the configured cloud service.

---

# ⚠️ Current Limitations

FinDrawAI is actively evolving.

Current limitations include:

* Local recognition is geometry-based.
* Extremely messy sketches may be difficult to classify.
* Cloud mode requires internet access.
* Cloud mode requires your own Anthropic API key.
* Canvas capture may require adjustment in some virtual/remote desktop environments.
* Recognition is currently triggered manually rather than continuously.

---

# 🗺️ Roadmap

Future improvements can include:

* [ ] 🔄 Real-time collaborative whiteboards
* [ ] 🌐 WebSocket collaboration
* [ ] ⚡ Automatic recognition
* [ ] 🧩 Layer management
* [ ] 🖼️ SVG export
* [ ] 📚 Diagram template library
* [ ] 📊 UML templates
* [ ] 🗄️ ERD templates
* [ ] 🔀 Advanced flowchart templates
* [ ] 🤖 Improved AI recognition
* [ ] 🎨 More customization options
* [ ] 📱 Cross-platform UI improvements

---

# 💡 Use Cases

FinDrawAI can be useful for:

### 👨‍💻 Software Developers

Create:

* System architecture
* Flowcharts
* Database diagrams
* Application workflows
* API concepts

### 🎓 Students

Create:

* Class diagrams
* Algorithms
* Flowcharts
* Project structures
* Study diagrams

### 🎨 Designers

Quickly sketch:

* Wireframes
* UI concepts
* User flows
* Product ideas

### 🧠 Creators & Researchers

Turn rough ideas into structured visual concepts.

---

# 🌟 What Makes FinDrawAI Different?

| Capability          | FinDrawAI  |
| ------------------- | ---------- |
| Free drawing        | ✅          |
| Shape tools         | ✅          |
| Offline recognition | ✅          |
| No API key required | ✅          |
| AI recognition      | ✅          |
| Claude integration  | ✅ Optional |
| AI cleanup          | ✅          |
| PNG export          | ✅          |
| JSON export         | ✅          |
| Project save/open   | ✅          |
| Undo / Redo         | ✅          |
| Zoom                | ✅          |
| Grid                | ✅          |

---

# 🤝 Contributing

Contributions are welcome.

```bash
# Fork the project

# Create a feature branch
git checkout -b feature/amazing-feature

# Commit your changes
git commit -m "Add amazing feature"

# Push the branch
git push origin feature/amazing-feature
```

Then open a Pull Request.

Ideas for contributions include:

* New recognition algorithms
* Additional drawing tools
* Better shape detection
* UI improvements
* Export formats
* Templates
* Performance improvements
* Cross-platform improvements

---

# 📄 License

FinDrawAI is released under the **MIT License**.

See [`LICENSE`](LICENSE) for details.

---

# 👨‍💻 Author

<div align="center">

### Muhammad Umar Jamal

**Software Developer • AI Enthusiast • Full-Stack Developer**

Building practical software, AI-powered tools, and developer-focused projects.

<br>

[![GitHub](https://img.shields.io/badge/GitHub-MUdevelops-181717?style=for-the-badge\&logo=github)](https://github.com/MUdevelops)

[![Portfolio](https://img.shields.io/badge/Portfolio-m--umar--jamal.netlify.app-00C7B7?style=for-the-badge\&logo=netlify\&logoColor=white)](https://m-umar-jamal.netlify.app/)

</div>

---

<div align="center">

## ⭐ If FinDrawAI helped you, consider giving the repository a star!

### 🎨 Draw → 🤖 Recognize → ✨ Clean → 📤 Export

**FinDrawAI — Turn rough ideas into intelligent diagrams.**

<br>

Made with ❤️ and Python

</div>

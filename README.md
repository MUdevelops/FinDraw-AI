<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=200&section=header&text=FinDrawAI&fontSize=60&fontColor=FFFFFF&animation=fadeIn&gradientColor=6,11,20,24,30" width="100%"/>

<br>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&duration=2800&pause=900&color=8B5CF6&center=true&vCenter=true&width=750&lines=AI-Powered+Intelligent+Drawing;Smart+Shape+Recognition;Draw+%E2%86%92+Detect+%E2%86%92+Refine;Built+with+Python+%26+Tkinter" alt="Typing Animation"/>

</div>


<br><br>

<a href="https://github.com/MUdevelops/FinDraw-AI">
<img src="https://img.shields.io/badge/GitHub-MUdevelops%2FFinDraw--AI-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>

<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Tkinter-Desktop%20GUI-FF6F00?style=for-the-badge"/>
<img src="https://img.shields.io/badge/AI-Shape%20Recognition-8B5CF6?style=for-the-badge"/>
<img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge"/>

<br><br>

### 🎨 Draw. Detect. Understand.

**FinDrawAI is an intelligent desktop whiteboard that recognizes hand-drawn geometric shapes and transforms rough sketches into structured visual elements.**

<br>

<a href="#-features">Features</a> • <a href="#-screenshots">Screenshots</a> • <a href="#-installation">Installation</a> • <a href="#-usage">Usage</a> • <a href="#-architecture">Architecture</a>

</div>

---

## 🧠 What is FinDrawAI?

**FinDrawAI** is a Python-based intelligent drawing application designed to bridge the gap between **freehand sketching** and **structured digital diagrams**.

Instead of forcing users to manually create perfect shapes, FinDrawAI allows them to simply draw.

The application analyzes the drawing and can recognize geometric forms such as:

* 🔵 Circles
* ▭ Rectangles
* ⬡ Heptagons
* ✏️ Custom freehand drawings
* 🔷 Other geometric structures

The result is a more accurate and organized representation of the user's original sketch.

---

## ✨ Core Concept

```text
              ✏️ USER DRAWING
                    │
                    ▼
          ┌───────────────────┐
          │   FinDrawAI       │
          │   Drawing Canvas  │
          └─────────┬─────────┘
                    │
                    ▼
             🔍 ANALYSIS
                    │
                    ▼
          ┌───────────────────┐
          │ Shape Detection   │
          │ & Recognition     │
          └─────────┬─────────┘
                    │
                    ▼
             🧠 AI / Logic
                    │
                    ▼
          ┌───────────────────┐
          │ Structured Shape  │
          │ / Clean Drawing   │
          └───────────────────┘
```

> **Your hand doesn't have to be perfect. FinDrawAI does the understanding.**

---

# 🚀 Features

<div align="center">

|    🎨 Drawing    |   🧠 Recognition   |       ⚡ Accuracy      |
| :--------------: | :----------------: | :-------------------: |
| Freehand Drawing |   Shape Detection  |   Accurate Geometry   |
|   Custom Shapes  | Circle Recognition | Rectangle Recognition |
|  Multiple Tools  |  Polygon Detection |    Clean Rendering    |

</div>

---

## 🎨 Freehand Drawing

FinDrawAI provides a flexible drawing canvas where users can freely sketch their ideas.

You can create:

* Freehand shapes
* Rough diagrams
* Custom drawings
* Geometric sketches
* Experimental designs

The application doesn't force you to create mathematically perfect shapes.

---

## 🧠 Intelligent Shape Detection

One of FinDrawAI's primary capabilities is detecting shapes from user drawings.

For example:

```text
        Rough Drawing
             │
             ▼
      ┌─────────────┐
      │ Shape Input │
      └──────┬──────┘
             │
             ▼
       Shape Analysis
             │
      ┌──────┼──────┐
      ▼      ▼      ▼
    Circle Rectangle Polygon
      │      │      │
      └──────┼──────┘
             ▼
       Detected Shape
```

This allows a user to draw naturally while the application interprets the geometry.

---

# 🔵 Circle Recognition

FinDrawAI can recognize freehand circles and reproduce them accurately.

### Workflow

```text
✏️ Freehand Circle
        ↓
🔍 Analyze Stroke
        ↓
⭕ Detect Circular Geometry
        ↓
✨ Accurate Circle
```

This is particularly useful when users need quick geometric diagrams without manually constructing perfect circles.

---

# ▭ Rectangle Recognition

Users can sketch a rough rectangle and allow FinDrawAI to identify the intended geometry.

```text
Rough Rectangle
      ↓
Stroke Analysis
      ↓
Corner Detection
      ↓
Rectangle Classification
      ↓
Accurate Rectangle
```

---

# ⬡ Heptagon Recognition

FinDrawAI also demonstrates polygon recognition through **heptagon detection**.

A rough polygon can be analyzed and converted into a cleaner geometric representation.

```text
       Rough Heptagon
             ↓
      Geometry Analysis
             ↓
       Vertex Detection
             ↓
      Polygon Recognition
             ↓
        ⬡ Heptagon
```

---

# 🖼️ Screenshots

## 🖥️ Main Dashboard

The central workspace where users interact with FinDrawAI and create their drawings.

<div align="center">

<img src="./Screenshots/Main%20Dashboard.png" width="90%" alt="FinDrawAI Main Dashboard"/>

<br>

### Main Dashboard

*The primary FinDrawAI drawing workspace.*

</div>

---

## 🎨 Custom Drawings

FinDrawAI supports custom freehand drawings, allowing users to experiment beyond predefined geometric shapes.

<div align="center">

<img src="./Screenshots/Custom%20Drawings.png" width="85%" alt="FinDrawAI Custom Drawings"/>

<br>

### Custom Drawings

*Freehand drawing and custom visual creation.*

</div>

---

# ⬡ Heptagon Recognition

## ✏️ Freehand Heptagon

A rough heptagon can be drawn freely on the canvas.

<div align="center">

<img src="./Screenshots/Freedraw%20Aptagon.png" width="75%" alt="FinDrawAI Freehand Heptagon"/>

<br>

### Freehand Heptagon

*Rough polygon drawn naturally by the user.*

</div>

---

## 🧠 Detected Heptagon

FinDrawAI analyzes the drawing and detects the intended heptagonal geometry.

<div align="center">

<img src="./Screenshots/Detect%20and%20Draw%20Aptagon%20Shape.png" width="75%" alt="FinDrawAI Detected Heptagon"/>

<br>

### Detected & Drawn Heptagon

*Shape recognition converts the rough drawing into a detected geometric form.*

</div>

---

# 🔵 Circle Recognition

## ✏️ Freestyle Circle

Users can draw circles naturally without worrying about perfect geometry.

<div align="center">

<img src="./Screenshots/Freestyle%20Circle.png" width="75%" alt="FinDrawAI Freestyle Circle"/>

<br>

### Freestyle Circle

*Freehand circular drawing.*

</div>

---

## 🎯 Accurate Circle Detection

FinDrawAI analyzes the freestyle circle and produces a more accurate circular representation.

<div align="center">

<img src="./Screenshots/Detect%20and%20Draw%20Circle%20Accurately.png" width="75%" alt="FinDrawAI Accurate Circle Detection"/>

<br>

### Detect & Draw Circle Accurately

*Recognized circular geometry rendered accurately.*

</div>

---

# ▭ Rectangle Recognition

## ✏️ Freehand Rectangle

Draw a rectangle naturally using the canvas.

<div align="center">

<img src="./Screenshots/Freedraw%20Rectangle.png" width="75%" alt="FinDrawAI Freehand Rectangle"/>

<br>

### Freehand Rectangle

*Rough rectangle drawn by hand.*

</div>

---

## 🎯 Accurate Rectangle Detection

The application analyzes the stroke and reconstructs the intended rectangle.

<div align="center">

<img src="./Screenshots/Detect%20and%20Draw%20Rectangle%20Accurately.png" width="75%" alt="FinDrawAI Accurate Rectangle Detection"/>

<br>

### Detect & Draw Rectangle Accurately

*Recognized rectangle rendered with cleaner geometry.*

</div>

---

# ⚙️ How FinDrawAI Works

The application follows a simple but powerful pipeline:

```text
             👤 USER
                │
                ▼
        ✏️ Draw on Canvas
                │
                ▼
        📍 Capture Stroke
                │
                ▼
       🔍 Analyze Geometry
                │
        ┌───────┴────────┐
        │                │
        ▼                ▼
   Freehand Data     Shape Analysis
        │                │
        └───────┬────────┘
                ▼
        🧠 Recognition
                │
                ▼
       🎯 Identify Shape
                │
                ▼
        ✨ Clean Rendering
                │
                ▼
          📐 Final Shape
```

---

# 🏗️ Architecture

```text
FinDraw-AI/
│
├── 📄 main.py
│
├── 🧠 ai_engine.py
│
├── ⚙️ local_engine.py
│
├── 📦 requirements.txt
│
├── 📁 Screenshots/
│   ├── Main Dashboard.png
│   ├── Custom Drawings.png
│   ├── Freedraw Aptagon.png
│   ├── Detect and Draw Aptagon Shape.png
│   ├── Freestyle Circle.png
│   ├── Detect and Draw Circle Accurately.png
│   ├── Freedraw Rectangle.png
│   └── Detect and Draw Rectangle Accurately.png
│
├── 📜 LICENSE
│
└── 📖 README.md
```

---

# 🛠️ Technology Stack

<div align="center">

| Technology                    | Role                        |
| :---------------------------- | :-------------------------- |
| 🐍 **Python**                 | Application logic           |
| 🖼️ **Tkinter**               | Desktop graphical interface |
| 🧠 **Shape Recognition**      | Geometric interpretation    |
| 📐 **Geometry Processing**    | Shape analysis              |
| 📦 **JSON / Data Structures** | Internal representation     |

</div>

---

# ⚡ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/MUdevelops/FinDraw-AI.git
```

```bash
cd FinDraw-AI
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv
```

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Run the Application

Launch FinDrawAI using:

```bash
python main.py
```

Once launched:

```text
        🚀 Start Application
                ↓
        🖥️ Open Dashboard
                ↓
        ✏️ Draw Something
                ↓
        🔍 Detect Shape
                ↓
        ✨ Generate Accurate Shape
```

---

# 🎮 Usage

### Step 1 — Open FinDrawAI

Launch the application.

### Step 2 — Draw

Use the canvas to create a freehand shape.

### Step 3 — Analyze

Allow FinDrawAI to inspect the drawing.

### Step 4 — Detect

The application determines the most likely geometric shape.

### Step 5 — Render

FinDrawAI produces the recognized/clean representation.

---

# 💡 Example

Suppose you draw this rough shape:

```text
       ╭──────────╮
      /            \
     │              │
      \            /
       ╰──────────╯
```

FinDrawAI analyzes the geometry and determines the intended structure.

The goal is:

```text
       ROUGH
         │
         ▼
    🔍 ANALYSIS
         │
         ▼
      🧠 DETECT
         │
         ▼
      ✨ CLEAN
```

---

# 🎯 Design Philosophy

FinDrawAI follows a simple principle:

> ### **Don't make the user draw perfectly. Make the software understand imperfect drawings.**

The project focuses on making geometric drawing more natural and accessible.

Instead of:

```text
Perfect Input
     ↓
Perfect Output
```

FinDrawAI aims for:

```text
Natural Input
     ↓
Intelligent Interpretation
     ↓
Clean Output
```

---

# 🚀 Future Roadmap

Potential future improvements include:

* [ ] 🤖 Advanced AI-powered recognition
* [ ] 🔺 More geometric shapes
* [ ] 🧩 Multi-shape diagrams
* [ ] 🔗 Automatic connection detection
* [ ] 📝 Text recognition
* [ ] 📐 Smart alignment
* [ ] 🎨 Advanced styling
* [ ] 📤 SVG export
* [ ] 📄 PDF export
* [ ] 💾 Project persistence
* [ ] ↩️ Advanced undo/redo
* [ ] 🖥️ Improved desktop UI
* [ ] 🌐 Web version
* [ ] 📱 Cross-platform support

---

# 🤝 Contributing

Contributions, ideas, and improvements are welcome.

```bash
# Fork the repository

# Create a feature branch
git checkout -b feature/new-feature

# Make your changes

# Commit
git commit -m "Add new feature"

# Push
git push origin feature/new-feature
```

Then open a Pull Request.

---

# 📄 License

This project is released under the **MIT License**.

See the [`LICENSE`](LICENSE) file for more information.

---

# 👨‍💻 Author

<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=20&duration=2500&pause=1000&color=7C3AED&center=true&vCenter=true&width=600&lines=Built+by+Muhammad+Umar+Jamal;Software+Developer;AI+%26+Automation+Enthusiast;Building+Real+Working+Software" />

<br><br>

### Muhammad Umar Jamal

**Software Developer • AI Enthusiast • Builder**

<br>

<a href="https://github.com/MUdevelops">
<img src="https://img.shields.io/badge/GitHub-MUdevelops-181717?style=for-the-badge&logo=github"/>
</a>

<a href="https://m-umar-jamal.netlify.app/">
<img src="https://img.shields.io/badge/Portfolio-Visit-00C7B7?style=for-the-badge&logo=netlify&logoColor=white"/>
</a>

</div>

---

<div align="center">

### ⭐ If you like FinDrawAI, consider giving the repository a star!

<br>

**✏️ Draw → 🔍 Detect → 🧠 Understand → ✨ Refine**

<br>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20,24,30&height=120&section=footer&animation=fadeIn" width="100%"/>

</div>

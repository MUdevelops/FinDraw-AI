"""
ai_engine.py — FinDrawAI Claude API Engine
All Claude API communication, prompt engineering, and response parsing.
"""

import base64
import json
import os
import time
from io import BytesIO
from typing import Optional

import anthropic
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

RECOGNITION_SYSTEM_PROMPT = """You are FinDrawAI, an intelligent visual diagram and shape recognition engine.

Your task is to analyze whiteboard drawings and identify what the user intended to draw, then describe clean renderable versions.

ANALYSIS RULES:
- Infer intent, not just pixels. A rough circle with a tail is likely an arrow with a circle head.
- Ignore visual noise, stray marks, and shakiness — focus on the intended structure.
- If you see multiple shapes, identify all of them and their relationships.
- Recognize flowcharts, system diagrams, UI wireframes, basic shapes, and mathematical figures.
- If confidence is below 0.5, mark success as false and explain why.

RESPONSE FORMAT — return ONLY valid JSON, no markdown, no preamble:

{
  "success": true,
  "drawing_type": "flowchart",
  "confidence": 0.94,
  "description": "A simple two-step authentication flowchart",
  "elements": [
    {
      "id": 0,
      "type": "rectangle",
      "label": "Login",
      "x": 200,
      "y": 100,
      "width": 160,
      "height": 60,
      "style": "rounded"
    },
    {
      "id": 1,
      "type": "diamond",
      "label": "Valid?",
      "x": 200,
      "y": 240,
      "width": 160,
      "height": 80
    },
    {
      "id": 2,
      "type": "circle",
      "label": "",
      "cx": 300,
      "cy": 150,
      "rx": 60,
      "ry": 60
    }
  ],
  "connections": [
    {
      "from": 0,
      "to": 1,
      "type": "arrow",
      "label": ""
    }
  ],
  "suggestions": [
    "Align nodes vertically",
    "Standardize box sizes",
    "Add start/end nodes"
  ]
}

ELEMENT TYPES supported: rectangle, rounded_rectangle, circle, ellipse, diamond, triangle, pentagon, hexagon, star, line, arrow, text, cylinder, parallelogram

DRAWING TYPES supported: flowchart, shapes, diagram, wireframe, network_diagram, math_figure, system_architecture, mixed, unknown

If the canvas appears empty or contains only scribbles with no recognizable intent:
{
  "success": false,
  "drawing_type": "unknown",
  "confidence": 0.0,
  "description": "Could not identify a clear drawing. Please draw something more defined.",
  "elements": [],
  "connections": [],
  "suggestions": ["Try drawing a clear shape or diagram", "Use distinct strokes"]
}

Never invent elements that are not reasonably present. Never return anything except valid JSON."""


class AIEngine:
    """Handles all Claude API interactions for FinDrawAI."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.client: Optional[anthropic.Anthropic] = None
        self.model = "claude-sonnet-5"
        self.last_result: Optional[dict] = None
        self.connected = False
        self._init_client()

    def _init_client(self):
        """Initialize the Anthropic client if API key is available."""
        if not self.api_key:
            self.connected = False
            return
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.connected = True
        except Exception:
            self.client = None
            self.connected = False

    def is_connected(self) -> bool:
        return self.connected and bool(self.api_key) and self.client is not None

    def get_status(self) -> dict:
        if not self.api_key:
            return {"status": "no_key", "message": "API key not configured"}
        if not self.connected:
            return {"status": "error", "message": "Failed to initialize client"}
        return {"status": "ready", "message": "AI Ready"}

    def _pil_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string."""
        # Resize if too large to keep API costs down
        max_dim = 1200
        w, h = image.size
        if w > max_dim or h > max_dim:
            ratio = min(max_dim / w, max_dim / h)
            image = image.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.standard_b64encode(buffer.read()).decode("utf-8")

    def _validate_element(self, el: dict) -> dict:
        """Ensure required fields exist on an element with safe defaults."""
        el.setdefault("id", 0)
        el.setdefault("type", "rectangle")
        el.setdefault("label", "")
        el.setdefault("x", 100)
        el.setdefault("y", 100)
        el.setdefault("width", 120)
        el.setdefault("height", 60)
        el.setdefault("style", "normal")
        # circle/ellipse use cx/cy/rx/ry — fill from x/y/width/height if absent
        if el["type"] in ("circle", "ellipse"):
            el.setdefault("cx", el["x"] + el["width"] // 2)
            el.setdefault("cy", el["y"] + el["height"] // 2)
            el.setdefault("rx", el["width"] // 2)
            el.setdefault("ry", el["height"] // 2)
        return el

    def _validate_connection(self, conn: dict, num_elements: int) -> Optional[dict]:
        """Validate a connection dict; return None if invalid."""
        try:
            frm = int(conn.get("from", -1))
            to = int(conn.get("to", -1))
            if frm < 0 or to < 0 or frm >= num_elements or to >= num_elements:
                return None
            return {
                "from": frm,
                "to": to,
                "type": conn.get("type", "arrow"),
                "label": conn.get("label", ""),
            }
        except (ValueError, TypeError):
            return None

    def _parse_response(self, raw_text: str) -> dict:
        """Parse and validate Claude's JSON response."""
        # Strip any accidental markdown fences
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            text = "\n".join(
                l for l in lines if not l.strip().startswith("```")
            ).strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "drawing_type": "unknown",
                "confidence": 0.0,
                "description": f"AI returned unparseable response: {e}",
                "elements": [],
                "connections": [],
                "suggestions": [],
                "raw": raw_text,
            }

        # Normalise
        elements = [self._validate_element(el) for el in data.get("elements", [])]
        connections = [
            c
            for c in (
                self._validate_connection(conn, len(elements))
                for conn in data.get("connections", [])
            )
            if c is not None
        ]

        return {
            "success": bool(data.get("success", True)),
            "drawing_type": str(data.get("drawing_type", "unknown")),
            "confidence": float(data.get("confidence", 0.0)),
            "description": str(data.get("description", "")),
            "elements": elements,
            "connections": connections,
            "suggestions": list(data.get("suggestions", [])),
        }

    def recognize(self, image: Image.Image, timeout: int = 30) -> dict:
        """
        Send a canvas image to Claude and return structured recognition data.

        Args:
            image: PIL Image of the whiteboard canvas.
            timeout: Request timeout in seconds (not directly supported by SDK
                     but kept for interface compatibility).

        Returns:
            dict with keys: success, drawing_type, confidence, description,
                            elements, connections, suggestions, error (if any).
        """
        if not self.is_connected():
            return {
                "success": False,
                "drawing_type": "unknown",
                "confidence": 0.0,
                "description": "AI engine not connected. Check your API key.",
                "elements": [],
                "connections": [],
                "suggestions": [],
                "error": "not_connected",
            }

        b64 = self._pil_to_base64(image)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=RECOGNITION_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64,
                                },
                            },
                            {
                                "type": "text",
                                "text": (
                                    "Analyze this whiteboard drawing. "
                                    "Identify all shapes, diagram elements, labels, and connections. "
                                    "Return ONLY valid JSON following the schema in your instructions."
                                ),
                            },
                        ],
                    }
                ],
            )

            raw = ""
            for block in response.content:
                if hasattr(block, "text"):
                    raw += block.text

            result = self._parse_response(raw)
            self.last_result = result
            return result

        except anthropic.AuthenticationError:
            return self._error_result("Invalid API key. Please check your .env file.", "auth_error")
        except anthropic.RateLimitError:
            return self._error_result("Rate limit reached. Please wait a moment and try again.", "rate_limit")
        except anthropic.APIConnectionError:
            return self._error_result("Cannot reach Anthropic API. Check your internet connection.", "connection_error")
        except anthropic.APIStatusError as e:
            return self._error_result(f"API error {e.status_code}: {e.message}", "api_error")
        except Exception as e:
            return self._error_result(f"Unexpected error: {str(e)}", "unknown_error")

    def _error_result(self, description: str, error_code: str) -> dict:
        return {
            "success": False,
            "drawing_type": "unknown",
            "confidence": 0.0,
            "description": description,
            "elements": [],
            "connections": [],
            "suggestions": [],
            "error": error_code,
        }

    def get_confidence_label(self, confidence: float) -> str:
        if confidence >= 0.85:
            return "High"
        if confidence >= 0.60:
            return "Medium"
        if confidence >= 0.35:
            return "Low"
        return "Very Low"

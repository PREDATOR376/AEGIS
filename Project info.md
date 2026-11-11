# AEGIS — Project Info (Context-Optimized Reference)

> **Last updated:** 2026-10-09 | **Status:** Pre-development (documentation complete, no code written)

---

## 1. What Is AEGIS?

**AEGIS (AI Gameplay Intelligence System)** — a **non-invasive, game-agnostic** real-time tactical assistant. It **watches** the game screen via screen capture, extracts structured state via CV/OCR, reasons over it, and delivers contextual guidance through a transparent overlay. It **never** touches game memory, injects code, or hooks rendering.

- **Initial target game:** GTA V (PC, 1080p, single-player)
- **Target hardware floor:** i5-10300H / Ryzen 5 4600H, GTX 1650 4GB, 16GB DDR4, Win10/11
- **Academic context:** MIT School of Computing PBL, Group TYAIEC102 ("Trailblazers"), Guide: Dr. Tushar Mote, Sem-5 AY 2026-27

---

## 2. Architecture (3-Process Model)

```
PROCESS 1: Capture & Telemetry Engine
  ├─ dxcam (DXGI Desktop Duplication, 30 FPS target)
  ├─ Frame Slicing → ROIs: Minimap 320×320, Health/Armor 220×20, Objective 420×50
  ├─ Deterministic CV: Vectorized HSV thresholding (health %, armor %, wanted stars)
  ├─ Object Detection: YOLOv11n ONNX via DirectML (minimap blips)
  └─ OCR: RapidOCR (PaddleOCR ONNX, trigger-based on text change)

    ↓ IPC: Zero-Copy SharedMemory Ring Buffer

PROCESS 2: Context Fusion & State Machine
  ├─ State hash delta check (health, threats, wanted, objective)
  ├─ Threshold gating (suppress LLM if delta below variance)
  ├─ Pre-prompt serialization → compact JSON
  ├─ PRIMARY: Groq Cloud (llama-3.1-8b-instant, 120–250ms)
  └─ FALLBACK: llama-cpp-python (Qwen2.5-1.5B-Q4_K_M, CPU-only, 2 threads)

    ↓ IPC: Thread-safe SimpleQueue (structured JSON)

PROCESS 3: Native DirectX 11 Overlay
  ├─ PyImGui + GLFW, Win32 layered transparent window
  ├─ WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOPMOST
  └─ Render pass: <1.5ms/frame, click-through, non-blocking
```

---

## 3. Resource Budgets (Hard Ceilings)

| Resource | System Total | AEGIS Budget |
|---|---|---|
| VRAM | 4096 MB | ≤ 450 MB (ONNX DirectML + DXGI) |
| System RAM | 16384 MB | ≤ 1600 MB (all subprocesses) |
| CPU | 100% (8 threads) | ≤ 14% total |
| Game FPS impact | 60 FPS baseline | ≤ 3.0 FPS delta |
| Overlay render | 16.66ms budget | ≤ 1.2ms |

---

## 4. Latency Budget (End-to-End ≤ 277.7ms)

| Stage | Budget |
|---|---|
| T_capture (DXGI pull) | ≤ 4.0ms |
| T_CV_parse (HSV 0.3 + YOLO 14 + OCR 7.5) | ≤ 22.0ms |
| T_fuse (state hash + delta) | ≤ 0.5ms |
| T_inference (Groq cloud) | ≤ 250.0ms |
| T_overlay_render | ≤ 1.2ms |

---

## 5. Key Data Schemas

### 5.1 Perception Telemetry (Process 1 → 2)
```json
{
  "timestamp_epoch_ms": int,
  "frame_id": int,
  "health_percentage": 0–100,
  "armor_percentage": 0–100,
  "wanted_level": 0–5,
  "objective_raw_text": str (max 128),
  "minimap_entities": [
    {
      "class": "enemy"|"police"|"objective_blip"|"destination",
      "norm_rel_x": -1.0–1.0,
      "norm_rel_y": -1.0–1.0,
      "confidence": 0.0–1.0
    }
  ]
}
```

### 5.2 Fused Context State (→ LLM)
```json
{
  "state_signature": "a7f3b89c",
  "player_status": { "hp": 34, "ap": 0, "status": "CRITICAL_HEALTH" },
  "tactical_environment": {
    "threat_count": 3, "police_engaged": true, "wanted_stars": 3,
    "nearest_threat_bearing_deg": 135, "nearest_threat_dist_normalized": 0.28
  },
  "mission_context": { "active_objective": "Lose the Cops" }
}
```

### 5.3 Overlay Action Payload (LLM → Overlay)
```json
{
  "alert_priority": "LOW"|"MODERATE"|"URGENT"|"FATAL",
  "directive_title": str (max 28),
  "action_instruction": str (max 80),
  "spatial_cue": {
    "screen_quadrant": "CENTER"|"BOTTOM_LEFT"|"TOP_RIGHT"|"FULL_PERIPHERY",
    "accent_color_hex": "#RRGGBB"
  },
  "ttl_seconds": 1.0–10.0
}
```

---

## 6. Tech Stack (Pinned Versions)

| Subsystem | Component | Version/Model | Exec Mode | Overhead |
|---|---|---|---|---|
| Runtime | Python | 3.11.x (64-bit) | multiprocessing (spawn) | 45MB/process |
| Capture | dxcam | ≥0.1.5 | DXGI Desktop Duplication | 2.5ms, 0% CPU |
| CV | OpenCV headless + NumPy | 4.10.x | Vectorized HSV | 0.3ms/slice |
| Detection | YOLOv11n ONNX | 2.6M params | DirectML | 120MB VRAM, 8–14ms |
| OCR | RapidOCR ONNX Mobile v4 | — | CPU 2 threads | 12–22ms |
| Cloud LLM | Groq (llama-3.1-8b) | groq-python 0.9.x | HTTP/2 stream | 120–250ms |
| Local LLM | llama-cpp-python | Qwen2.5-1.5B Q4_K_M | CPU 2 threads | 1.1GB RAM |
| Overlay | pyimgui + glfw | ImGui 1.89 | DX11 layered Win32 | 18MB, 1.0ms |
| IPC | multiprocessing | Python native | SharedMemory + Queue | 0.1ms |

---

## 7. Critical Pitfalls (Must-Know)

| # | Pitfall | Impact | Mitigation |
|---|---|---|---|
| 1 | DXGI Device Loss on Alt-Tab/resolution change | CRASH | Catch COM 0x887A0026, rebuild camera |
| 2 | BGRA→RGB color inversion | Silent detection failure | Crop ROI first in BGRA, convert sub-array only |
| 3 | Absolute pixel coords vs DPI scaling | Position desync | `SetProcessDpiAwareness(2)`, use normalized coords |
| 4 | HUD alpha blending + ambient light | False health readings | Green-over-Red/Blue channel differential |
| 5 | SharedMemory leak | System crash in 15min | Pre-allocated 2-slot ring buffer, atomic swaps |
| 6 | Windows spawn re-imports main | Infinite process spawn | `if __name__ == '__main__'` guards |
| 7 | Malformed LLM JSON | Overlay crash | `response_format=json_object` + regex fallback |
| 8 | API rate limit during combat | Dropped alerts | Leaky bucket queue + state hashing |
| 9 | Overlay steals focus | Game input loss | WS_EX_NOACTIVATE + WS_EX_TRANSPARENT |
| 10 | Alpha blending artifacts | Black boxes on overlay | DWM `DwmExtendFrameIntoClientArea` margins |

---

## 8. Environment Setup

```bash
py -3.11 -m venv aegis_env
.\aegis_env\Scripts\activate
pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0

# Use onnxruntime-directml (NOT onnxruntime-gpu) for GTX 1650 compat
# See requirements.txt for pinned versions
# .gitignore: *.onnx, *.engine, *.gguf, *.mp4, *.mkv
# Model weights tracked via DVC, not git
```

---

## 9. Sprint Plan (12-Week Semester)

| Sprint | Weeks | Focus | Success Gate |
|---|---|---|---|
| 1 | 1–2 | Capture + Overlay stub | <3ms capture, zero focus loss |
| 2 | 3–4 | Health/Armor HSV + OCR | 100% bar precision, OCR <25ms |
| 3 | 5–6 | Minimap YOLO detection | mAP@0.5 ≥90%, <15ms inference |
| 4 | 7–8 | Context fusion + Groq API | End-to-end <350ms |
| 5 | 9–10 | Local fallback + hardening | 45min soak test, flat memory |
| 6 | 11–12 | Benchmarking + user study | NASA-TLX, latency distributions |

---

## 10. Non-Negotiable Constraints

1. **ZERO game memory access** — perception is visual-only via DXGI
2. **No code injection / DLL hooking / input injection** — anti-cheat safe
3. **Privacy-preserving** — capture isolated to game window ROIs, no cloud frame upload
4. **Game-agnostic architecture** — initial target GTA V, but normalized coords + configurable ROIs
5. **Prompt injection defense** — OCR content is untrusted; separate system/user instruction channels
6. **Confidence propagation** — uncertainty flows through: Visual → State → Decision → User

# Original User Request

## 2026-10-09T17:48:31Z

# Teamwork Project Prompt — Draft

> Status: Step 9 — Assemble and Validate
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Build the AEGIS 1-day MVP: a real-time screen capture + transparent overlay system for GTA V, with a health bar extraction stretch goal.

Working directory: e:\AEGIS
Integrity mode: development

## Requirements

### R1. Environment Setup
Install Python 3.11.x if missing, create a virtual environment at `e:\AEGIS\aegis_env`, and install the required MVP dependencies (dxcam, numpy, opencv-python-headless, pyimgui[glfw], glfw, pywin32, PyOpenGL) via a `requirements.txt` file. Exclude environment and model files via `.gitignore`.

### R2. Screen Capture Module
Implement `src/capture/screen_capture.py` using `dxcam` for DXGI Desktop Duplication with device-loss recovery. It must set DPI awareness, support normalized ROI cropping, and target 30 FPS.

### R3. Transparent Overlay Module
Implement `src/overlay/overlay.py` using PyImGui + GLFW. The window must be transparent, borderless, click-through (WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOPMOST), and use DWM true alpha to avoid black box artifacts. It should display a HUD with capture latency, FPS, and an alert panel.

### R4. Health Bar Extraction
Implement `src/perception/health_extractor.py` to extract health and armor percentages from BGRA ROIs using green/blue channel differentials (not broad HSV) to handle translucent backgrounds.

### R5. Main Pipeline
Implement `src/main.py` (guarded with `if __name__ == '__main__':`) to tie capture, perception, and overlay together. It must instrument stages with `time.perf_counter_ns()` and generate a mock alert when health < 30%.

## Acceptance Criteria

### Execution & Integration
- [ ] Pipeline runs without errors and renders the transparent overlay on the desktop.
- [ ] Mouse clicks pass through the overlay to underlying windows.
- [ ] DXGI device loss (e.g., resizing) is handled gracefully without crashing.

### Perception & Unit Tests
- [ ] `tests/test_health_extractor.py` exists with synthetic BGRA tests (full, empty, half, None).
- [ ] `pytest tests/` passes all tests.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*

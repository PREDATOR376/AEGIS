# AEGIS — Handoff Document

> **Last updated:** 2026-10-09 | **Author:** Project Manager (AI)
> **Companion file:** [Project info.md](file:///e:/AEGIS/Project%20info.md)

---

## 1. Project Status Summary

| Dimension | Status |
|---|---|
| Documentation | ✅ Complete — IEEE paper, PRD, pitfalls matrix, timeline, lit review, synopsis |
| Codebase | ❌ Not started — zero code written |
| Environment | ❌ Not set up — no venv, no dependencies installed |
| Dataset | ❌ Not collected — no GTA V gameplay recordings or annotated frames |
| Models | ❌ Not trained — no YOLO minimap detector, no ONNX exports |
| Overlay | ❌ Not built — no Win32/ImGui code |
| Integration | ❌ Not started |
| Testing | ❌ Not started |

**Current phase:** Transitioning from documentation → implementation. Need to finalize MVP scope and begin Sprint 1.

---

## 2. MVP / Prototype Definition

### What constitutes a demonstrable MVP:
A working pipeline where:
1. Screen capture grabs GTA V frames in real time (<3ms)
2. Health/armor % extracted via HSV thresholding (100% accuracy on known frames)
3. At least one minimap entity class detected via YOLO
4. State change triggers LLM call (Groq cloud)
5. Overlay displays tactical text on-screen without stealing focus

### What is NOT in MVP:
- Local LLM fallback (Sprint 5)
- Cross-game generalization
- NASA-TLX user study
- Confidence propagation chain
- Adaptive spatial overlay placement

---

## 3. Goal Checklists

### 🎯 SHORT-TERM GOALS (MVP — Sprint 1–4, Weeks 1–8)

#### Sprint 1: Capture + Overlay Foundation
- [x] Set up Python 3.11 venv with pinned dependencies (including PyYAML)
- [x] Archive the prototype under `src_old/` and `tests_old/` without deleting it
- [x] Add immutable YAML configuration, SharedMemory two-slot IPC, and the three process entry points
- [x] Implement the `dxcam` capture loop with device-loss recovery and target-FPS pacing
- [x] Build the transparent PyImGui + GLFW overlay with GLFW native mouse pass-through and non-activating Win32 styles
- [x] Set DPI awareness once in the launcher before capture initialization
- [x] Add headless unit/integration tests plus opt-in `--live` GTA V smoke testing
- [ ] Validate live performance and focus behavior with GTA V in Windowed Borderless mode (requires an elevated interactive session)

#### Sprint 2: Deterministic Perception
- [ ] Record 20min GTA V gameplay at 1080p (varied conditions)
- [ ] Implement health bar HSV extraction (green channel differential, not broad HSV)
- [ ] Implement armor bar extraction
- [ ] Implement wanted stars detection
- [ ] Integrate RapidOCR on objective text ROI
- [ ] Implement SSIM/pixel-diff gating for OCR (only run when text changes)
- [ ] BGRA→RGB conversion only on sub-array (NOT full frame)
- [ ] Validate: 100% bar accuracy, OCR <25ms, handle translucent HUD backgrounds

#### Sprint 3: Minimap Object Detection
- [ ] Annotate 600+ cropped minimap frames (4 classes: police, enemy, destination, objective)
- [ ] Train YOLOv11n (100 epochs, Colab or local)
- [ ] Export to ONNX with fixed input dims
- [ ] Build ONNX Runtime inference wrapper using DirectMLExecutionProvider
- [ ] Convert detections → relative bearing + distance from minimap center
- [ ] Validate: mAP@0.5 ≥90%, inference <15ms on target GPU

#### Sprint 4: Context Fusion + Cloud Reasoning
- [ ] Build ContextFusionEngine module
- [ ] Implement state hashing (trigger on: health drop ≥20%, wanted change, new objective)
- [ ] Implement threshold gating to suppress redundant LLM calls
- [ ] Wire async Groq API worker (llama-3.1-8b-instant, JSON mode, temp 0.1)
- [ ] Implement drop-tail queue (maxsize=1) for inference requests
- [ ] JSON regex fallback parser for malformed LLM output
- [ ] Connect output queue → PyImGui overlay rendering
- [ ] Implement SharedMemory ring buffer (2 slots, atomic pointer swap)
- [ ] `if __name__ == '__main__'` guards on all entry points
- [ ] Validate: end-to-end event→overlay <350ms

### 🔭 LONG-TERM GOALS (Post-MVP — Sprint 5–6+)

- [ ] **Local LLM fallback:** llama-cpp-python + Qwen2.5-1.5B-Q4_K_M, CPU-only, auto-switch on Groq timeout (>300ms)
- [ ] **45-minute soak test:** flat memory (<50MB growth), no crashes, FPS within 3 of baseline
- [ ] **Latency profiling:** log 1,000 events, build P50/P95/P99 distributions per pipeline stage
- [ ] **NASA-TLX user study:** A/B test (5–10 participants), 3-star wanted level mission
- [ ] **Cross-game testing:** validate on a second title beyond GTA V
- [ ] **Confidence propagation:** Visual → State → Decision → User uncertainty chain
- [ ] **Adaptive overlay placement:** Fitts's law spatial cue positioning
- [ ] **Prompt injection hardening:** trusted/untrusted data separation, sanitized OCR fields
- [ ] **Zero-shot UI discovery:** VLM-based HUD region auto-detection for new games

---

## 4. Architecture Decisions Made

| Decision | Rationale | Document Source |
|---|---|---|
| 3-process architecture (capture/fusion/overlay) | Isolation prevents one subsystem crashing others; Windows spawn-safe | PRD §1.1 |
| DirectML over CUDA | GTX 1650 CUDA version conflicts; DirectML works across DX12 GPUs | Pitfalls §1.2, Timeline §1.2 |
| RapidOCR over Tesseract | Lighter, faster for ROI-cropped game text | PRD §2, IEEE §III.D |
| Groq cloud primary + local CPU fallback | Cloud is fast but unreliable under rate limits; local is slow but guaranteed | PRD §1.1, Timeline Sprint 5 |
| Green/Red channel differential for health | HUD alpha blending + environmental lighting defeats static HSV ranges | Pitfalls §2.2 |
| Event-driven inference (not continuous) | 3,600 calls/min at 60 FPS is wasteful; state-change gating targets ≤50/min | IEEE §V.A |
| Normalized coordinates everywhere | DPI scaling breaks absolute pixel coords across displays | Pitfalls §2.1 |
| Pre-allocated ring buffer for IPC | Dynamic SharedMemory allocation causes kernel handle exhaustion in ~15min | Pitfalls §3.1 |

---

## 5. Known Risks & Unsolved Problems

| # | Risk/Problem | Severity | Status | Notes |
|---|---|---|---|---|
| 1 | No GTA V gameplay dataset exists yet | HIGH | Unsolved | Must record and annotate before Sprint 2–3 |
| 2 | YOLOv11n minimap accuracy is unvalidated | HIGH | Unsolved | 90% mAP is a target, not a measurement |
| 3 | Groq rate limiting under fast combat | MEDIUM | Mitigation planned | Leaky bucket + state hash dedup |
| 4 | PyImGui + ONNX DirectML wheel compatibility on 3.11 | MEDIUM | Untested | PRD warns about 3.12 issues; 3.11 should work but verify |
| 5 | Anti-cheat response to DXGI Desktop Duplication | LOW | Acceptable risk | DXGI DD is OS-level, no memory access; but not universally guaranteed safe |
| 6 | GTA V HUD changes across updates | LOW | Accepted | Normalized coords mitigate; per-version ROI config may be needed |
| 7 | Qwen2.5-1.5B quality for tactical reasoning | MEDIUM | Deferred | Fallback quality is unknown; acceptable for MVP as "better than nothing" |
| 8 | dxcam library maintenance status | LOW | Monitor | Dependency on a small OSS project |

---

## 6. Strategy Playbook

### What worked / planned strategies:
- **"Crop first, convert later"** — avoid full-frame BGRA→RGB conversion, process only ROI sub-arrays
- **"State hash dedup"** — hash the game state, only call LLM when hash changes
- **"Drop-tail queue"** — newest state wins, old queued requests are discarded
- **"Ring buffer IPC"** — 2 fixed slots, atomic pointer swaps, no dynamic allocation
- **"DWM true alpha"** — DwmExtendFrameIntoClientArea with -1 margins for proper transparency

### What to try if stuck:
- If YOLO accuracy is low → try YOLOv12-N or fine-tune with more epochs/augmentation
- If Groq latency spikes → increase state-hash threshold to reduce call frequency
- If overlay causes stutter → profile with `time.perf_counter_ns()`, check SwapChain mode
- If SharedMemory crashes → verify `unlink()` calls, check kernel handle count
- If health detection drifts → switch from HSV to pure green-channel ratio method

---

## 7. Onboarding Checklist for Next Model/Agent

1. Read [Project info.md](file:///e:/AEGIS/Project%20info.md) first — it has all specs, schemas, and constraints
2. Check this file's §3 checklists — unchecked items are the current TODO
3. Check §5 for known risks before starting work in that area
4. **Never** write code that accesses game memory or injects input
5. **Always** use normalized coordinates, not absolute pixel positions
6. **Always** guard multiprocessing entry points with `if __name__ == '__main__'`
7. **Always** handle DXGI device loss gracefully
8. Test with static PNG fixtures before requiring GTA V to be running
9. Profile every pipeline stage with `time.perf_counter_ns()` — latency budgets are tight
10. Update this Handoff.md after completing any checklist item or encountering a new problem

---

## 8. File/Module Structure (Proposed — Not Yet Created)

```
e:\AEGIS\
├── Project info.md          # Context reference (this stays updated)
├── Handoff.md               # This file (checklists + strategy)
├── AEGIS_Combined_Documentation.md  # Full source docs
├── requirements.txt         # Pinned dependencies
├── .gitignore               # *.onnx, *.gguf, *.mp4, *.mkv
├── src/
│   ├── capture/             # Process 1: dxcam, ROI slicing
│   ├── perception/          # CV: HSV telemetry, YOLO, RapidOCR
│   ├── fusion/              # Process 2: state machine, context fusion
│   ├── reasoning/           # Groq client, llama-cpp fallback
│   ├── overlay/             # Process 3: PyImGui, Win32 setup
│   └── ipc/                 # SharedMemory ring buffer, queues
├── tests/
│   ├── fixtures/            # Static PNG frames for headless tests
│   └── test_perception_unit.py
├── models/                  # ONNX weights (gitignored, DVC tracked)
├── data/                    # Gameplay recordings, annotations
└── configs/                 # ROI coordinates, model paths, API keys
```

---

## 9. Decision Log

| Date | Decision | Decided By | Context |
|---|---|---|---|
| 2026-10-09 | Project info + Handoff docs created | AI Manager | Establish working memory for multi-model development |
| 2026-10-09 | Priority: Demo + Metrics equally | User | Every pipeline stage must have perf instrumentation from day 1 |
| 2026-10-09 | GTA V available on dev machine at 1080p | User | Live testing possible from Sprint 1 |
| 2026-10-09 | Dev GPU: RTX 5050 8GB VRAM + Ryzen 7 + 24GB RAM | User | Exceeds floor spec; develop here, target GTX 1650 as floor |
| 2026-10-09 | LLM: Groq free tier (sign up later, not blocking Sprint 1–3) | User | Free + fast; API key needed by Sprint 4 |
| 2026-10-09 | Solo developer + AI — sequential pipeline build | User | No parallel module splits; bottom-up approach |
| 2026-10-09 | 1-day MVP scope: Capture + Overlay (mock data) + stretch: health bar HSV | User | Proves hardest integration first (Win32, DXGI, focus) |
| 2026-10-09 | Overlay tech: PyImGui + GLFW (PRD spec) | User | Dear PyGui as fallback if wheel install fails |
| 2026-10-09 | GTA V display mode: Windowed Borderless | User | Most reliable for DXGI capture + overlay layering |
| 2026-10-09 | Python 3.11 not installed — must install first | User | Step 0 of execution |

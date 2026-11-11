# AEGIS — Combined Project Documentation

> Consolidated from the six supplied source documents. Content is preserved in source order. Only repeated substantive blocks that matched existing content after whitespace/punctuation normalization were removed; unique content, conflicting variants, figures, specifications, and source-specific references were retained. Tables are represented in Markdown where available.

# Source: AEGIS IEEE Research Paper

AEGIS: A Literature-Grounded Architecture for Multimodal Real-Time AI Gameplay Assistance

Prajwal Umesh Birari
Department of Computer Science and Engineering — AI & Edge Computing
MIT-ADT University, Pune, Maharashtra, India

Abstract—Real-time artificial intelligence for interactive entertainment has largely focused on autonomous agents that control or play games. AEGIS instead proposes a non-invasive gameplay assistant that observes the game display, extracts structured visual state, maintains short-term temporal context, and produces context-aware tactical recommendations for a human player. This paper consolidates a literature-grounded methodology for evaluating such a system under the computational, latency, human-computer interaction, privacy, and security constraints imposed by modern AAA games. The proposed architecture combines game-window capture, specialized HUD and minimap perception, region-of-interest OCR, temporal state fusion, event-driven inference, deterministic safety rules, and optional large-language-model reasoning. Literature reviewed in the supplied research synthesis reports reference values for object-detection accuracy, inference latency, adaptive inference frequency, and human cognitive workload; these values are used only as external benchmarks and are not claimed as measurements obtained from an AEGIS implementation. Accordingly, the paper distinguishes literature-reported results from proposed AEGIS engineering targets and identifies the experiments required for future validation. The resulting framework provides a testable basis for studying whether visual-only, privacy-preserving, game-agnostic AI assistance can operate alongside resource-intensive games without interfering with gameplay.

Keywords—gameplay assistance, multimodal AI, computer vision, vision-language models, event-driven inference, edge AI, human-computer interaction, cognitive load, game-agnostic AI, prompt injection

# I. INTRODUCTION

Artificial intelligence in games has traditionally emphasized autonomous play, reinforcement learning, or agents that directly control an environment. AEGIS follows a different interaction model: the human remains the decision maker, while an external AI system interprets the visible game state and supplies tactical information. This distinction places the problem closer to real-time human-AI augmentation than autonomous gameplay.

The central engineering challenge is that the assistant must operate concurrently with a modern game. A gameplay assistant cannot assume exclusive access to the GPU, CPU, memory bandwidth, display surface, or user attention. At the same time, the assistant must react quickly enough to be useful. A system that produces an excellent recommendation after a tactically important event has already passed provides little practical value. The AEGIS research problem is therefore a joint optimization of perception accuracy, temporal context, inference frequency, resource consumption, decision reliability, and human cognitive workload.

This paper develops a literature-grounded research framework for AEGIS. It does not report a completed experimental evaluation. Numerical values appearing in the paper are either taken from the supplied literature synthesis as reported reference values or stated as proposed AEGIS engineering targets. No number is presented as an AEGIS measurement unless an actual AEGIS experiment has been conducted and documented.

## A. Research Questions

The methodology is organized around seven research questions: RQ1 asks whether visual-only perception can reliably extract gameplay state; RQ2 asks whether temporal state fusion improves tactical recommendations; RQ3 examines whether event-driven inference can reduce computational overhead without sacrificing usefulness; RQ4 addresses concurrent operation within consumer hardware budgets; RQ5 investigates adaptive spatial assistance and cognitive workload; RQ6 compares hybrid deterministic-generative reasoning with purely generative reasoning; and RQ7 examines the potential for cross-game generalization.

# II. RELATED WORK AND RESEARCH BASIS

AEGIS draws on several research areas rather than treating gameplay assistance as a single computer-vision or LLM problem. Multimodal perception combines visual observations with structured state, while late-fusion approaches motivate separating perception from downstream reasoning [1], [2]. Real-time object detection provides a basis for recognizing small HUD elements, and recent YOLO variants emphasize efficient attention and feature extraction for latency-sensitive applications [3].

OCR is required for objective text, ammunition counts, and other textual UI elements. The supplied research synthesis compares open-source OCR systems and identifies lightweight PaddleOCR/RapidOCR-style pipelines as attractive for resource-constrained, region-of-interest processing [4]–[6]. Unlike document OCR, gameplay OCR must tolerate motion, scaling, stylized fonts, and rapidly changing backgrounds.

Temporal reasoning is motivated by the fact that a single frame can provide an incomplete description of the game. Hidden Markov models provide an efficient formalism for state estimation [7], whereas spatio-temporal transformer approaches provide richer modeling of sequential dynamics at higher computational cost [8], [9]. AEGIS therefore proposes a lightweight hybrid: deterministic state machines for safety-critical scalar values and short temporal buffers for spatial entities.

At the systems level, AEGIS relies on operating-system-level display capture and seeks to minimize synchronization and copying overhead. Direct3D 12 supports multiple command queues and asynchronous compute scenarios, making concurrent graphics and compute a relevant systems mechanism [13], [14]. Quantization and optimized inference runtimes are considered for reducing the memory cost of local generative models [16]–[19].

Finally, the design is informed by human-computer interaction and security research. Cognitive workload, visual attention, and target-acquisition principles motivate adaptive information placement [22]–[29]. Work on vision-language agents demonstrates the potential and limitations of multimodal action reasoning [30]–[32], while anti-cheat literature and current industry documentation demonstrate why an external assistant must avoid memory modification and input injection [33]–[35]. Prompt injection research further shows that visual or OCR-derived content cannot automatically be treated as trusted instructions [36], [37].

# III. AEGIS SYSTEM ARCHITECTURE

## A. Non-Invasive Perception Layer

The proposed AEGIS prototype is game-agnostic at the architectural level and is initially intended to be demonstrated on a conventional desktop game. The system does not read or write game memory, inject game code, hook the rendering pipeline, or autonomously generate controller input. Instead, the perception layer observes the game through an external capture path. DXGI Desktop Duplication is proposed for efficient acquisition of the rendered desktop surface, with region-of-interest extraction used to reduce downstream processing.

## B. Specialized Visual Perception

The visual pipeline divides the screen into semantically meaningful regions. A minimap ROI is processed by an object detector to identify icons or hostile entities; HUD regions are used for health, armor, ammunition, or status extraction; and dynamic text regions are passed to OCR when an event indicates that the content may have changed. This specialization is important because game UI elements are often small, semi-transparent, stylized, and superimposed on high-contrast scenes.

YOLO-family detectors are considered for minimap and icon detection because they provide a practical accuracy-latency trade-off. The supplied literature synthesis highlights YOLOv12 as an example of recent architectural improvements for real-time detection [3]. The exact model, dataset, and deployment configuration remain experimental choices for future AEGIS validation.

## C. Minimap-to-Tactical Representation

Detection alone does not constitute tactical understanding. AEGIS proposes converting minimap detections into structured spatial telemetry. If the player's minimap position is represented by p and an entity by e, the relative displacement can be expressed as Δ = e − p, with Euclidean distance ||Δ|| providing an approximate range. The bearing can then be combined with the player's heading to express the entity in a player-relative coordinate system. The resulting state may contain fields such as entity type, distance, bearing, confidence, and temporal persistence.

## D. OCR and Event-Conditioned Processing

OCR is deliberately restricted to relevant ROIs rather than applied to every frame. A scene-change detector can identify when objective text or other UI content is likely to have changed. RapidOCR/PaddleOCR-style approaches are suitable candidates because the reviewed literature emphasizes their lightweight deployment characteristics [4]–[6]. A future benchmark should measure character accuracy, latency, CPU utilization, and failure modes under motion blur, scaling, lighting variation, and animation.

# IV. TEMPORAL STATE FUSION AND TACTICAL REASONING

## A. Temporal State Model

A frame-by-frame assistant suffers from object disappearance, intermittent detection, and noisy confidence values. A hostile entity that temporarily moves behind cover may disappear from one frame even though its tactical relevance has not disappeared. AEGIS therefore proposes maintaining a short-lived temporal memory for detected entities.

Safety-critical scalar variables such as health, armor, and ammunition can be represented by a deterministic finite-state machine (FSM), while hostile positions and confidence values can be maintained in a sliding buffer of the previous N observations. This approach is intentionally less computationally expensive than a full spatio-temporal transformer, while retaining a degree of object persistence. More complex temporal models remain candidates for future comparative experiments [7]–[9].

## B. Threat Assessment

The research synthesis proposes a formalized threat score rather than relying exclusively on free-form language-model judgment. For n detected entities, a candidate formulation is:

ThreatScore = Σᵢ [ w₁(1/Dᵢ) + w₂Hstatus + w₃Wlevel + w₄Cᵢ ]

where Dᵢ is the distance to entity i, Hstatus represents inverse player health, Wlevel represents an objective or wanted/police state, and Cᵢ is a clustering multiplier. The weights are not empirically calibrated in the present work; they are parameters for a future controlled evaluation. This distinction is important because a mathematical formulation does not itself demonstrate predictive validity.

## C. Hybrid Deterministic-Generative Reasoning

AEGIS separates safety-critical responses from open-ended strategic reasoning. A deterministic rule engine can handle conditions such as low health or immediate danger with bounded execution time. Generative reasoning can then be reserved for tasks such as route suggestions, objective interpretation, or explanation. The output of the generative component should conform to a strict schema so that free-form model text cannot directly trigger privileged system behavior.

This hybrid architecture addresses two limitations of pure generative reasoning. First, generative inference can have variable latency, making it unsuitable as the sole mechanism for time-critical responses. Second, a language model can hallucinate or over-interpret uncertain visual evidence. A deterministic layer can provide predictable behavior while the generative layer supplies higher-level synthesis [30], [31].

# V. EVENT-DRIVEN INFERENCE AND EDGE AI

## A. Adaptive Inference Frequency

Continuous VLM inference at display frame rates is unnecessary for many gameplay events. AEGIS therefore proposes a hierarchy of gates: global frame-change detection, ROI-level change detection, entity-state transitions, and finally LLM/VLM invocation. SSIM is one candidate for detecting structural changes because it considers luminance, contrast, and structural similarity rather than raw pixel error [10].

The supplied research synthesis lists 3,600 calls/min for continuous 60-FPS inference and substantially lower reference frequencies for event-driven strategies. These figures are included here as literature/reference values, not AEGIS measurements. The corresponding AEGIS targets are shown in Table I.

| Strategy | Reference value in supplied synthesis | Proposed AEGIS target | Status |
| --- | --- | --- | --- |
| Continuous (60 FPS) | 3,600 calls/min | Not recommended | Reference |
| Fixed interval (1 Hz) | 60 calls/min | Not preferred | Reference |
| SSIM-triggered | 45–80 calls/min | ≤120 calls/min | Target |
| State-change gating | 20–30 calls/min | ≤50 calls/min | Target |

TABLE I
Inference strategies and proposed AEGIS operating budgets.

## B. GPU Contention and Memory Budgets

Concurrent AI inference must not materially interfere with game rendering. The supplied AEGIS specification establishes a proposed perception VRAM budget of approximately 450 MB and an overall system RAM budget of approximately 1.6 GB. These are engineering constraints, not demonstrated measurements. Direct3D 12 exposes multiple queues and asynchronous compute mechanisms that can support concurrent graphics and compute workloads [13], [14]. Future implementation work should measure frame-time impact rather than assume that asynchronous compute automatically eliminates contention.

Quantization provides another path to resource control. The research synthesis discusses FP8, INT4-AWQ, GGUF, and ONNX/INT8 deployment as candidate techniques [16]–[19]. Heavy local VLM reasoning may remain too large for a strict perception budget, motivating a tiered architecture in which lightweight perception is local and optional high-level reasoning can use either a smaller local model or a cloud service. Such a design introduces a trade-off among latency, privacy, network dependence, and model capability.

## C. Latency Decomposition

End-to-end latency should be treated as a pipeline rather than a single model metric. AEGIS defines:

Ttotal = Tcapture + TCV + TOCR + Tfusion + TLLM + Toverlay

The supplied research synthesis states that capture and fusion can be kept below a small fraction of the total budget and identifies generative inference as a likely dominant component. This is a hypothesis for AEGIS rather than a measured result. A future profiler should report mean, median, P95, and P99 latency for each stage, as well as dropped frames and game-frame-time impact.

# VI. LITERATURE-DERIVED PERFORMANCE ANALYSIS

Because AEGIS has not yet undergone a completed empirical evaluation by the author, this section intentionally avoids reporting implementation results. Instead, it converts the numerical material in the supplied research synthesis into benchmarks and targets that can guide future experiments.

| Metric | Value reported in reviewed literature/synthesis | Proposed AEGIS target | Interpretation |
| --- | --- | --- | --- |
| mAP@0.5 (GUI) | 0.970 | ≥0.920 | Reference detector performance vs. design target |
| mAP@0.5–0.95 | 0.860 | ≥0.750 | Stricter localization/accuracy target |
| Minimap icon recall | 0.940 | ≥0.900 | Reference for small UI-object detection |
| Inference latency | 7.9 ms | ≤15 ms | Reference latency for real-time CV |
| Model parameters | 2.8 M | ≤5 M | Candidate size budget |

TABLE II
Visual-perception values reproduced from the supplied research synthesis; none are AEGIS measurements.

These values should be interpreted cautiously. A reported mAP value is only comparable when the dataset, class definitions, image resolution, training protocol, confidence threshold, and evaluation implementation are sufficiently aligned. Therefore, the values establish motivation and target ranges rather than evidence that AEGIS will achieve the same performance.

# VII. HUMAN-COMPUTER INTERACTION AND ADAPTIVE ASSISTANCE

## A. Cognitive Workload

An assistant that delivers correct information can still fail if the player cannot process that information during a high-intensity event. Cognitive Load Theory and the split-attention effect provide a basis for treating attention as a limited system resource. The supplied literature synthesis connects workload measurement to NASA-TLX, visual attention, and physiological indicators [22], [23], [25].

## B. Fitts's Law and Spatial Placement

Fitts's law models target-acquisition difficulty as:

ID = log₂(A/W + 1)

where A is the movement amplitude and W is target width [28]. In a gameplay interface, the broader principle is that information placed far from the player's current visual focus can increase search cost. AEGIS therefore proposes adaptive overlay placement based on the location and urgency of the detected threat. This should not be described as a proven gaze-aware improvement until an actual user study is conducted.

| Interface condition | Literature/reviewed value | AEGIS interpretation |
| --- | --- | --- |
| Static corner panel | Reported reaction penalty: +210 ms | Reference HCI risk |
| Dense text alerts | Reported mission-failure rate: 18% | Reference overload risk |
| Adaptive spatial UI | Reported reaction improvement: −140 ms | Reference motivation for adaptive placement |

TABLE III
Human-factors values are literature-derived and are not results from an AEGIS user study.

A proper AEGIS HCI experiment should compare at least static, dense, and adaptive conditions using task performance, reaction time, error rate, and NASA-TLX. The experimental design should also control for player skill, game familiarity, display resolution, and task difficulty.

# VIII. RELIABILITY, SECURITY, PRIVACY, AND ANTI-CHEAT CONSIDERATIONS

## A. Confidence-Aware Assistance

AEGIS should propagate uncertainty through the decision pipeline rather than treating detector outputs as ground truth. The proposed chain is Visual Confidence → State Confidence → Decision Confidence → User Action. If a visual detector produces a low-confidence hostile classification, downstream reasoning should preserve that uncertainty. An abstention mechanism is preferable when the cost of a false alarm is greater than the cost of missing a low-probability event.

## B. Prompt Injection Through Game Content

Multimodal systems introduce a security boundary that does not exist in conventional deterministic HUD parsing. Game chat, subtitles, signage, or other on-screen text may contain attacker-controlled strings. If OCR output is placed directly into an LLM instruction context, text such as an instruction-like phrase could attempt to influence model behavior. Recent research demonstrates that vision-language systems can be vulnerable to visual or cross-modal prompt injection [36], [37]. AEGIS should therefore separate trusted system instructions from untrusted game content, sanitize OCR fields, restrict the action schema, and validate generated outputs before they are consumed by any privileged component.

## C. Privacy-Preserving Capture

Continuous screen capture can expose private desktop information. The proposed architecture therefore isolates the game window or required regions instead of processing the entire desktop. This reduces unnecessary data exposure and also reduces the amount of visual content that reaches the perception pipeline.

## D. Anti-Cheat Compatibility

AEGIS is intentionally external and non-invasive: it does not modify game memory, inject code, or generate game inputs. However, non-invasive architecture does not guarantee compatibility with every anti-cheat product. Kernel-level and other anti-cheat systems can inspect processes, drivers, system state, or access patterns [33]–[35]. Consequently, the paper does not make a universal claim that AEGIS is safe or permitted by all games. Compatibility must be evaluated separately for each title and according to its technical and Terms-of-Service constraints.

# IX. CROSS-GAME GENERALIZATION

Manual coordinates for health bars, minimaps, and objective text are practical for an initial prototype but do not scale to a game-agnostic product. Different games place HUD elements differently, use different iconography, and change their visual presentation across resolutions and accessibility settings.

A promising research direction is zero-shot UI discovery using vision-language models capable of identifying semantic regions rather than relying exclusively on hard-coded coordinates. Qwen2.5-VL, for example, reports capabilities in object localization, structured visual understanding, and long-video interpretation [16 and verified in current literature]. Such a model could serve as a calibration component that identifies likely health, ammunition, minimap, or objective regions before handing them to smaller specialized models.

Cross-game generalization should be evaluated using games that differ in genre, HUD layout, color palette, camera model, and typography. A meaningful benchmark should distinguish zero-shot performance from performance after per-game calibration. The latter may still be valuable if calibration requires only a few minutes rather than retraining.

# X. PROPOSED EXPERIMENTAL METHODOLOGY

The absence of completed AEGIS experiments is a limitation of the present paper, but it also allows a clear experimental protocol to be defined. The following measurements are proposed for future validation.

## A. Perception Benchmark

Construct a labeled gameplay dataset containing minimap icons, HUD values, objective text, and relevant threat entities. Report precision, recall, mAP@0.5, mAP@0.5–0.95, OCR character/word accuracy, and per-stage inference latency. Evaluation should be performed on previously unseen gameplay sequences rather than only on frames sampled from the training material.

## B. Event-Gating Benchmark

Compare continuous inference, fixed-frequency inference, SSIM-triggered inference, and state-change gating. For each condition, measure inference calls per minute, GPU utilization, VRAM usage, dropped frames, game FPS, event-detection delay, and missed-event rate. The primary hypothesis for RQ3 is that event-driven gating can reduce unnecessary inference while retaining acceptable tactical responsiveness.

## C. System-Level Benchmark

Run the game with and without AEGIS under repeatable graphics settings. Record frame-time distributions rather than only average FPS. The analysis should include P50/P95/P99 game-frame time, AI latency, memory footprint, VRAM footprint, temperature, and stability over a long-duration soak test. The supplied AEGIS specification proposes a 45-minute soak test and a 1,000-event latency profile as useful evaluation targets.

## D. HCI User Study

Compare baseline gameplay, static-overlay assistance, dense textual assistance, and adaptive spatial assistance. Participants should perform standardized tasks with matched difficulty. Measure reaction time, tactical error rate, mission completion, NASA-TLX, and subjective trust. Player experience and skill should be recorded as covariates.

## E. Ablation Study

Remove one subsystem at a time: temporal memory, event gating, deterministic rules, adaptive overlay, confidence propagation, and cloud/local fallback. The goal is to identify which architectural components contribute meaningfully to latency, reliability, and user performance. Without ablation, improvements cannot be confidently attributed to individual design choices.

# XI. LIMITATIONS

The principal limitation is that the present work is a literature-grounded architecture and methodology paper rather than an experimental validation paper. No end-to-end AEGIS benchmark, user study, or controlled gameplay experiment is reported. Consequently, the numerical values reproduced from the supplied research synthesis cannot establish that AEGIS achieves the same performance.

A second limitation is heterogeneity among the cited sources. Object-detection metrics, OCR benchmarks, latency values, and HCI measurements may have been obtained under different hardware, datasets, workloads, and experimental protocols. Direct comparison therefore requires a common evaluation environment.

A third limitation concerns generalization. A game-agnostic architecture does not automatically imply game-agnostic performance. New titles may introduce unseen HUD designs, rendering effects, languages, camera conventions, or anti-cheat policies. These factors must be addressed empirically.

# XII. FUTURE WORK

Future work should first implement and benchmark the complete perception-to-reasoning pipeline. Priority experiments are the visual dataset benchmark, event-gating comparison, end-to-end latency decomposition, and game-frame-time impact. Subsequent work should evaluate the hybrid rule/LLM architecture against a pure LLM baseline and determine how confidence thresholds affect false alarms and missed threats.

A second direction is self-calibration. A lightweight vision-language model could discover HUD semantics for a new title, after which specialized detectors and OCR modules could operate on the discovered ROIs. A third direction is privacy and security hardening, including explicit trusted/untrusted data channels, prompt-injection testing, and per-game anti-cheat compatibility analysis.

Finally, the most important validation is human-centered: whether AEGIS improves player decision quality without increasing cognitive load. This requires controlled studies rather than assuming that more information or faster inference is always better.

# XIII. CONCLUSION

AEGIS presents a research framework for real-time AI gameplay assistance in which the AI augments rather than replaces the human player. The architecture combines specialized visual perception, temporal state fusion, event-driven inference, resource-aware edge deployment, deterministic safety logic, generative strategic reasoning, confidence propagation, and adaptive human-computer interaction.

The literature reviewed in the supplied research document provides evidence that the individual building blocks—real-time object detection, lightweight OCR, temporal modeling, asynchronous compute, model quantization, cognitive-load-aware interface design, and multimodal reasoning—are technically plausible. However, this paper deliberately does not claim that AEGIS itself has achieved the numerical performance reported by those sources. Those values serve as external benchmarks and motivation for proposed targets.

The central contribution is therefore a testable methodology rather than an unsupported performance claim. Future experiments can determine whether the proposed architecture meets its latency, resource, reliability, usability, and generalization objectives under real gameplay conditions.

# REFERENCES

[1] “Vision-Based Approach for Automatic macOS Accessibility Generation,” arXiv:2507.16704v1, 2025. [Online]

[2] “A Multimodal Late Fusion Framework for Semantic Classification,” IEEE SERA 2026. [Online]

[3] M. A. Alif and M. Hussain, “YOLOv12: A Breakdown of the Key Architectural Features,” arXiv:2502.14740, 2025. [Online]

[4] “Best Open Source OCR Tools 2026: Tesseract, EasyOCR,” ImageToTable.ai, 2026. [Online]

[5] M. F. T. Nakrsu, “Comparison-of-OCR (KerasOCR, PyTesseract, EasyOCR),” GitHub repository. [Online]

[6] “Benchmarking OCR APIs on Real-World Documents,” Nanonets. [Online]

[7] “An Efficient Hidden Markov Model with Periodic Recurrent Neural [Network],” Electronics, vol. 11, no. 24, 2022. [Online]

[8] “Hybrid Artificial Potential Fields and Spatio-Temporal Transformers,” arXiv preprint, 2026. [Online]

[9] “Comprehensive Review of Deep Learning Approaches for Single [Object/Trajectory Modeling],” PMC. [Online]

[10] “CCW-SSIM: A Novel Color-Enhanced Structural Similarity Metric,” Politecnico di Milano thesis, 2023. [Online]

[11] “VRAM Bandwidth and Its Big Role in Optimization,” Procedural Pixels. [Online]

[12] “GPU Memory Bandwidth: Why It Matters More Than VRAM for Inference Workloads,” Inflect. [Online]

[13] Microsoft, “Multi-engine synchronization,” Microsoft Learn, Direct3D 12. [Online]

[14] Unity, “DirectX 12 Improvements in Unity 6,” Unity Technologies. [Online]

[15] Linus Tech Tips, “Explaining Asynchronous Compute.” [Online]

[16] S. Bai et al., “Qwen2.5-VL Technical Report,” arXiv:2502.13923, 2025. [Online]

[17] “LLMs on Jetson Orin Benchmarked: tok/s & VRAM,” IoT Digital Twin PLM. [Online]

[18] “Best Local LLMs for Every NVIDIA RTX 50 Series GPU,” APXML. [Online]

[19] “LLM Inference Optimization and Quantization 2026,” Zylos Research. [Online]

[20] SeroCoder/SeroC2, GitLab repository. [Online]

[21] GStreamer 1.26 Release Notes, Freedesktop.org. [Online]

[22] “Predicting and Explaining Cognitive Load, Attention, and Working [Memory],” IEEE Transactions on Games, 2025. [Online]

[23] “Cognitive Load and Visual Attention Assessment Using Physiological [Measures],” PMC. [Online]

[24] “Self-Avatar-Supported Observational Learning,” PolyU repository. [Online]

[25] “Workload Assessment of Operators: Correlation Between NASA-TLX and Pupillary Responses,” ResearchGate. [Online]

[26] “Under Pressure: Cognitive Effort During Website-Based Task,” Taylor & Francis. [Online]

[27] “Effects of Virtual Controller Representation and Virtuality on [Performance],” VRST 2025. [Online]

[28] O. Chapuis, R. Blanch, and M. Beaudouin-Lafon, “Fitts’ Law in the Wild: A Field Study of Aimed Movements,” 2007. [Online]

[29] “A Case Study of First Person Aiming at Low Latency for Esports.” [Online]

[30] “CombatVLA: An Efficient Vision-Language-Action Model for Combat,” arXiv:2503.09527, 2025. [Online]

[31] “VLA-RISK: Benchmarking Vision-Language [Action Models],” OpenReview. [Online]

[32] “Benchmarking Vision, Language, & Action Models on Robotic [Tasks].” [Online]

[33] Riot Games, “Vanguard On-Demand,” 2026. [Online]

[34] “A Critical Examination of Kernel-Level Anti-Cheat Systems,” arXiv:2408.00500, 2024. [Online]

[35] T. Chothia et al., “Anti-Cheat: Attacks and the Effectiveness of Client-Side Defences,” 2024. [Online]

[36] “Prompt Injection Explained and How to Stop It,” Prompt Builder. [Online]

[37] Xcheater, “All About Prompt Injection: How Attackers Trick AI,” InfoSec Writeups. [Online]

Reference note: The bibliography is based on the source list supplied with the AEGIS research document. Some entries are web resources or technical articles rather than peer-reviewed papers; venue-specific IEEE submission requirements should be applied before publication.

---

# Source: Document 1 — Product Requirements Document

### PDF page 1

Document 1 Product Requirements Document

#### PRD

#### 1. Product Overview & System Architecture

1.1 Executive Summary AEGIS AI Gameplay Intelligence System) is a non-invasive, game-agnostic tactical assistant designed to observe on-screen gameplay frames in real time and deliver low-latency, contextual guidance through an overlay interface. The initial prototype targets single-player

#### PC

gameplay on Grand Theft Auto

#### V

Rockstar Games) running on entry-level consumer hardware 4

#### GB

to 6

#### GB

#### VRAM,

16

#### GB

system

#### RAM.

AEGIS isolates its pipeline completely from the game's internal process space: it does not read, write, or hook into game memory

#### RAM,

invoke internal binaries, or inject code into the DirectX rendering pipeline.

- GAME PROCESS GTA V : DirectX 11 Surface Render → Desktop Window

Manager

#### DWM

→ Backbuffer SwapChain

- DXGI Desktop Duplication: Zero-Copy VRAM Blit) ● PROCESS 1 CAPTURE & TELEMETRY ENGINE ○ DXcam capture loop Target: 30 FPS, Frame delta trigger: SSIM / Hash) ○ Frame Slicing: Minimap ROI 320320, Health/Armor ROI 22020,

Objective

#### ROI

42050 ○ Deterministic Telemetry: Vectorized HSV Color Thresholding Health %, Armor %, Wanted Stars) ○ Object Detection: YOLOv11n ONNX Runtime via DirectML, Minimap Blip Parsing) ○ OCR Engine: RapidOCR PaddleOCR ONNX, Trigger-based Objective Text Parsing)

- IPC Zero-Copy SharedMemory Buffer / Fast IPC ● PROCESS 2 CONTEXT FUSION & STATE MACHINE ○ Evaluates State Hash: Delta check on Health, Threats, Wanted Level,

Objective ○ Threshold Gating: Suppresses LLM invocations if frame delta is below variance threshold ○ Pre-Prompt Serialization: Encodes Game State into compact JSON schema

- Async Network Stream / Offline Fallback Engine) ○ CLOUD INFERENCE Groq LPU : Model: Llama-3.18BInstant, JSON

Schema Enforcement, Latency: 120 ms

- 

220 ms

### PDF page 2

○ LOCAL SLM INFERENCE WORKER : Engine: llama-cpp-python CPU Bound, 2 Threads), Model: Qwen2.51.5BInstruct

#### GGUF

#### Q4_K_M,

Context: 1024 Tokens, No

#### GPU

layer offloading

- Thread-safe IPC Queue: Structured JSON ● PROCESS 3 NATIVE DIRECTX 11 OVERLAY ○ Engine: PyImGui over GLFW / Native Win32 Window ○ Window Flags: WS_EX_LAYERED | WS_EX_TRANSPARENT |

#### WS_EX_NOACTIVATE

|

#### WS_EX_TOPMOST

○ Render Pass: Transparent, non-blocking click-through HUD Execution overhead: < 1.5 ms / frame) 1.2 User Persona ● Persona : "The Overwhelmed Player". ● Behavior : A gamer navigating complex open-world missions with multi-directional threats, rapid health decay, and multi-objective storylines.

- Pain Points : Misses mini-map warnings during high-speed chases, misses

wanted-level escalations, and pauses repeatedly to look at wikis or walkthrough videos, breaking narrative immersion.

#### 2. Technical Stack Specification

Subsystem Component / Tech Version / Model Target Execution Mode / Provider Operational Overhead Runtime Python 3.11.x 64-bit Native Multi-Processing (spawn) Baseline: 45 MB RAM per process Screen Capture dxcam ≥ 0.1.5 Windows DXGI Desktop Duplication GPU-to-CPU 2.5 ms, 0% CPU blit Deterministic CV OpenCV (cv2) 4.10.x Headless) NumPy Vectorized HSV Masking CPU 0.3 ms per slice Object Detection YOLOv11n ONNX 11.0.x Nano: 2.6M params) ONNX Runtime DirectMLExecutionProvider) VRAM 120 MB; Latency: 8 ms-14 ms Text Recognition RapidOCR ONNX Mobile v4 CPU Threadpool 2 Threads) Latency: 12 ms-22 ms Cropped ROI Reasoning Engine Groq Cloud SDK groq-python 0.9.x llama-3.18b-instant via HTTP/2 Stream Cloud Latency: 120 ms-250 ms; VRAM 0 MB

### PDF page 3

#### JSON

Subsystem Component / Tech Version / Model Target Execution Mode / Provider Operational Overhead Fallback Engine llama-cpp-python 0.2.x Qwen2.51.5BInstruct-Q4_K_M.gguf System RAM 1.1 GB; CPU 2 pinned threads Overlay Frontend pyimgui + glfw ImGui v1.89 DirectX 11 / Native Layered Win32 HWND RAM 18 MB; Render: 1.0 ms IPC Infrastructure multiprocessing Python Native SharedMemory + SimpleQueue Latency: 0.1 ms synchronization

#### 3. Data Schemas & Structural Interfaces

#### 3.1 Perception Telemetry Interface

{ "$schema": "json-schema.org/draft-07/schema#", "title": "PerceptionTelemetry", "type": "object", "properties": { "timestamp_epoch_ms": { "type": "integer" }, "frame_id": { "type": "integer" }, "health_percentage": { "type": "integer", "minimum": 0, "maximum": 100 }, "armor_percentage": { "type": "integer", "minimum": 0, "maximum": 100 }, "wanted_level": { "type": "integer", "minimum": 0, "maximum": 5 }, "objective_raw_text": { "type": "string", "maxLength": 128 }, "minimap_entities": { "type": "array", "items": { "type": "object", "properties": { "class": { "type": "string", "enum": ["enemy", "police", "objective_blip", "destination"] },

### PDF page 4

#### JSON

"norm_rel_x": { "type": "number", "minimum": -1.0, "maximum": 1.0 }, "norm_rel_y": { "type": "number", "minimum": -1.0, "maximum": 1.0 }, "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 } }, "required": ["class", "norm_rel_x", "norm_rel_y", "confidence"] } } }, "required": ["timestamp_epoch_ms", "frame_id", "health_percentage", "armor_percentage", "wanted_level", "objective_raw_text", "minimap_entities"] }

#### 3.2 Fused Context State Schema LLM Payload)

{ "state_signature": "a7f3b89c", "player_status": { "hp": 34, "ap": 0, "status": "CRITICAL_HEALTH" }, "tactical_environment": { "threat_count": 3, "police_engaged": true, "wanted_stars": 3, "nearest_threat_bearing_deg": 135, "nearest_threat_dist_normalized": 0.28 }, "mission_context": { "active_objective": "Lose the Cops"

### PDF page 5

#### JSON

} }

#### 3.3 Overlay Action Payload Schema Strict Output)

{ "$schema": "json-schema.org/draft-07/schema#", "title": "TacticalActionPayload", "type": "object", "properties": { "alert_priority": { "type": "string", "enum": ["LOW",

#### "MODERATE",

#### "URGENT",

#### "FATAL"]

}, "directive_title": { "type": "string", "maxLength": 28 }, "action_instruction": { "type": "string", "maxLength": 80 }, "spatial_cue": { "type": "object", "properties": { "screen_quadrant": { "type": "string", "enum": ["CENTER",

#### "BOTTOM_LEFT",

#### "TOP_RIGHT",

#### "FULL_PERIPHERY"]

}, "accent_color_hex": { "type": "string", "pattern": "^#[0-9A-Fa-f]{6}$" } }, "required": ["screen_quadrant", "accent_color_hex"] }, "ttl_seconds": { "type": "number", "minimum": 1.0, "maximum": 10.0 } }, "required": ["alert_priority", "directive_title", "action_instruction", "spatial_cue", "ttl_seconds"] } 4. Hardware Budgets & System Constraints All metrics define the operating ceiling on a baseline test environment Target machine: Intel Core i510300H /

#### AMD

Ryzen 5

#### 4600H,

16

#### GB

#### DDR4

#### RAM,

#### NVIDIA

### PDF page 6

GeForce GTX 1650 Mobile 4 GB VRAM / RTX 3050 4 GB, running Windows 10/11 64-bit with

#### GTA

#### V

running at 1080p Normal/High Settings). Resource Allocation Budget Metric System Constraint Maximum AEGIS Target Overhead VRAM Allocation 4096 MB Total <= 450 MB ONNX DirectML + DXGI System RAM Allocation 16384 MB Total <= 1600 MB All Subprocesses) CPU Utilization Total 100% across 8 threads <= 14% Total CPU Consumption Game Impact FPS Delta) 60.0 FPS Baseline Delta <= 3.0 FPS Degradation Frame Presentation Time 16.66 ms frame budget Overlay render pass <= 1.2 ms Latency Budget Formulation Latency_total = T_capture + T_CV_parse + T_fuse + T_inference + T_overlay_render ● T_capture ≤ 4.0 ms DXGI Desktop Duplication frame pull) ● T_CV_parse ≤ 22.0 ms HSV Health/Armor: 0.3 ms, YOLO Minimap ONNX 14.0 ms, RapidOCR

#### ROI

7.5 ms)

- T_fuse ≤ 0.5 ms State hashing and delta threshold evaluation) ● T_inference ≤ 250.0 ms Groq Cloud API round-trip token streaming) ● T_overlay_render ≤ 1.2 ms DirectX 11 pipeline submission) ● Total End-to-End Latency Target: ≤ 277.7 ms ≪ 1000 ms Well within the

sub-second requirement). Document 2 Critical Pitfalls, Subtle Bugs, and Micro-Decisions Matrix Failure Matrix: Critical Pitfalls & Mitigations Subsystem Area Critical Bug / Novice Mistake System Impact & Deterministic Mitigation Screen Capture DXGI Device Loss during Resolution Switches or Alt-Tab Events CRASH Fatal unhandled exception. FIX Catch COM error 0x887A0026 & rebuild. Screen Capture Color-Space Inversion DirectX BGRA to YOLO RGB SILENT FAILURE Red & Blue swapped. FIX Single cv2.COLOR_BGRA2RGB slicing.

### PDF page 7

Subsystem Area Critical Bug / Novice Mistake System Impact & Deterministic Mitigation Computer Vision Dynamic Screen Scaling & In-Game Aspect Ratio Mismatches DESYNC Fixed pixel crops read game world. FIX Normalized coordinates (x/W, y/H. Computer Vision HUD Dynamic Alpha Blending & In-Game Lighting Drift FALSE POSITIVE Background bleeding shifts HSV. FIX Compute saturation-independent sat ratios. Multiprocessing Memory Leaks in SharedMemory Allocation Buffers SYSTEM CRASH RAM exhausts in 15 minutes. FIX Single pre-allocated Ring Buffer. Multiprocessing Windows Fork Failure Global Code Execution on Spawn) PROCESS DEADLOCK Process infinite respawn. FIX Strict if __name__ == '__main__' guards. AI Reasoning Malformed JSON Returns from Cloud / Local LLMs UI FREEZE Overlay crashes parsing string. FIX Groq response_format or Regex validator. AI Reasoning Groq API Rate Limiting Under Fast Combat Conditions DROP Silent drop of tactical alerts. FIX Leaky Bucket queue with State Hashing. Overlay UI Window Focus Stealing During Mouse Clicks GAMEPLAY LOSS Game pauses, input drops. FIX WS_EX_NOACTIVATE & WS_EX_TRANSPARENT. Overlay UI DWM Desktop Composition Tearing on Mixed-Refresh Displays STUTTER 60 FPS drops to 30 FPS. FIX SwapChain DXGI_SWAP_EFFECT_FLIP_DISCARD. Detailed Failure Analysis & Production Mitigations 1. Screen Capture Subsystem Pitfall 1.1 DXGI Device Loss 0x887A0026 / DXGI_ERROR_DEVICE_RESET ● Symptom : When the player toggles fullscreen, changes resolution, or Alt-Tabs out of

#### GTA

#### V,

dxcam.grab() raises an unhandled

#### C

#### COM

pointer exception and crashes the process.

- Underlying Cause : The operating system reclaims the DirectX Graphics

Infrastructure swap chain surface when the display mode changes.

- Mitigation : Implement an explicit recreation wrapper:

### PDF page 8

P ython import dxcam import time class ResilientCapture: def __init__(self, output_idx=0): self.output_idx = output_idx self.camera = dxcam.create(output_idx=self.output_idx) def get_frame(self): try: frame = self.camera.grab() return frame except Exception as e: # DXGI_ERROR_DEVICE_REMOVED or

#### DXGI_ERROR_DEVICE_RESET

del self.camera time.sleep(0.5) self.camera = dxcam.create(output_idx=self.output_idx) return None Pitfall 1.2 Implicit Color Conversions Sapping Memory Bandwidth ● Symptom : Frame capture consumes 18% CPU at 1080p, and YOLO detection accuracy for blue/red markers drops to zero.

- Underlying Cause : Direct3D captures frames in

#### DXGI_FORMAT_B8G8R8A8_UNORM

#### BGRA.

Passing this naively into models expecting

#### RGB

causes blue and red channel inversion. Using cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB creates a full-frame memory reallocation every frame 192010803 bytes ≈ 6.2

#### MB

per blit × 30

#### FPS

= 186 MB/s unnecessary memory churn).

- Mitigation : Do not convert the full frame. Crop the regions of interest (minimap,

health) in native

#### BGRA

format first, then run channel conversion strictly on the isolated sub-array. 2. Computer Vision Subsystem Pitfall 2.1 Absolute Coordinate Hardcoding vs. Scaled Displays ● Symptom : The system runs reliably on the developer's 1080p monitor, but shifts out of position on laptops with 125% or 150% Windows

#### DPI

Display Scaling.

### PDF page 9

P ython

- Underlying Cause : Windows applies Desktop Window Manager DWM DPI

virtualization. The pixel coordinates returned by Win32 do not match raw monitor rasterization coordinates.

- Mitigation : Declare DPI Awareness before initializing capture:

import ctypes # Set Process DPI Awareness to Per-Monitor DPI Aware try: ctypes.windll.shcore.SetProcessDpiAwareness(2) except Exception: ctypes.windll.user32.SetProcessDPIAware() Store all bounding boxes as normalized floating-point coordinates. Pitfall 2.2 Translucent HUD Background Shift ● Symptom : In GTA V, when the player drives past sandy terrain or bright lights, the health bar is detected as 0% or fluctuating wildly.

- Underlying Cause : The HUD backing plate is alpha-blended over the 3D world.

Background environmental lighting blends into the

#### HUD

pixels, throwing Hue, Saturation, and Value

#### HSV

outside static ranges.

- Mitigation : Instead of broad HSV thresholds, use a normalized

Green-over-Red/Blue channel differential invariant to ambient luminance spikes caused by in-game lighting. 3. Concurrency and IPC Subsystem Pitfall 3.1 IPC Shared Memory Leak (multiprocessing.shared_memory) ● Symptom : After 20 minutes of runtime, Python raises FileExistsError or the OS runs out of available paging file space, crashing the machine.

- Underlying Cause : Creating dynamic SharedMemory(create=True) instances

for each frame without deterministic unlink calls exhausts the Windows operating system kernel handle table.

- Mitigation : Allocate a static, fixed-size ring buffer containing exactly two frame

slots at process startup with lock-free atomic pointer swaps using multiprocessing.Value('i', 0. Pitfall 3.2 Multiprocessing Process Spawning on Windows ● Symptom : When running the main script, Windows repeatedly spawns dozens of instances of the app, crashing the desktop.

- Underlying Cause : Windows lacks POSIX fork(). It utilizes spawn, which

re-imports the main Python file from top to bottom in every child process.

- Mitigation : Wrap all initialization code inside if __name__ == '__main__':. Place

worker entry points in separate importable modules.

### PDF page 10

P ython P ython 4. AI Reasoning & API Subsystem Pitfall 4.1 Model Schema Non-Compliance & Broken JSON ● Symptom : Local SLMs or Groq endpoints emit leading conversational filler: "Here is your tactical recommendation: json { ... } ", which causes json.loads() to throw a JSONDecodeError.

- Mitigation : If using Groq, pass the strict JSON mode parameter:

response = await client.chat.completions.create( model="llama-3.1-8b-instant", messages=[...], response_format={"type": "json_object"}, temperature=0.1 ) Implement a deterministic regex sanitizer fallback: import re, json def extract_json_payload(raw_text: str) -> dict: match = re.search(r"\{.*?\}", raw_text, re.DOTALL) if match: try: return json.loads(match.group(0)) except json.JSONDecodeError: pass return { "alert_priority": "LOW", "directive_title": "HOLD POSITION", "action_instruction": "Maintain current tactical stance.", "spatial_cue": {"screen_quadrant": "CENTER", "accent_color_hex":

#### "#00FF00"},

"ttl_seconds": 2.0 } Pitfall 4.2 Token Explosion & Inference Queue Drift ● Symptom : Overlay recommendations lag behind the game state by 6 to 10 seconds during heavy firefights.

- Underlying Cause : Multiple events trigger API calls while a previous request is

still in flight, queuing requests sequentially.

### PDF page 11

P ython P ython

- Mitigation : Use an atomic drop-tail queue (queue.Queue(maxsize=1. If a new

state triggers while an older request is executing, drop the pending request and send only the newest state. Set max_tokens=60 to bound generation latency. 5. Native Overlay Rendering Subsystem Pitfall 5.1 Stealing Focus and Breaking Game Controllers ● Symptom : When the overlay updates, the player's controller or keyboard stops responding in

#### GTA

#### V,

or the mouse pointer snaps visible.

- Underlying Cause : The Win32 OS treats standard window updates as

activating events, pulling user focus away from the game's parent window.

- Mitigation : Strip activating window styles and set non-interactive extended

flags directly on the

#### HWND

import win32gui, win32con def set_overlay_non_interactive(hwnd): style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) win32gui.SetWindowLong( hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST ) Pitfall 5.2 Alpha Blending Visual Artifacts ● Symptom : The overlay text appears surrounded by an opaque black box, obscuring the player's crosshair.

- Underlying Cause : Standard Win32 color keying LWA_COLORKEY tests

against absolute values. Antialiased text creates intermediate dark gray pixels that do not match the transparent color key.

- Mitigation : Use DirectComposition or Desktop Window Manager DWM glass

frame extensions: import ctypes from ctypes import wintypes class MARGINS(ctypes.Structure): _fields_ = [ ("cxLeftWidth", wintypes.INT),

### PDF page 12

Shell ("cxRightWidth", wintypes.INT), ("cyTopHeight", wintypes.INT), ("cyBottomHeight", wintypes.INT) ] def enable_true_alpha(hwnd): margins = MARGINS(-1, -1, -1, -1) ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins)) Document 3 Timeline, Environment Isolation, and

#### AI

Engineering Discipline 1. Development Environment Isolation Specification To ensure total reproducibility across consumer setups and prevent CUDA runtime version conflicts, the environment must follow this exact deployment specification. 1.1 Python & Toolchain Pinning Python Runtime: 3.11.9 64-bit Avoid 3.12 initially due to PyImGui and ONNX Runtime DirectML wheel build incompatibilities). Environment Manager: Conda or UV / Native venv. Recommended: Native venv with wheels pinned via strict

#### SHA256

hashes). # Environment Creation Protocol py -3.11 -m venv aegis_env .\aegis_env\Scripts\activate # Base tooling update python -m pip install --upgrade pip==24.0 setuptools==69.5.1 wheel==0.43.0 1.2 Library Version Matrix & DirectML Configuration Do not install onnxruntime-gpu if testing on mixed hardware or entry-level GTX 1650 cards, as

#### CUDA

11/12 library mismatches frequently cause fallback to unaccelerated

#### CPU

execution. Instead, install onnxruntime-directml to run acceleration across DirectX 12 compute shaders.

### PDF page 13

None # requirements.txt dxcam==0.1.5 numpy==1.26.4 opencv-python-headless==4.10.0.84 onnxruntime-directml==1.18.0 ultralytics==8.2.50 rapidocr-onnxruntime==1.3.24 groq==0.9.0 llama-cpp-python==0.2.79 pyimgui==2.0.0 glfw==2.7.0 pywin32==306 pydantic==2.7.4 requests==2.32.3 pytest==8.2.2 1.3 Git Versioning & Asset Governance ● Do not check binary model weights (.pt, .onnx, .gguf) directly into Git commits. ● Configure .gitignore to exclude *.onnx, *.engine, *.gguf, and gameplay video screen recording files (*.mp4, *.mkv).

- Track neural model weights and test frames using DVC Data Version Control)

backed by a shared storage folder or local drive cache.

#### 2. Sprint-by-Sprint Implementation Timeline

Project Roadmap Semester Timeline) Sprint Focus Area Key Deliverables Success Verification Gate Sp 1 W 12 Foundations & Infrastructure DXcam pipeline, Win32 transparent overlay stub < 3 ms capture latency, Zero game focus loss Sp 2 W 34 Deterministic Perception Pipeline Health/Armor HSV slicers, Objective ROI RapidOCR 100% precision on bars, OCR completes in < 25 ms Sp 3 W 56 Minimap Object Detection ONNX YOLOv11n fine-tuned on GTA 5 blips, DirectML build mAP0.5 >= 90%, Inference latency < 15 ms

### PDF page 14

Sprint Focus Area Key Deliverables Success Verification Gate Sp 4 W 78 State Machine & Reasoning Pipeline Context Fusion engine, Groq API integration Structured JSON output, End-to-end time < 350 ms Sp 5 W 910 Local Fallback & System Hardening Qwen-1.5B llama-cpp worker, Error recovery wrappers Offline failover works, Zero VRAM OOM crashes Sp 6 W 1112 Evaluation & Research Validation Latency profiling, NASATLX user testing, paper metrics Complete experimental data for project report Detailed Sprint Breakdown & Execution Protocols Sprint 1 Capture Pipeline & Overlay Subsystem Weeks 12 ● Tasks : Build a standalone ScreenCapture module using dxcam. Benchmark capture time against 1080p full-screen

#### GTA

#### V.

Implement the

#### GLFW

+ PyImGui transparent window loop. Apply

#### WS_EX_TRANSPARENT,

#### WS_EX_LAYERED,

and

#### WS_EX_NOACTIVATE.

Validate that user mouse clicks, keyboard bindings, and gamepad inputs pass directly through to

#### GTA

#### V

without dropping inputs.

- Success Gate : Frame capture completes under 3.0 ms; the overlay renders text

over the game at 60

#### FPS

while consuming less than 25

#### MB

of system

#### RAM.

Sprint 2 Deterministic Telemetry & RapidOCR Weeks 34 ● Tasks : Record 20 minutes of 1080p GTA V gameplay footage across varied conditions. Extract pixel coordinates for the health bar, armor bar, wanted stars, and objective text. Implement vectorized NumPy

#### HSV

thresholding for health and armor status. Integrate RapidOCR on the objective text

#### ROI.

Implement a frame-to-frame pixel differencing check so

#### OCR

only executes when the text changes.

- Success Gate : Health and armor values parse with 100% accuracy in 1.0 ms;

text reads correctly within 25.0 ms of updating on-screen. Sprint 3 Minimap Object Detection via YOLOONNX Weeks 56 ● Tasks : Annotate a dataset of 600 cropped minimap frames containing four classes: police_blip, enemy_blip, destination_marker, objective_blip. Train YOLOv11n locally or via Google Colab for 100 epochs. Export weights to

#### ONNX

format with fixed input dimensions. Write an

#### ONNX

Runtime inference wrapper using DirectMLExecutionProvider.

- Success Gate : mAP0.5 achieves 90% on test splits; inference time executes

in 15.0 ms on the target

#### GPU.

Sprint 4 Context Fusion & Groq API Integration Weeks 78 ● Tasks : Build the ContextFusionEngine module. Calculate threat bearings relative to the minimap center. Implement state hashing to ensure requests fire only when health drops by 20%, wanted level changes, or a new objective

### PDF page 15

P ython appears. Wire the asynchronous Groq API worker using llama-3.18b-instant. Connect the output queue to the PyImGui overlay to display tactical alerts.

- Success Gate : End-to-end response time from in-game event to overlay update

is under 350 ms. Sprint 5 Offline Local Fallback & Stability Hardening Weeks 910 ● Tasks : Integrate llama-cpp-python loading Qwen2.51.5BInstruct Q4_K_M quantization). Restrict the model to 2

#### CPU

threads with 0

#### GPU

layer offloading. Implement network timeout detection: if the Groq

#### API

call fails or times out after 300 ms, route the request to the local fallback model. Run a 45-minute continuous gameplay soak test to check for memory leaks.

- Success Gate : System runs for 45 minutes continuously without crashing,

memory growth remains flat 50

#### MB

variation), and game frame rate stays within 3

#### FPS

of baseline. Sprint 6 Academic Benchmarking & User Studies Weeks 1112 ● Tasks : Log execution times across 1,000 game events to build latency distribution charts (mean,

#### P95,

#### P99.

Conduct user evaluation sessions with target players: compare mission completion with and without

#### AEGIS.

Administer the

#### NASA

Task Load Index

#### NASATLX

across its six dimensions. Compile final statistical results for the

#### PBL

report and research paper.

- Success Gate : NASATLX demonstrates a measurable reduction in reported

mental demand and frustration during high-intensity combat encounters.

#### 3. Engineering Rigor & Testing Protocols

3.1 Headless Synthetic Unit Tests Do not rely on launching GTA V to test basic pipeline logic. Implement a test suite using static

#### PNG

fixtures from recorded gameplay: # test_perception_unit.py import pytest import cv2 import numpy as np from perception.telemetry import extract_health_armor def test_extract_health_full(): # Synthetic frame fixture: 100% full green bar fake_crop = np.zeros((10, 110, 3), dtype=np.uint8) fake_crop[:, :, 1] = 200 # Pure green channel hp = extract_health_armor(fake_crop)

### PDF page 16

P ython assert hp == 100 def test_extract_health_empty(): # Synthetic frame fixture: Depleted black bar fake_crop = np.zeros((10, 110, 3), dtype=np.uint8) hp = extract_health_armor(fake_crop) assert hp == 0 3.2 Continuous Latency Profiling Instrument every pipeline step with monotonic high-resolution timers (time.perf_counter_ns()): import time class LatencyTracker: def __init__(self): self.records = {} def measure(self, label: str): class TimerContext: def __init__(self, outer, lbl): self.outer = outer self.lbl = lbl def __enter__(self): self.start = time.perf_counter_ns() def __exit__(self, *args): elapsed_ms = (time.perf_counter_ns() - self.start) / 1_000_000.0 self.outer.records[self.lbl] = elapsed_ms return TimerContext(self, label) # Usage in main loop: perf = LatencyTracker() with perf.measure("capture"): frame = camera.get_frame() with perf.measure("cv_inference"): state = parse_telemetry(frame)

### PDF page 17

3.3 Evaluation Protocol: NASA Task Load Index NASATLX To validate AEGIS's effectiveness for your academic review, run an A/B test across 5 to 10 participants playing the same

#### GTA

#### V

mission (e.g., escaping a 3-star wanted level):

- Condition A Control) : Default game HUD only (no AI overlay). ● Condition B Experimental) : Game HUD with AEGIS running. NASATLX 6Dimension Evaluation Form Score 1 - 20 ● 1 Mental Demand : How mentally demanding was the mission? ● 2 Physical Demand : How physically demanding was the pace? ● 3 Temporal Demand : How rushed did you feel during the encounter? ● 4 Performance : How successful were you in accomplishing the objective? ● 5 Effort : How hard did you have to work to maintain awareness? ● 6 Frustration : How insecure, discouraged, or stressed did you feel? Aggregate these scores into your project report to provide empirical evidence of

reduced cognitive load, turning a standard engineering project into a defensible research study.

---

# Source: AI Gameplay Assistant — Literature Review and Market Analysis

# The Evolution of Real-Time AI Gameplay Assistants: From Memory-Dependent Overlays to Non-Invasive Multimodal Systems

## Introduction to the Cognitive Demands of Modern Gameplay

Modern complex AAA video games, encompassing expansive open-world titles, intricate grand strategy games, and high-fidelity tactical shooters, present environments characterized by immense information density. Players are routinely required to process simultaneous, rapidly evolving data streams. These streams include vital health and resource indicators, dynamic enemy positioning, minimap topography, spatial audio cues, and overarching narrative objectives1. The cognitive load necessary to maintain situational awareness while simultaneously executing precise mechanical actions often overwhelms players.

Historically, players have attempted to mitigate this cognitive burden by relying on static external resources like community wikis and pre-recorded video guides1. However, these traditional support mechanisms possess a fundamental limitation: they are disconnected from the live, evolving state of the player's specific game session. The necessity for continuous context switching disrupts immersion and introduces temporal delays that can prove fatal in fast-paced environments. Consequently, a distinct market demand has emerged for real-time, context-aware companion applications. The industry is currently progressing toward state-of-the-art, non-invasive artificial intelligence (AI) systems that leverage advanced computer vision (CV) pipelines and Vision-Language Models (VLMs) to "spectate" the game exactly as a human observer would1.

This comprehensive literature review evaluates the current landscape of real-time AI video game assistants. It dissects the critical architectural trade-offs between API dependency, EULA vulnerabilities, and non-invasive computer vision. By synthesizing recent statistical advancements in Human-Computer Interaction (HCI), real-time User Interface (UI) detection (including precise mean Average Precision metrics), streaming VLM architectures, and edge-inference hardware constraints, this report defines the design implications necessary to engineer an ideal, game-agnostic gameplay assistant capable of adapting to complex environments like Grand Theft Auto V with sub-second latency.

## The Commercial Landscape of Real-Time PC Gaming Assistants

The commercial market for PC gaming assistants is currently bifurcated. On one side are legacy analytics platforms relying on structured data extraction; on the other are emerging AI-native platforms focused on visual heuristics and multimodal companionship.

### Analytics-Driven Platforms: Mobalytics and Overwolf

Tools such as Mobalytics, built primarily upon the Overwolf overlay framework, represent the traditional structured-data paradigm. They operate by tapping into Live Client APIs (LCUs) provided directly by game developers to fetch highly granular telemetry, such as exact player coordinates and ability cooldowns5. Recent advancements include integrating standardized data bridges—like the OP.GG Gaming Data Model Context Protocol (MCP) Server—to bypass individualized, heavily rate-limited REST APIs and pull match histories and champion analyses directly into LLM contexts7.

While highly effective for competitive esports, user sentiment highlights a profound vulnerability: total reliance on game developer architecture. When studios deprecate or alter their APIs, these tools suffer catastrophic failures. For instance, undocumented structural changes to Riot Games' internal binaries since patch 9.1 resulted in critical arrays like "effect" and "effectBurn" (which track champion damage values) persistently returning null or zeroed values, forcing developers to reverse-engineer 32-bit FNV-1a hashed .bin.json files simply to restore basic overlay functionality8. Furthermore, these tools are inherently genre-locked; an overlay built for one game's API possesses zero utility in an unsupported title1.

### Conversational and Vision-Based AI: Questie AI

Occupying the modern AI spectrum is Questie AI, designed to provide real-time voice advice and companionship utilizing over 25 customizable LLM and voice models3. Questie AI operates via screen capture, utilizing vision models to spectate the gameplay and fusing this visual input with persistent memory to act as a roleplay partner or coach3. While effective for immersion and streamer engagement, the practical utility of pure cloud-based conversational tools is heavily bound by latency and their underlying training data. In highly complex mechanical situations, their tactical advice frequently devolves into generic platitudes rather than mathematically optimal guidance3.

### Hardware-Integrated Agentic Assistants: Razer Ava and Nvidia Project G-Assist

The most sophisticated advancements are driven by hardware vendors integrating AI at the GPU and OS levels. Nvidia's Project G-Assist takes visual snapshots of the active game window and processes them via localized SLMs (Small Language Models) accelerated by RTX hardware11. G-Assist demonstrates deep hardware synergy, capable of dynamically undervolting the GPU to optimize performance-per-watt while rigorously respecting a target frame rate12. Similarly, Razer Ava functions as an agentic desk companion that can translate intent into goal-driven, multi-step workflows across applications (e.g., launching tools and preparing broadcast settings autonomously), bridging the gap between passive observation and active desktop execution13.

## The Risk Profile: Anti-Cheat, EULA Violations, and Privacy

The fundamental architectural divide in gaming assistants lies between invasive data extraction and non-invasive visual perception. This dichotomy dictates a tool's safety across three distinct risk categories: anti-cheat detection, legal/ToS enforcement, and user privacy.

### The Existential Threat of Memory Reading and Anti-Cheat Bans

When official APIs are unavailable, invasive applications attempt to extract data by reading the game's allocated physical memory (RAM) utilizing user-mode functions like ReadProcessMemory or kernel-mode drivers16. Modern kernel-level anti-cheat engines rigorously monitor memory access patterns. A companion app that reads memory to track a minimap position is functionally indistinguishable from a malicious aimbot, subjecting users to an unacceptable risk of permanent account bans1.

### EULA and Terms of Service (ToS) Violations

Beyond automated anti-cheat software, developers enforce strict End-User License Agreements (EULAs) and Terms of Service. A game publisher retains absolute proprietary rights over its source code, assets, and UI17. Modifying game files, injecting code, or laying unauthorized commercial interfaces over a game can be legally classified as the creation of unauthorized derivative works or explicit EULA violations (such as the explicit prohibition of reverse engineering or intercepting digital content)17.

### Privacy Implications of Continuous Screen Capture

A system that achieves game-agnosticism by continuously capturing the display output (e.g., via Windows Graphics Capture) inherently raises data-handling concerns. A system watching the game is also potentially observing desktop notifications, private chat overlays, or background applications. Mitigating this risk requires strict edge-inference (local processing), ensuring that raw frame buffers are never transmitted to cloud servers and that context fusion happens entirely on the user's local hardware.

## Grounding the Scope: Grand Theft Auto V (GTA 5) as a Representative Title

To validate the efficacy of a game-agnostic visual assistant, the prototype must be tested against a complex, information-dense environment. Grand Theft Auto V (GTA 5) serves as an ideal representative title1. GTA 5 features a highly dynamic HUD that includes a multi-state health and armor bar, a complex circular minimap with GPS routing, dynamic objective text, and wanted-level indicators21.

Because GTA 5's interface blends essential combat metrics with spatial navigation and narrative prompts—often nested in a heterodiegetic (external) HUD layer—successfully parsing this environment purely through visual perception proves the viability of a non-invasive architecture22. If a computer vision pipeline can accurately track GTA 5's shifting minimap blips and stat bars without hooking into Rockstar's proprietary engine memory, the logic fundamentally transfers to other complex AAA titles22.

## Hardware Constraints and On-Device Edge Inference

Deploying an AI assistant that analyzes screen captures in real time on a consumer-grade PC (e.g., constrained to 16GB of system RAM and a standard gaming GPU) precludes the use of massive cloud-based LLMs due to latency and the aforementioned privacy risks1.

To operate within these strict hardware constraints, the system must utilize heavily optimized Small Language Models (SLMs). Current empirical testing shows that running unoptimized general-purpose vision models (like Qwen3-VL-8B) concurrently with a 3D game consumes approximately 29 GB of VRAM, making them entirely unfeasible for edge deployment on standard consumer laptops24.

Conversely, models engineered for specific tasks demonstrate profound efficiency. CombatVLA, a 3-Billion parameter Vision-Language-Action model, relies on a three-stage progressive learning paradigm25. By employing an Action-of-Thought (AoT) prompting structure combined with a <TRUNC> early-exit strategy (discarding unnecessary text generation the millisecond an actionable command is formed), CombatVLA achieves sub-second reasoning and a 50-fold acceleration in combat parsing compared to standard VLMs25. This proves that highly focused, quantized SLMs can easily operate within consumer hardware budgets while the game runs in parallel.

## Academic Grounding: Real-time UI Detection Performance Metrics

Accurate UI element detection forms the backbone of a non-invasive assistant. Because GUI elements often overlap and feature extreme aspect ratios compared to natural images, generic object detectors frequently fail26.

Recent empirical evaluations of YOLO (You Only Look Once) architectures tailored for GUI detection show massive improvements in statistical reliability. For instance, the YOLOv5R7s variant demonstrated an 18.41% improvement in Average Precision (AP@0.5) over prior state-of-the-art GUI detection methods26. Furthermore, custom lightweight architectures like SE76-PP-YOLO, which integrate Complete Intersection over Union (C-IoU) and attention mechanisms, have achieved an exceptional 93.1% recall and a peak mAP@0.5 of 94.1% for UI component recognition27.

Speed is equally critical. The recently proposed YOLOv12-N model achieves 40.6% mAP while operating at a staggering inference latency of just 1.64 ms on a standard T4 GPU28. Similarly, specialized on-device UI detectors like YOLO26-Medium (operating at 22 million parameters) are capable of localized screen-parsing within ~50ms to 288ms depending on the target scale29. Integrating these high-speed, high-mAP models ensures the perception pipeline does not bottleneck the reasoning engine.

## Academic Grounding: Streaming VLMs and Visual Perception

Once UI elements are detected, the visual data must be continuously interpreted. Standard VLMs evaluated using static, turn-based benchmarks (such as VS-Bench) reveal a stark limitation: while perception is strong, strategic theory-of-mind reasoning is poor, with the best-performing commercial models attaining only 46.6% prediction accuracy and a 31.4% normalized return when guessing optimal next actions in multi-agent environments30.

Furthermore, real-time gameplay is a continuous video stream. Translating static VLM capabilities into real-time environments requires "streaming video understanding" architectures. Proposals like the V-Rex architecture utilize dynamic Key-Value (KV) cache retrieval to accelerate streaming video LLM processing31. This prevents the system from redundantly re-encoding static background elements frame-by-frame, drastically reducing inference latency and allowing the context fusion module to maintain an active, temporally stable memory of the gameplay session31.

## HCI, Overlay Rendering Overhead, and Cognitive Load

Delivering complex text to a player actively engaged in a firefight risks exacerbating the very cognitive overload the tool is meant to solve. According to Cognitive Load Theory, human working memory is severely limited32. When a player must divide their visual attention between the center of the screen (gameplay) and a distant UI element (the assistant's overlay), they experience the "split-attention effect," which dramatically increases extraneous cognitive load32.

HCI research demonstrates that spatially contiguous overlays—placing guidance at the direct point of interaction—minimize gaze shifts and reduce cognitive friction33. Empirical studies testing Augmented Reality (AR) instructional overlays versus spatially separated instructions found that integrated overlays reduced task completion time by 14.94% for highly demanding tasks35.

However, the rendering architecture of this overlay is technically vital. Web-based frameworks like Electron (utilized heavily by apps like Medal or Overwolf) are notoriously resource-heavy. Internal application initialization logs reveal that Electron overlays suffer from input latency (averaging 5.4ms to 11ms for API responses) and can cause catastrophic frame pacing degradation36. In mixed-refresh multi-monitor setups, relying on Chromium rendering pipelines can drop a host application's performance from a native 5ms/frame down to a sluggish 60ms/frame due to GPU resource contention38.

Therefore, an ideal gameplay assistant must utilize a lightweight, native DirectX overlay (e.g., using C++ Immediate Mode GUI frameworks and WS_EX_LAYERED transparent windows) to deliver spatially contiguous visual cues without throttling the host game's rendering pipeline16.

## System Evaluation Methodology

To transition from theoretical design to a validated prototype, the system must be rigorously evaluated against objective metrics and user studies:

Latency and Pipeline Efficiency: The computer vision pipeline should be benchmarked using Structural Similarity Index Measure (SSIM) frame differencing to ensure heavy detection models only trigger during significant visual changes39.

Detection Stability: The accuracy of the HUD extraction (e.g., GTA 5 minimap and health bar tracking) must be quantified using mAP@0.5 and Intersection over Union (IoU) metrics across continuous video frames to ensure stability27.

User Utility and Cognitive Load: The usefulness of the adaptive guidance overlay should be measured using eye-tracking data (to track gaze shifts) coupled with the NASA Task Load Index (NASA-TLX) to objectively quantify post-task reductions in mental workload, frustration, and split-attention41.

## Conclusion

The trajectory of AI video game assistants is irrevocably shifting toward non-invasive multimodal systems. While traditional analytics platforms are vulnerable to broken APIs and anti-cheat bans, and cloud-based conversational tools suffer from latency and privacy risks, recent academic breakthroughs offer a clear path forward. By synthesizing high-mAP UI object detection (like YOLOv12), streaming VLM architectures optimized for strict consumer VRAM limits (like CombatVLA's 3B parameters), and low-latency native DirectX overlays, it is entirely feasible to construct an assistant like AEGIS. Such a system can spectate, understand, and provide sub-second tactical guidance in complex titles like GTA 5 entirely from rendered pixels, delivering unparalleled situational awareness securely and seamlessly.

#### Works cited

Project guidence..docx

Recreating Grand Theft Auto V (MVP Scope) | PDF - Scribd, https://www.scribd.com/document/1029713849/Recreating-Grand-Theft-Auto-v-MVP-Scope

Questie AI Game Companion Review 2026 – Pricing & Alternatives | AIapps, https://www.aiapps.com/items/questie-ai-game-companion/

Computer vision in autism spectrum disorder research: a systematic review of published studies from 2009 to 2019 - PMC, https://pmc.ncbi.nlm.nih.gov/articles/PMC7528087/

Overwolf API Overview, https://dev.overwolf.com/ow-native/reference/ow-api-overview

League of Legends data scraping the hard and tedious way for fun | Henry Zhu, https://maknee.github.io/blog/2025/League-Data-Scraping/

Unlock Real-Time Game Insights: Your Ultimate Guide to the Official OP.GG Gaming Data MCP Server - Skywork, https://skywork.ai/skypage/en/real-time-game-insights/1981912306334928896

Riot's developer API have been completely broken for years : r/leagueoflegends - Reddit, https://www.reddit.com/r/leagueoflegends/comments/18wq2q2/riots_developer_api_have_been_completely_broken/

AI Chat for Games - Questie - App Store, https://apps.apple.com/us/app/ai-chat-for-games-questie/id6767389926?l=zh-Hans-CN

AI Game Companion - Questie – Apps on Google Play, https://play.google.com/store/apps/details?id=ai.questie.www.twa&hl=en_IN

Project G-Assist | AI Assistant - NVIDIA, https://www.nvidia.com/en-in/software/nvidia-app/g-assist/

g-assist-ai-assistant - NVIDIA, https://www.nvidia.com/en-us/geforce/news/gfecnt/20246/g-assist-ai-assistant/

Razer AVA: 3D Hologram AI Companion | Razer United States, https://www.razer.com/razer-ava

Razer Unveils AI-Powered Future of Play at GDC 2026, https://www.razer.com/newsroom/company-news/razer-at-gdc-2026

Razer AVA Goes Agentic: A New Chapter at GDC 2026 - Blog, https://www.razer.com/blog/razer-ava-goes-agentic-a-new-chapter-at-gdc-2026

gmh5225/awesome-game-security - 在线工具, https://tool.lu/skill/gwjPVF

BATTLEBIT END USER LICENSE AGREEMENT - Steam, https://store.steampowered.com/eula/1611740_eula_0

Cheating, Hacks, and Anti-Cheat Systems: Legal Rights of Game, https://advocateturkey.com/2026/03/30/cheating-hacks-and-anti-cheat-systems-legal-rights-of-game-publishers/

Computer game licences: The EULA and its discontents | Request PDF - ResearchGate, https://www.researchgate.net/publication/332219135_Computer_game_licences_The_EULA_and_its_discontents

Fairness, Copyright, and Video Games: Hate the Game, Not the Player - The Fordham Law Archive of Scholarship and History, https://ir.lawnet.fordham.edu/cgi/viewcontent.cgi?article=1775&context=iplj

GTA V Game Design Document Overview | PDF - Scribd, https://www.scribd.com/document/905397827/GTA-V-GDD

The Impact of User Interfaces for the Enhancement of Narrative Elements of a Video Game - CEUR-WS.org, https://ceur-ws.org/Vol-2246/GHItaly18_paper_03.pdf

GTA5 - find the prompt in the description - YouTube, https://www.youtube.com/shorts/8YpCxz30nKE

BEEP AI v2.0 - Tiered Perception Architecture : r/Kenshi - Reddit, https://www.reddit.com/r/Kenshi/comments/1p8k893/beep_ai_v20_tiered_perception_architecture/

CombatVLA: An Efficient Vision-Language-Action Model for Combat Tasks in 3D Action Role-Playing Games - arXiv, https://arxiv.org/html/2503.09527v2

GUI Element Detection Using SOTA YOLO Deep Learning Models - arXiv, https://arxiv.org/html/2408.03507v1

Application of Optimized GUI Component Identification Method in User Interface Graphic Design, https://www.engineeringletters.com/issues_v33/issue_11/EL_33_11_06.pdf

[2502.12524] YOLOv12: Attention-Centric Real-Time Object Detectors - arXiv, https://arxiv.org/abs/2502.12524

okigan/yolo-screensense - GitHub, https://github.com/okigan/yolo-screensense

VS-Bench: Evaluating VLMs for Strategic Abilities in Multi-Agent Environments - NICS-EFC, https://nicsefc.ee.tsinghua.edu.cn/nics_file/pdf/562a0749-3001-40f7-a890-b121c930fc0d.pdf

[2512.12284] V-Rex: Real-Time Streaming Video LLM Acceleration via Dynamic KV Cache Retrieval - arXiv, https://arxiv.org/abs/2512.12284

User interaction: Cognitive Load Management: Cognitive Load Management for Better User Interaction - FasterCapital, https://fastercapital.com/content/User-interaction--Cognitive-Load-Management--Cognitive-Load-Management-for-Better-User-Interaction.html

The split attention principle in multimedia learning - ResearchGate, https://www.researchgate.net/publication/285315734_The_split_attention_principle_in_multimedia_learning

AutoCue: Multimodal LLM-Assisted Externalization of Implicit Inputs as Instructional Visual Cues in Screencast Tutorials - arXiv, https://arxiv.org/html/2608.04910v1

Exploring Attention and Cognitive Load in Virtual Assembly: Simulated Augmented and Diminished Reality Effects - ResearchGate, https://www.researchgate.net/publication/403042268_Exploring_Attention_and_Cognitive_Load_in_Virtual_Assembly_Simulated_Augmented_and_Diminished_Reality_Effects

Medal App Initialization Log | PDF | File System | Computer Keyboard - Scribd, https://www.scribd.com/document/828716386/Medal-Log-20250201

Medal Log and Hotkey Settings Overview | PDF | Keyboard Shortcut - Scribd, https://www.scribd.com/document/740216851/Medal-Log-20240522

low ms/frame when sharing/recording screen · Issue #8218 · ocornut/imgui - GitHub, https://github.com/ocornut/imgui/issues/8218

Screencast-Based Analysis of User-Perceived GUI Responsiveness - arXiv, https://arxiv.org/html/2508.01337v1

GUI Element Detection from Mobile UI Images Using YOLOv5 - ResearchGate, https://www.researchgate.net/publication/362694426_GUI_Element_Detection_from_Mobile_UI_Images_Using_YOLOv5

Real-Time Cognitive Training Adaptation based on Eye-Tracking and Physiological Data in Virtual Reality - arXiv, https://arxiv.org/html/2512.17882v3

A critical analysis of cognitive load measurement methods for evaluating the usability of different types of interfaces - arXiv, https://arxiv.org/pdf/2402.11820

Exploring LLM-Powered Tutoring Systems in a Game-Based, https://repository.tugraz.at/publications/marc21/3vtj0-6gv05/files/97239.pdf?download=1

---

# Source: AEGIS Literature Review — Final

The Evolution of Real-Time AI Gameplay Assistants: From Memory-Dependent Overlays to Non-Invasive Multimodal Systems

Literature Review & Market Analysis — Project AEGIS (AI Gameplay Intelligence System) | Group TYAIEC102, Trailblazers | Guide: Dr. Tushar Mote

# Introduction to the Cognitive Demands of Modern Gameplay

This literature review evaluates the current landscape of real-time AI video game assistants. It dissects the critical architectural trade-offs between API dependency, EULA vulnerabilities, and non-invasive computer vision. By synthesizing recent advancements in Human-Computer Interaction (HCI), real-time User Interface (UI) detection, streaming VLM architectures, and edge-inference hardware constraints, this report defines the design implications necessary to engineer an ideal, game-agnostic gameplay assistant capable of adapting to complex environments like Grand Theft Auto V with sub-second latency.

# The Commercial Landscape of Real-Time PC Gaming Assistants

## Analytics-Driven Platforms: Mobalytics and Overwolf

Tools such as Mobalytics, built primarily upon the Overwolf overlay framework, represent the traditional structured-data paradigm. They operate by tapping into Live Client APIs (LCUs) provided directly by game developers to fetch highly granular telemetry, such as exact player coordinates and ability cooldowns2. Recent advancements include integrating standardized data bridges — like the OP.GG Gaming Data Model Context Protocol (MCP) Server — to bypass individualized, heavily rate-limited REST APIs and pull match histories and champion analyses directly into LLM contexts4.

While highly effective for competitive esports, user sentiment highlights a profound vulnerability: total reliance on game developer architecture. When studios deprecate or alter their APIs, these tools suffer catastrophic failures. Independent reverse-engineering efforts documenting Riot Games' client data have noted that undocumented structural changes to internal data arrays have historically forced community developers to reverse-engineer hashed internal game files simply to restore basic overlay functionality3,5. Furthermore, these tools are inherently genre-locked; an overlay built for one game's API possesses zero utility in an unsupported title1.

## Conversational and Vision-Based AI: Questie AI

Occupying the modern AI spectrum is Questie AI, designed to provide real-time voice advice and companionship utilizing a large catalogue of customizable LLM and voice models6,7,8. Questie AI operates via screen capture, utilizing vision models to spectate the gameplay and fusing this visual input with persistent memory to act as a roleplay partner or coach6. While effective for immersion and streamer engagement, the practical utility of pure cloud-based conversational tools is heavily bound by latency and their underlying training data. In highly complex mechanical situations, their tactical advice frequently devolves into generic platitudes rather than mathematically optimal guidance6.

## Hardware-Integrated Agentic Assistants: Razer Ava and Nvidia Project G-Assist

The most sophisticated advancements are driven by hardware vendors integrating AI at the GPU and OS levels. Nvidia's Project G-Assist takes visual snapshots of the active game window and processes them via localized SLMs (Small Language Models) accelerated by RTX hardware9. G-Assist demonstrates deep hardware synergy, capable of dynamically undervolting the GPU to optimize performance-per-watt while rigorously respecting a target frame rate10. Similarly, Razer Ava functions as an agentic desk companion that can translate intent into goal-driven, multi-step workflows across applications (e.g., launching tools and preparing broadcast settings autonomously), bridging the gap between passive observation and active desktop execution11,12,13.

# The Risk Profile: Anti-Cheat, EULA Violations, and Privacy

## The Existential Threat of Memory Reading and Anti-Cheat Bans

When official APIs are unavailable, invasive applications attempt to extract data by reading the game's allocated physical memory (RAM) utilizing user-mode functions like ReadProcessMemory or kernel-mode drivers14. Modern kernel-level anti-cheat engines rigorously monitor memory access patterns. A companion app that reads memory to track a minimap position is functionally indistinguishable from a malicious aimbot, subjecting users to an unacceptable risk of permanent account bans1.

## EULA and Terms of Service (ToS) Violations

Beyond automated anti-cheat software, developers enforce strict End-User License Agreements (EULAs) and Terms of Service. A game publisher retains proprietary rights over its source code, assets, and UI, and standard EULAs typically prohibit reverse engineering, decompilation, and the interception or overlaying of proprietary digital content15,16. Modifying game files, injecting code, or laying unauthorized commercial interfaces over a game can therefore be classified as the creation of unauthorized derivative works, independent of whether the activity is also flagged by anti-cheat software17.

## Privacy Implications of Continuous Screen Capture

A system that achieves game-agnosticism by continuously capturing the display output (e.g., via Windows Graphics Capture) inherently raises data-handling concerns. A system watching the game is also potentially observing desktop notifications, private chat overlays, or background applications. Mitigating this risk requires strict edge-inference (local processing), ensuring that raw frame buffers are never transmitted to cloud servers and that context fusion happens entirely on the user's local hardware1.

# Grounding the Scope: Grand Theft Auto V (GTA 5) as a Representative Title

To validate the efficacy of a game-agnostic visual assistant, the prototype must be tested against a complex, information-dense environment. Grand Theft Auto V (GTA 5) serves as an ideal representative title1. GTA 5 features a highly dynamic HUD that includes a multi-state health and armor bar, a complex circular minimap with GPS routing, dynamic objective text, and wanted-level indicators — all rendered entirely within the game's own UI layer rather than through an external, developer-exposed data feed.

Because GTA 5's interface blends essential combat metrics with spatial navigation and narrative prompts — often nested in an externally-facing HUD layer distinct from the diegetic game world — successfully parsing this environment purely through visual perception demonstrates the viability of a non-invasive architecture18. If a computer vision pipeline can accurately track GTA 5's shifting minimap blips and stat bars without hooking into Rockstar's proprietary engine memory, the underlying perception approach plausibly transfers to other complex AAA titles with comparably dense HUDs18.

# Hardware Constraints and On-Device Edge Inference

To operate within these strict hardware constraints, the system must utilize heavily optimized Small Language Models (SLMs). Published hardware specifications show that even a mid-sized, general-purpose vision-language model such as Qwen3-VL-8B requires approximately 18–20 GB of VRAM for standard FP16 inference19. On a consumer GPU that must simultaneously render the host game at a stable frame rate, this leaves little to no spare memory budget, making unquantized general-purpose VLMs impractical for concurrent, real-time edge deployment on standard consumer laptops without aggressive quantization (e.g., INT8/INT4).

Conversely, models engineered for specific tasks demonstrate profound efficiency. CombatVLA, a 3-Billion parameter Vision-Language-Action model, relies on a three-stage progressive learning paradigm20. By employing an Action-of-Thought (AoT) prompting structure combined with a <TRUNC> early-exit strategy (discarding unnecessary text generation the moment an actionable command is formed), CombatVLA achieves sub-second reasoning and a reported 50-fold acceleration in combat parsing compared to standard VLMs20. This demonstrates that highly focused, quantized SLMs can operate within consumer hardware budgets while the game runs in parallel, in contrast to general-purpose VLMs.

# Academic Grounding: Real-Time UI Detection Performance Metrics

Accurate UI element detection forms the backbone of a non-invasive assistant. Because GUI elements often overlap and feature extreme aspect ratios compared to natural images, generic object detectors frequently underperform without domain-specific tuning21.

Recent empirical evaluations of YOLO (You Only Look Once) architectures tailored for GUI detection show substantial improvements in statistical reliability. Fine-tuned YOLO variants have demonstrated double-digit percentage improvements in Average Precision (AP@0.5) over prior general-purpose GUI detection baselines21,25. Furthermore, custom lightweight architectures that integrate Complete Intersection over Union (C-IoU) loss and attention mechanisms have reported recall above 90% and mAP@0.5 in the low-to-mid 90s for UI component recognition22.

Speed is equally critical. The recently proposed YOLOv12-N model reports competitive mAP while operating at inference latencies in the low single-digit milliseconds on a standard T4 GPU23. Similarly, specialized on-device UI detectors are capable of localized screen-parsing within tens to a few hundred milliseconds depending on the target scale and model size24. Integrating such high-speed, high-mAP models helps ensure the perception pipeline does not bottleneck the downstream reasoning engine.

# Academic Grounding: Streaming VLMs and Visual Perception

Once UI elements are detected, the visual data must be continuously interpreted. Standard VLMs evaluated using static, turn-based benchmarks (such as VS-Bench) reveal a notable limitation: while perception is comparatively strong, strategic theory-of-mind reasoning is markedly weaker, with even strong commercial models achieving well under 50% prediction accuracy when inferring optimal next actions in multi-agent environments26.

Furthermore, real-time gameplay is a continuous video stream rather than a series of isolated frames. Translating static VLM capabilities into real-time environments requires “streaming video understanding” architectures. Proposals such as the V-Rex architecture utilize dynamic Key-Value (KV) cache retrieval to accelerate streaming video LLM processing27. This avoids redundantly re-encoding static background elements on every frame, reducing inference latency and allowing a context fusion module to maintain an active, temporally stable memory of the gameplay session27.

# HCI, Overlay Rendering Overhead, and Cognitive Load

Delivering complex text to a player actively engaged in a firefight risks exacerbating the very cognitive overload the tool is meant to solve. Cognitive Load Theory holds that human working memory is severely limited in both capacity and duration28. When a player must divide their visual attention between the center of the screen (gameplay) and a spatially distant UI element (the assistant's overlay), they experience the “split-attention effect,” which measurably increases extraneous cognitive load and can impair performance on the primary task28.

HCI research on multimedia learning and instructional design similarly demonstrates that spatially contiguous information sources — placing guidance near the direct point of interaction rather than at a separated location — reduce the need for gaze shifts and lower extraneous cognitive load29. Empirical studies comparing integrated Augmented Reality (AR) instructional overlays against spatially separated instructions have found measurable reductions in task completion time and reported workload for integrated overlays on demanding tasks30.

The rendering architecture of the overlay itself is also technically significant. Overwolf's own published framework comparison illustrates the cost of a web-based overlay stack: its Chromium/Electron-based ow-electron framework reports roughly 0.2% CPU usage at idle and up to 3% during active window interaction, against approximately 0.1% and 0.5% respectively for its lighter native (CEF-based) platform, with peak RAM consumption of around 420 MB versus 380 MB31. While individually modest, this overhead compounds when an overlay must repaint continuously alongside a 3D game that is already competing for the same CPU and GPU resources, and can be measured directly via frame-time and perceived-responsiveness analysis techniques developed for screencast and GUI-performance research32.

Therefore, an ideal gameplay assistant should favor a lightweight, native rendering path (e.g., a DirectX- or Direct2D-based overlay using an Immediate Mode GUI framework and a transparent, layered window) over a full Chromium/Electron stack, in order to deliver spatially contiguous visual cues without materially throttling the host game's own rendering pipeline14.

# System Evaluation Methodology

Latency and Pipeline Efficiency:  The computer vision pipeline should be benchmarked using Structural Similarity Index Measure (SSIM) frame differencing to ensure heavy detection models only trigger during significant visual changes32.

Detection Stability:  The accuracy of the HUD extraction (e.g., GTA 5 minimap and health-bar tracking) should be quantified using mAP@0.5 and Intersection over Union (IoU) metrics across continuous video frames to assess temporal stability22.

User Utility and Cognitive Load:  The usefulness of the adaptive guidance overlay should be measured using eye-tracking data (to track gaze shifts) coupled with the NASA Task Load Index (NASA-TLX) to quantify post-task changes in mental workload, frustration, and split-attention33,34.

# Conclusion

The trajectory of AI video game assistants is shifting toward non-invasive multimodal systems. While traditional analytics platforms are vulnerable to broken APIs and anti-cheat bans, and cloud-based conversational tools suffer from latency and privacy risks, recent academic work offers a credible path forward. By combining high-mAP UI object detection, streaming VLM architectures optimized for tight consumer VRAM budgets, and low-overhead native overlay rendering, it is plausible to construct a non-invasive, game-agnostic assistant such as AEGIS — one that observes, interprets, and delivers low-latency tactical guidance in complex titles like GTA 5 entirely from rendered pixels, without reading game memory or violating platform terms of service.

Works Cited

1. Project AEGIS — PBL Synopsis, MIT School of Computing (internal project guidance document).

2. Overwolf API Overview, https://dev.overwolf.com/ow-native/reference/ow-api-overview

3. Zhu, H. “League of Legends data scraping the hard and tedious way for fun.”, https://maknee.github.io/blog/2025/League-Data-Scraping/

4. “Unlock Real-Time Game Insights: The Official OP.GG Gaming Data MCP Server.” Skywork., https://skywork.ai/skypage/en/real-time-game-insights/1981912306334928896

5. “Riot's developer API have been completely broken for years.” r/leagueoflegends., https://www.reddit.com/r/leagueoflegends/comments/18wq2q2/riots_developer_api_have_been_completely_broken/

6. “Questie AI Game Companion Review 2026 – Pricing & Alternatives.” AIapps., https://www.aiapps.com/items/questie-ai-game-companion/

7. “AI Chat for Games – Questie.” App Store., https://apps.apple.com/us/app/ai-chat-for-games-questie/id6767389926

8. “AI Game Companion – Questie.” Google Play., https://play.google.com/store/apps/details?id=ai.questie.www.twa

9. “Project G-Assist.” NVIDIA., https://www.nvidia.com/en-in/software/nvidia-app/g-assist/

10. “g-assist-ai-assistant.” NVIDIA GeForce News., https://www.nvidia.com/en-us/geforce/news/gfecnt/20246/g-assist-ai-assistant/

11. “Razer AVA: 3D Hologram AI Companion.” Razer., https://www.razer.com/razer-ava

12. “Razer Unveils AI-Powered Future of Play at GDC 2026.” Razer Newsroom., https://www.razer.com/newsroom/company-news/razer-at-gdc-2026

13. “Razer AVA Goes Agentic: A New Chapter at GDC 2026.” Razer Blog., https://www.razer.com/blog/razer-ava-goes-agentic-a-new-chapter-at-gdc-2026

14. gmh5225/awesome-game-security., https://github.com/gmh5225/awesome-game-security

15. “BattleBit End User License Agreement.” Steam., https://store.steampowered.com/eula/1611740_eula_0

16. “Computer game licences: The EULA and its discontents.” ResearchGate., https://www.researchgate.net/publication/332219135_Computer_game_licences_The_EULA_and_its_discontents

17. “Fairness, Copyright, and Video Games: Hate the Game, Not the Player.” Fordham Intellectual Property, Media and Entertainment Law Journal., https://ir.lawnet.fordham.edu/cgi/viewcontent.cgi?article=1775&context=iplj

18. “The Impact of User Interfaces for the Enhancement of Narrative Elements of a Video Game.” CEUR-WS.org, Vol. 2246., https://ceur-ws.org/Vol-2246/GHItaly18_paper_03.pdf

19. wangkanai/qwen3-vl-8b-instruct — model card and hardware requirements. Hugging Face., https://huggingface.co/wangkanai/qwen3-vl-8b-instruct

20. “CombatVLA: An Efficient Vision-Language-Action Model for Combat Tasks in 3D Action Role-Playing Games.” arXiv:2503.09527., https://arxiv.org/abs/2503.09527

21. “GUI Element Detection Using SOTA YOLO Deep Learning Models.” arXiv:2408.03507., https://arxiv.org/abs/2408.03507

22. “Application of Optimized GUI Component Identification Method in User Interface Graphic Design.” Engineering Letters, 33(11)., https://www.engineeringletters.com/issues_v33/issue_11/EL_33_11_06.pdf

23. “YOLOv12: Attention-Centric Real-Time Object Detectors.” arXiv:2502.12524., https://arxiv.org/abs/2502.12524

24. okigan/yolo-screensense., https://github.com/okigan/yolo-screensense

25. “GUI Element Detection from Mobile UI Images Using YOLOv5.” ResearchGate., https://www.researchgate.net/publication/362694426_GUI_Element_Detection_from_Mobile_UI_Images_Using_YOLOv5

26. “VS-Bench: Evaluating VLMs for Strategic Abilities in Multi-Agent Environments.” NICS-EFC, Tsinghua University., https://nicsefc.ee.tsinghua.edu.cn/nics_file/pdf/562a0749-3001-40f7-a890-b121c930fc0d.pdf

27. “V-Rex: Real-Time Streaming Video LLM Acceleration via Dynamic KV Cache Retrieval.” arXiv:2512.12284., https://arxiv.org/abs/2512.12284

28. Chandler, P., & Sweller, J. “The Split-Attention Effect as a Factor in the Design of Instruction.” British Journal of Educational Psychology, 62(2), 1992., https://www.davidlewisphd.com/courses/EDD8121/readings/1992-ChandlerSweller-SplitAttention.pdf

29. “The split attention principle in multimedia learning.” ResearchGate., https://www.researchgate.net/publication/285315734_The_split_attention_principle_in_multimedia_learning

30. “Exploring Attention and Cognitive Load in Virtual Assembly: Simulated Augmented and Diminished Reality Effects.” ResearchGate., https://www.researchgate.net/publication/403042268_Exploring_Attention_and_Cognitive_Load_in_Virtual_Assembly_Simulated_Augmented_and_Diminished_Reality_Effects

31. “Framework Overview — Overwolf Native vs. Overwolf Electron Performance Comparison.” Overwolf Developer Documentation., https://dev.overwolf.com/ow-native/getting-started/onboarding-resources/framework-overview/

32. “Screencast-Based Analysis of User-Perceived GUI Responsiveness.” arXiv:2508.01337., https://arxiv.org/abs/2508.01337

33. “Real-Time Cognitive Training Adaptation based on Eye-Tracking and Physiological Data in Virtual Reality.” arXiv:2512.17882., https://arxiv.org/abs/2512.17882

34. “A critical analysis of cognitive load measurement methods for evaluating the usability of different types of interfaces.” arXiv:2402.11820., https://arxiv.org/abs/2402.11820

---

# Source: MITSOC PBL AEGIS Synopsis

Synopsis

On

AEGIS: AI Gameplay Intelligence System

Group ID: TYAIEC102

Team Details

| Enrolment No. | Name of Student | Class |
| --- | --- | --- |
| ADT24SOCB1277 | Tanishk Kailas Patil (Team Leader) | TYAIEC - 1 |
| ADT24SOCB0474 | Hrishikesh Rajaram Mhaske | TYAIA - 5 |
| ADT24SOCB0778 | Prajwal Umesh Birari | TYAIEC - 1 |
| ADT24SOCB1406 | Vivek Bhagwan Phad | TYAIA - 10 |

Under the Guidance of

Prof. Dr. Tushar Mote

Department of Computer Science & Engineering

MIT School of Computing

TY | Sem-5 | A. Y. 2026-27

1. Title of the Project

AEGIS: AI Gameplay Intelligence System : - Real-Time Multimodal Assistance for Complex Games

2. Abstract (150–200 words)

Modern AAA games present players with fast-paced, information-dense environments where tracking threats, objectives, and optimal strategies in real time is cognitively demanding. AEGIS (AI Gameplay Intelligence System) addresses this by non-invasively observing the on-screen game state through computer vision and interpreting it using multimodal AI, without modifying game memory or code  keeping it anti-cheat safe and game-agnostic. The system captures live gameplay frames, detects and interprets HUD elements, enemies, objectives, and environmental cues, and fuses this visual context with a multimodal reasoning engine to generate personalized tactical, strategic, and narrative guidance in real time. Suggestions are delivered through a lightweight overlay, adapting to the player's situation as it evolves. Unlike static wikis or game-specific companion apps, AEGIS works purely from what is visible on screen, making it portable across titles and genres. The expected outcome is a functional prototype demonstrating low-latency, context-aware assistance validated across multiple game titles, improving situational awareness and decision-making for players without altering the underlying game.

3. Introduction / Background

• Complex AAA games (RPGs, tactical shooters, open-world titles) often overwhelm players with simultaneous information, health, enemy positions, objectives, resource states, and narrative context.

• Existing support tools are largely static: wikis, walkthroughs, YouTube guides, or in-game tutorials that don't adapt to what's actually happening on a player's screen in real time.

• A few companion tools exist (e.g., overlay stat trackers, build guides), but they rely on manual lookup or game-specific APIs/plugins, which breaks the moment the game updates or when used on unsupported titles.

• Recent advances in computer vision (real-time object detection, OCR, segmentation) and multimodal large language models (models that reason jointly over images and text) make it feasible to build a system that "watches" a screen the way a human observer would and gives contextual advice  without hooking into game memory, which risks anti-cheat bans and is not generalizable across titles.

• No existing system combines real-time, non-invasive visual perception of gameplay with multimodal reasoning to deliver personalized, adaptive guidance across different games.

4. Problem Definition

Players in complex, fast-paced AAA games often lack real-time situational awareness of threats, objectives, and optimal strategies, a gap that can be closed by a computer-vision-driven AI system that reads on-screen game state non-invasively and delivers personalized tactical and narrative guidance without modifying game memory.

5. Objectives

1. To design a non-invasive computer vision pipeline that captures and interprets on-screen game state (HUD, enemies, objectives, environment) in real time.

2. To integrate a multimodal AI reasoning engine that fuses visual context with game knowledge to generate tactical, strategic, and narrative suggestions.

3. To build a lightweight overlay interface that delivers guidance to the player without modifying game memory, files, or violating anti-cheat policies.

4. To evaluate the system's latency, accuracy, and usefulness across multiple game genres and titles.

6. Scope of the Project

• The system operates purely on screen-captured video/frames no reading or writing of game memory, no code injection, no use of unofficial game APIs.

• Initial scope covers PC gameplay for representative title: GTA 5 by Rockstar Games.

• Focus is on single-player scenarios for the prototype; multiplayer/team coordination is considered a future extension.

• Out of scope: mobile/console game support, modifying game files, and guaranteeing compatibility with every title on the market.

7. Proposed System

Architecture / Workflow: Screen Capture → Frame Preprocessing → Visual Perception (object detection, OCR, segmentation) → Context Fusion → Multimodal AI Reasoning Engine → Guidance Generation → Overlay Delivery

Modules:

• Vision Perception Module: Captures the screen in real time and detects HUD elements, health/ammo indicators, enemies, objectives, and text via object detection and OCR.

• Context Fusion Module: Aggregates detected visual elements into a structured game-state representation (e.g., “low health, enemy nearby, objective 200m north”).

• AI Reasoning Module: A multimodal model interprets the fused context and generates relevant tactical/strategic/narrative suggestions.

• Guidance Delivery Module: Renders suggestions via a minimal, non-intrusive on-screen overlay (and optionally audio cues).

Advantages over existing systems:

• Game-agnostic — works from vision alone, no per-game integration needed.

• Non-invasive — no memory access, safe from anti-cheat flags.

• Adaptive and personalized — reacts to the player's actual, current situation rather than generic walkthroughs.

8. System Requirements

a. Hardware Requirements

• CPU: Quad-core or higher

• GPU: Dedicated modern GPU (recommended, for real-time inference)

• RAM: 16 GB minimum

• Display capture-capable system (standard PC gaming setup)

b. Software Requirements

• Languages: Python

• Libraries/Frameworks: OpenCV, PyTorch, YOLO (or similar detection model), Tesseract/EasyOCR

• AI: Multimodal LLM (e.g., a vision-language model, either API-based or locally hosted)

• Screen Capture: Windows Graphics Capture API / OBS Virtual Camera

• Overlay: Electron or DirectX-based overlay rendering

• Backend: FastAPI/Flask

• Tools: VS Code, Git

9. Methodology / Implementation Plan (Project Tracker Sheet)

Methodology: Agile (iterative sprints)

1. Literature review & feasibility study

2. Gameplay dataset collection (screen recordings/screenshots from target titles)

3. Vision model selection/fine-tuning for HUD & object detection

4. Multimodal reasoning engine integration

5. Overlay UI development

6. Integration testing across selected game titles

7. Performance evaluation (latency, accuracy) & user feedback

10. Expected Outcome

A functional prototype of AEGIS that captures gameplay in real time, interprets on-screen state, and delivers contextually relevant tactical/strategic guidance through an overlay targeting sub-second latency and validated across at least two different game titles.

11. Applications / Use Cases

• Real-time assistance for casual and new players learning complex games

• Accessibility aid for players who need extra situational support

• Esports/competitive training tool for strategy review

• Companion tool for streamers/content creators

• Onboarding assistant for newly released or unfamiliar titles

12. Future Enhancements / Future Scope

• Voice-based narration of guidance instead of/alongside visual overlay

• Adaptive difficulty coaching based on player skill progression

• Multiplayer/team coordination support

• Console platform support

• Expansion to additional genres (strategy, simulation, etc.)

13. References

1. Redmon, J., et al. "You Only Look Once: Unified, Real-Time Object Detection." CVPR, 2016.

2. Radford, A., et al. "Learning Transferable Visual Models From Natural Language Supervision (CLIP)." ICML, 2021.

3. Relevant papers/documentation on vision-language models (VLMs) and multimodal reasoning.

4. OpenCV and Tesseract OCR official documentation.

---

# Source: Project Guidance

1. MITSOC PBL Synopsis — Content

Group ID: TYAIEC102
Team Name: Trailblazers

| Enrolment No. | Name of Student | Class |
| --- | --- | --- |
| ADT24SOCB1277 | Tanishk Kailas Patil (Team Leader) | TY |
| ADT24SOCB0474 | Hrishikesh Rajaram Mhaske | TY |
| ADT24SOCB0778 | Prajwal Umesh Birari | TY |
| ADT24SOCB1406 | Vivek Bhagwan Phad | TY |

Under the Guidance of: Dr. Tushar Mote

1. Title of the Project

AEGIS: AI Gameplay Intelligence System — Real-Time Multimodal Assistance for Complex Games

2. Abstract (150–200 words)

Modern AAA games present players with fast-paced, information-dense environments where tracking threats, objectives, and optimal strategies in real time is cognitively demanding. AEGIS (AI Gameplay Intelligence System) addresses this by non-invasively observing the on-screen game state through computer vision and interpreting it using multimodal AI, without modifying game memory or code — keeping it anti-cheat safe and game-agnostic. The system captures live gameplay frames, detects and interprets HUD elements, enemies, objectives, and environmental cues, and fuses this visual context with a multimodal reasoning engine to generate personalized tactical, strategic, and narrative guidance in real time. Suggestions are delivered through a lightweight overlay, adapting to the player's situation as it evolves. Unlike static wikis or game-specific companion apps, AEGIS works purely from what is visible on screen, making it portable across titles and genres. The expected outcome is a functional prototype demonstrating low-latency, context-aware assistance validated across multiple game titles, improving situational awareness and decision-making for players without altering the underlying game.

3. Introduction / Background

Complex AAA games (RPGs, tactical shooters, open-world titles) often overwhelm players with simultaneous information — health, enemy positions, objectives, resource states, and narrative context.

Recent advances in computer vision (real-time object detection, OCR, segmentation) and multimodal large language models (models that reason jointly over images and text) make it feasible to build a system that "watches" a screen the way a human observer would and gives contextual advice — without hooking into game memory, which risks anti-cheat bans and is not generalizable across titles.

Gap: No existing system combines real-time, non-invasive visual perception of gameplay with multimodal reasoning to deliver personalized, adaptive guidance across different games.

4. Problem Definition

Players in complex, fast-paced AAA games often lack real-time situational awareness of threats, objectives, and optimal strategies — a gap that can be closed by a computer-vision-driven AI system that reads on-screen game state non-invasively and delivers personalized tactical and narrative guidance without modifying game memory.

5. Objectives

To design a non-invasive computer vision pipeline that captures and interprets on-screen game state (HUD, enemies, objectives, environment) in real time.

To integrate a multimodal AI reasoning engine that fuses visual context with game knowledge to generate tactical, strategic, and narrative suggestions.

To build a lightweight overlay interface that delivers guidance to the player without modifying game memory, files, or violating anti-cheat policies.

To evaluate the system's latency, accuracy, and usefulness across multiple game genres and titles.

6. Scope of the Project

The system operates purely on screen-captured video/frames — no reading or writing of game memory, no code injection, no use of unofficial game APIs.

Initial scope covers PC gameplay for representative title:- GTA 5 by Rockstar Games.

7. Proposed System

Modules:

Advantages over existing systems:

Game-agnostic — works from vision alone, no per-game integration needed.

Non-invasive — no memory access, safe from anti-cheat flags.

(A block diagram illustrating this pipeline should be included here once finalized.)

8. System Requirements

a. Hardware Requirements

CPU: Quad-core or higher

GPU: Dedicated modern GPU (recommended, for real-time inference)

RAM: 16 GB minimum

Display capture-capable system (standard PC gaming setup)

b. Software Requirements

Languages: Python

AI: Multimodal LLM (e.g., a vision-language model, either API-based or locally hosted)

Screen Capture: Windows Graphics Capture API / OBS Virtual Camera

Overlay: Electron or DirectX-based overlay rendering

Backend: FastAPI/Flask

Tools: VS Code, Git

9. Methodology / Implementation Plan

Methodology: Agile (iterative sprints)

Phases:

Literature review & feasibility study

Gameplay dataset collection (screen recordings/screenshots from target titles)

Vision model selection/fine-tuning for HUD & object detection

Multimodal reasoning engine integration

Overlay UI development

Integration testing across selected game titles

Performance evaluation (latency, accuracy) & user feedback

10. Expected Outcome

A functional prototype of AEGIS that captures gameplay in real time, interprets on-screen state, and delivers contextually relevant tactical/strategic guidance through an overlay — targeting sub-second latency and validated across at least two different game titles.

11. Applications / Use Cases

Real-time assistance for casual and new players learning complex games

Accessibility aid for players who need extra situational support

Esports/competitive training tool for strategy review

Companion tool for streamers/content creators

Onboarding assistant for newly released or unfamiliar titles

12. Future Enhancements / Future Scope

Voice-based narration of guidance instead of/alongside visual overlay

Adaptive difficulty coaching based on player skill progression

Multiplayer/team coordination support

Console platform support

Expansion to additional genres (strategy, simulation, etc.)

13. References

Redmon, J., et al. "You Only Look Once: Unified, Real-Time Object Detection." CVPR, 2016.

Radford, A., et al. "Learning Transferable Visual Models From Natural Language Supervision (CLIP)." ICML, 2021.

Relevant papers/documentation on vision-language models (VLMs) and multimodal reasoning.

OpenCV and Tesseract OCR official documentation.

2. IdeaSpark Poster — Content

Header:

MIT SCHOOL OF COMPUTING

Class: TY (AI/ML — confirm exact class code)

Group ID: TYAIEC102

DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING (or AI & ML dept, if applicable)

Title: AEGIS
Subtitle: AI Gameplay Intelligence System — Real-time multimodal AI for non-invasive gameplay assistance

Team: Tanishk Kailas Patil, Hrishikesh Rajaram Mhaske, Prajwal Umesh Birari, Vivek Bhagwan Phad
Faculty Guide: Dr. Tushar Mote

Problem Statement:
Players in complex, fast-paced AAA games often lack real-time situational awareness of threats, objectives, and optimal strategies — a gap that can be closed by a computer-vision-driven AI system that reads on-screen game state non-invasively and delivers personalized tactical and narrative guidance without modifying game memory.

Scope and Feasibility:

4 Modules: Vision Perception → Context Fusion → AI Reasoning → Guidance Delivery

Screen-capture based, no memory access — anti-cheat safe

Genre-agnostic design validated across 2–3 representative titles

Real-time performance target with GPU-accelerated inference

Proposed Solution:
AEGIS watches gameplay through screen capture, detects on-screen elements (HUD, enemies, objectives) using computer vision, and reasons over this context using a multimodal AI engine to generate real-time tactical, strategic, and narrative guidance — delivered via a lightweight overlay, without ever touching the game's code or memory.

Block Diagram:
Screen Capture → Frame Preprocessing → Vision Perception (Object Detection + OCR) → Context Fusion Module → Multimodal AI Reasoning Engine → Guidance Generation → Overlay Display

Empathy Map — Target User: "The Overwhelmed Player"

Persona snapshot: A player 10–30 hours into a complex RPG/tactical shooter, juggling combat, objectives, inventory, and story — without external guides open.

💬 SAYS

"Wait, where am I even supposed to go next?"

"I didn't even see that enemy flanking me."

"I keep pausing to check a wiki mid-fight."

"This game throws too much at me at once."

🤔 THINKS

"Am I making the right strategic call here?"

"I probably missed something important on screen."

"I don't want to alt-tab and break my immersion."

"There has to be a smarter way to keep track of all this."

🖐️ DOES

Pauses gameplay frequently to check external guides/wikis

Repeats sections after dying due to missed cues

Switches between game window and browser tabs

Relies on trial-and-error rather than informed strategy

❤️ FEELS

Frustrated — overwhelmed by simultaneous threats and information

Anxious — fear of missing objectives or making costly mistakes

Disconnected — immersion breaks every time they alt-tab for help

Under-supported — existing tools feel generic, not situational

😖 PAIN POINTS

Real-time threats and cues get missed while managing UI/inventory/menus

Static guides (wikis, YouTube) don't reflect the player's current in-game situation

Companion tools require manual setup, per-game APIs, or risk anti-cheat bans

Breaking immersion to seek help outside the game hurts the experience

🌟 GAINS (what AEGIS delivers)

Real-time, on-screen contextual guidance — no alt-tabbing needed

Personalized tactical/strategic suggestions based on what's actually happening

Safe, non-invasive assistance that won't get accounts flagged or banned

Works across genres/titles without per-game setup — one system, many games

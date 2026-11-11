"""Immutable, validated configuration loaded from the Sprint 1 YAML files."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class GameConfig:
    name: str; window_class: str; window_title: str; display_mode: str

@dataclass(frozen=True)
class CaptureConfig:
    target_fps: int; output_color: str; output_idx: int

@dataclass(frozen=True)
class ROIConfig:
    health_bar: dict[str, float]; armor_bar: dict[str, float]; minimap: dict[str, float]
    hud_scan_region: dict[str, float]

@dataclass(frozen=True)
class PerceptionConfig:
    health: dict[str, float]

@dataclass(frozen=True)
class OverlayConfig:
    title: str; vsync: bool; telemetry_hud: bool; vitals_hud: bool

@dataclass(frozen=True)
class IPCConfig:
    ring_buffer_slots: int; frame_width: int; frame_height: int; frame_channels: int; metadata_size: int

@dataclass(frozen=True)
class SystemConfig:
    target_fps: int; log_level: str; debug_mode: bool; debug_dump_dir: str

@dataclass(frozen=True)
class AegisConfig:
    game: GameConfig; capture: CaptureConfig; roi: ROIConfig; perception: PerceptionConfig
    alerts: dict[str, float]; overlay: OverlayConfig; ipc: IPCConfig; system: SystemConfig
    performance: dict[str, float]


def _mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Missing required mapping: {key}")
    return value


def _roi(data: dict[str, Any], name: str) -> dict[str, float]:
    roi = _mapping(data, name)
    required = ("x1", "y1", "x2", "y2")
    if any(key not in roi for key in required):
        raise ValueError(f"Missing required ROI field in {name}")
    values = {key: float(roi[key]) for key in required}
    if any(value < 0 or value > 1 for value in values.values()) or values["x1"] >= values["x2"] or values["y1"] >= values["y2"]:
        raise ValueError(f"ROI {name} must be ordered and within [0.0, 1.0]")
    return values


def _load(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"Configuration file {path} must contain a mapping")
    return data


def load_config(game_yaml: str | Path, system_yaml: str | Path) -> AegisConfig:
    game_data, system_data = _load(game_yaml), _load(system_yaml)
    game = _mapping(game_data, "game"); capture = _mapping(game_data, "capture")
    roi = _mapping(game_data, "roi"); perception = _mapping(game_data, "perception")
    overlay = _mapping(system_data, "overlay"); ipc = _mapping(system_data, "ipc"); system = _mapping(system_data, "system")
    for section, keys in ((game, ("name", "window_class", "window_title", "display_mode")), (capture, ("target_fps", "output_color", "output_idx")), (system, ("target_fps", "log_level", "debug_mode", "debug_dump_dir"))):
        if any(key not in section for key in keys):
            raise ValueError("Missing required configuration field")
    slots, width, height, channels, metadata = (int(ipc[key]) for key in ("ring_buffer_slots", "frame_width", "frame_height", "frame_channels", "metadata_size"))
    if slots < 2 or min(width, height, channels, metadata) <= 0:
        raise ValueError("IPC dimensions and slot count must be positive (at least two slots)")
    return AegisConfig(
        GameConfig(**game), CaptureConfig(**capture),
        ROIConfig(_roi(roi, "health_bar"), _roi(roi, "armor_bar"), _roi(roi, "minimap"), _mapping(roi, "hud_scan_region")),
        PerceptionConfig(_mapping(perception, "health")), _mapping(game_data, "alerts"), OverlayConfig(**overlay),
        IPCConfig(slots, width, height, channels, metadata), SystemConfig(**system), _mapping(system_data, "performance"),
    )

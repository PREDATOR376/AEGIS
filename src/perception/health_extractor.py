"""Health-bar extraction using a lightweight BGR channel differential."""
from __future__ import annotations

import math

import numpy as np

from src.config import ROIConfig


def _crop(frame: np.ndarray, roi: dict[str, float]) -> np.ndarray:
    """Return a normalized ROI, rejecting invalid capture frames immediately."""
    if not isinstance(frame, np.ndarray) or frame.ndim != 3 or frame.shape[2] not in (3, 4):
        raise ValueError("Health extraction requires a BGR or BGRA frame")
    height, width = frame.shape[:2]
    if height == 0 or width == 0:
        raise ValueError("Health extraction received an empty frame")
    x1, y1 = math.floor(roi["x1"] * width), math.floor(roi["y1"] * height)
    x2, y2 = math.ceil(roi["x2"] * width), math.ceil(roi["y2"] * height)
    if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
        raise ValueError("Health ROI is outside the captured frame")
    result = frame[y1:y2, x1:x2]
    if result.size == 0:
        raise ValueError("Health ROI crop is empty")
    return result


def extract_health(frame: np.ndarray, roi: ROIConfig, *, green_delta: int = 30,
                   red_delta: int = 30, min_intensity: int = 50,
                   column_threshold: float = 0.30) -> float:
    """Estimate health as a 0.0--1.0 fill fraction.

    GTA's normal bar is green (G exceeds R/B); at critical health it may flash
    red, so that equally simple channel differential is accepted too.  Counting
    active pixels per column makes the result insensitive to the bar's height.
    """
    bar = _crop(frame, roi.health_bar)
    blue = bar[..., 0].astype(np.int16)
    green = bar[..., 1].astype(np.int16)
    red = bar[..., 2].astype(np.int16)
    green_fill = (green >= min_intensity) & (green - np.maximum(red, blue) >= green_delta)
    red_fill = (red >= min_intensity) & (red - np.maximum(green, blue) >= red_delta)
    filled_columns = (green_fill | red_fill).mean(axis=0) >= column_threshold
    return float(np.clip(filled_columns.mean(), 0.0, 1.0))

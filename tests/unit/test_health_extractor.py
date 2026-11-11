import numpy as np
import pytest

from src.config import ROIConfig
from src.perception import extract_health


ROI = ROIConfig({"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}, {"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}, {"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}, {})


@pytest.mark.parametrize("fill", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_extracts_known_green_fill(fill):
    frame = np.full((12, 100, 4), (20, 20, 20, 255), dtype=np.uint8)
    frame[:, :round(fill * 100), :] = (30, 220, 30, 255)
    assert extract_health(frame, ROI) == pytest.approx(fill, abs=0.01)


def test_extracts_critical_red_fill():
    frame = np.full((12, 100, 4), (20, 20, 20, 255), dtype=np.uint8)
    frame[:, :20, :] = (30, 30, 220, 255)
    assert extract_health(frame, ROI) == pytest.approx(0.20, abs=0.01)


def test_rejects_invalid_frame():
    with pytest.raises(ValueError, match="BGR"):
        extract_health(np.zeros((10, 10), dtype=np.uint8), ROI)

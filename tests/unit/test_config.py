from dataclasses import FrozenInstanceError
from pathlib import Path
import pytest
from src.config import load_config

ROOT = Path(__file__).parents[2]

def test_loads_validated_immutable_config():
    config = load_config(ROOT / "configs/gta_v.yaml", ROOT / "configs/system.yaml")
    assert config.capture.output_color == "BGRA"
    assert config.roi.health_bar["x1"] == 0.045
    with pytest.raises(FrozenInstanceError): config.capture.target_fps = 60

def test_rejects_out_of_range_roi(tmp_path):
    game = (ROOT / "configs/gta_v.yaml").read_text().replace("x1: 0.045", "x1: -0.1", 1)
    path = tmp_path / "game.yaml"; path.write_text(game)
    with pytest.raises(ValueError, match="ROI"):
        load_config(path, ROOT / "configs/system.yaml")

import pytest

@pytest.mark.live
def test_gta_v_capture_smoke():
    dxcam = pytest.importorskip("dxcam")
    camera = dxcam.create(output_idx=0, output_color="BGRA")
    try:
        frame = camera.grab()
        assert frame is not None and frame.ndim == 3 and frame.shape[2] == 4
    finally:
        camera.release()

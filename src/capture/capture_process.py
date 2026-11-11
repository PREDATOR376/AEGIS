"""Dedicated DXGI capture process; it owns the dxcam camera lifecycle."""
from __future__ import annotations
import logging
import time
from multiprocessing.synchronize import Event

from src.config import AegisConfig
from src.ipc import RingBuffer

log = logging.getLogger(__name__)

def run_capture(config: AegisConfig, ring_buffer_name: str, shutdown_event: Event) -> None:
    try:
        import dxcam
        camera = dxcam.create(output_idx=config.capture.output_idx, output_color=config.capture.output_color)
    except Exception as exc:
        raise RuntimeError("dxcam capture could not start. Run AEGIS as Administrator for DXGI Desktop Duplication.") from exc
    ring = RingBuffer(ring_buffer_name, config.ipc.ring_buffer_slots, config.ipc.frame_height, config.ipc.frame_width, config.ipc.frame_channels, create=False)
    frame_id, target = 0, 1 / config.capture.target_fps
    try:
        while not shutdown_event.is_set():
            started = time.perf_counter()
            try:
                frame = camera.grab()
                if frame is not None:
                    ring.write_frame(frame, frame_id)
                    frame_id += 1
            except Exception:
                log.exception("DXGI device lost; rebuilding capture camera")
                try: camera.release()
                except Exception: pass
                time.sleep(0.5)
                try:
                    import dxcam
                    camera = dxcam.create(output_idx=config.capture.output_idx, output_color=config.capture.output_color)
                except Exception:
                    log.exception("DXGI camera recovery failed")
            time.sleep(max(0.0, target - (time.perf_counter() - started)))
    except KeyboardInterrupt:
        pass
    finally:
        try: camera.release()
        finally: ring.close()

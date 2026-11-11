"""Frame perception and state publication bridge."""
from __future__ import annotations
import logging
import time
from multiprocessing.synchronize import Event

from src.config import AegisConfig
from src.ipc import RingBuffer, StateRingBuffer
from src.perception import extract_health

log = logging.getLogger(__name__)

def run_fusion(config: AegisConfig, capture_rb_name: str, state_rb_name: str, shutdown_event: Event) -> None:
    ring = RingBuffer(capture_rb_name, config.ipc.ring_buffer_slots, config.ipc.frame_height, config.ipc.frame_width, config.ipc.frame_channels, create=False)
    state_ring = StateRingBuffer(state_rb_name, config.ipc.ring_buffer_slots, config.ipc.metadata_size, create=False)
    try:
        while not shutdown_event.is_set():
            item = ring.read_frame()
            if item is None:
                time.sleep(0.001)
                continue
            frame, frame_id, timestamp_ns = item
            try:
                health_pct = extract_health(
                    frame, config.roi,
                    green_delta=int(config.perception.health["green_delta"]),
                    red_delta=int(config.perception.health["red_delta"]),
                    min_intensity=int(config.perception.health["min_intensity"]),
                    column_threshold=float(config.perception.health["col_threshold"]),
                )
            except ValueError:
                log.exception("Skipping frame %s: invalid health ROI", frame_id)
                continue
            state_ring.write_state({"frame_id": frame_id, "timestamp": timestamp_ns / 1_000_000_000, "health_pct": health_pct})
    finally:
        ring.close()
        state_ring.close()

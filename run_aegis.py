"""Single Sprint 1 launcher for the capture, fusion, and overlay processes."""
from __future__ import annotations
import logging
import multiprocessing as mp
from pathlib import Path
import signal

from src.capture import run_capture
from src.config import load_config
from src.fusion import run_fusion
from src.ipc import RingBuffer, StateRingBuffer
from src.overlay import run_overlay
from src.utils.admin import require_admin
from src.utils.dpi import init_dpi_awareness

ROOT = Path(__file__).resolve().parent

def main() -> None:
    init_dpi_awareness()
    require_admin("dxcam DXGI Desktop Duplication screen capture")
    config = load_config(ROOT / "configs/gta_v.yaml", ROOT / "configs/system.yaml")
    logging.basicConfig(level=getattr(logging, config.system.log_level), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    shutdown = mp.Event()
    name = f"aegis_capture_{mp.current_process().pid}"
    state_name = f"aegis_state_{mp.current_process().pid}"
    ring = RingBuffer(name, config.ipc.ring_buffer_slots, config.ipc.frame_height, config.ipc.frame_width, config.ipc.frame_channels, create=True)
    state_ring = StateRingBuffer(state_name, config.ipc.ring_buffer_slots, config.ipc.metadata_size, create=True)
    processes = [mp.Process(target=run_capture, args=(config, name, shutdown), name="aegis-capture"), mp.Process(target=run_fusion, args=(config, name, state_name, shutdown), name="aegis-fusion"), mp.Process(target=run_overlay, args=(config, state_name, shutdown), name="aegis-overlay")]
    def stop(*_): shutdown.set()
    signal.signal(signal.SIGINT, stop)
    try:
        for process in processes: process.start()
        while not shutdown.is_set():
            for process in processes:
                if process.exitcode not in (None, 0): logging.error("%s exited with %s", process.name, process.exitcode)
            shutdown.wait(0.25)
    finally:
        shutdown.set()
        for process in processes: process.join(2)
        for process in processes:
            if process.is_alive(): process.terminate(); process.join()
        ring.close()
        state_ring.close()

if __name__ == "__main__":
    mp.freeze_support()
    main()

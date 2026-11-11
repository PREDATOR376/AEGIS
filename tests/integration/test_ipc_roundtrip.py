import uuid
import numpy as np
from src.ipc import RingBuffer

def test_multiple_frames_round_trip_intact():
    ring = RingBuffer(f"aegis_integration_{uuid.uuid4().hex}", 2, 2, 3, 4, create=True)
    try:
        first = np.zeros((2, 3, 4), dtype=np.uint8); second = np.ones((2, 3, 4), dtype=np.uint8)
        ring.write_frame(first, 0); assert ring.read_frame()[1] == 0
        ring.write_frame(second, 1); frame, frame_id, _ = ring.read_frame()
        assert frame_id == 1 and np.array_equal(frame, second)
    finally: ring.close()

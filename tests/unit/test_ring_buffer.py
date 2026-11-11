import uuid
import numpy as np
from src.ipc import RingBuffer

def make_ring():
    return RingBuffer(f"aegis_test_{uuid.uuid4().hex}", 2, 3, 4, 4, create=True)

def test_round_trip_and_nonblocking_empty_read():
    ring = make_ring()
    try:
        assert ring.read_frame() is None
        frame = np.full((3, 4, 4), 7, dtype=np.uint8)
        ring.write_frame(frame, 12)
        received, frame_id, timestamp = ring.read_frame()
        assert frame_id == 12 and timestamp > 0 and np.array_equal(received, frame)
    finally:
        ring.close()

def test_rejects_invalid_shape():
    ring = make_ring()
    try:
        import pytest
        with pytest.raises(ValueError): ring.write_frame(np.zeros((1, 1, 4), dtype=np.uint8), 1)
    finally: ring.close()

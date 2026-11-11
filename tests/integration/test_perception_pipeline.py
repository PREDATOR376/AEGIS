import uuid

from src.ipc import StateRingBuffer


def test_state_ring_delivers_latest_complete_health_state():
    name = f"aegis_state_{uuid.uuid4().hex}"
    ring = StateRingBuffer(name, slots=2, payload_size=256, create=True)
    reader = StateRingBuffer(name, slots=2, payload_size=256, create=False)
    try:
        ring.write_state({"frame_id": 1, "timestamp": 1.0, "health_pct": 0.80})
        ring.write_state({"frame_id": 2, "timestamp": 2.0, "health_pct": 0.55})
        assert reader.read_latest() == {"frame_id": 2, "timestamp": 2.0, "health_pct": 0.55}
    finally:
        reader.close()
        ring.close()

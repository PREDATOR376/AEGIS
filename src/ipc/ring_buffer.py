"""Fixed-size SharedMemory ring buffer for BGRA capture frames."""
from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Value
from multiprocessing.shared_memory import SharedMemory
import struct
import time
from typing import Optional
import json

import numpy as np

HEADER_SIZE = 256
_HEADER = struct.Struct("<IIqIII")  # ready, frame id, timestamp ns, height, width, channels

@dataclass(frozen=True)
class FrameHeader:
    frame_id: int
    timestamp_ns: int
    height: int
    width: int
    channels: int

class RingBuffer:
    def __init__(self, name: str, slots: int, frame_h: int, frame_w: int, channels: int, create: bool) -> None:
        if slots < 2 or min(frame_h, frame_w, channels) <= 0:
            raise ValueError("RingBuffer requires at least two positive-sized slots")
        self.name, self.slots, self.frame_h, self.frame_w, self.channels = name, slots, frame_h, frame_w, channels
        self.slot_size = HEADER_SIZE + frame_h * frame_w * channels
        self._creator = create
        self.shm = SharedMemory(name=name, create=create, size=self.slot_size * slots if create else 0)
        self.write_idx = Value("i", 0)
        self.read_idx = Value("i", 0)
        if create:
            self.shm.buf[:] = b"\0" * len(self.shm.buf)

    def write_frame(self, frame: np.ndarray, frame_id: int) -> None:
        if frame.dtype != np.uint8 or frame.shape != (self.frame_h, self.frame_w, self.channels):
            raise ValueError(f"Expected uint8 frame {(self.frame_h, self.frame_w, self.channels)}, got {frame.shape}/{frame.dtype}")
        with self.write_idx.get_lock():
            index = self.write_idx.value
            self.write_idx.value = (index + 1) % self.slots
        offset = index * self.slot_size
        payload = memoryview(np.ascontiguousarray(frame)).cast("B")
        self.shm.buf[offset + HEADER_SIZE:offset + self.slot_size] = payload
        _HEADER.pack_into(self.shm.buf, offset, 1, int(frame_id), time.perf_counter_ns(), self.frame_h, self.frame_w, self.channels)

    def read_frame(self) -> Optional[tuple[np.ndarray, int, int]]:
        with self.read_idx.get_lock():
            index = self.read_idx.value
            offset = index * self.slot_size
            ready, frame_id, timestamp_ns, height, width, channels = _HEADER.unpack_from(self.shm.buf, offset)
            if not ready:
                return None
            data = np.ndarray((height, width, channels), dtype=np.uint8, buffer=self.shm.buf, offset=offset + HEADER_SIZE).copy()
            _HEADER.pack_into(self.shm.buf, offset, 0, frame_id, timestamp_ns, height, width, channels)
            self.read_idx.value = (index + 1) % self.slots
        return data, frame_id, timestamp_ns

    def close(self) -> None:
        self.shm.close()
        if self._creator:
            try:
                self.shm.unlink()
            except FileNotFoundError:
                pass


_STATE_HEADER = struct.Struct("<IIqI")  # ready, frame id, timestamp ns, JSON bytes


class StateRingBuffer:
    """Latest-state shared-memory ring for small JSON messages.

    Unlike the frame ring this is deliberately latest-wins: the overlay scans
    every completed slot and selects the newest frame, so it never displays a
    backlog when rendering is slower than capture.
    """
    def __init__(self, name: str, slots: int, payload_size: int, create: bool) -> None:
        if slots < 2 or payload_size <= _STATE_HEADER.size:
            raise ValueError("StateRingBuffer requires two slots and usable payload space")
        self.name, self.slots, self.payload_size, self._creator = name, slots, payload_size, create
        self.slot_size = _STATE_HEADER.size + payload_size
        self.shm = SharedMemory(name=name, create=create, size=self.slot_size * slots if create else 0)
        if create:
            self.shm.buf[:] = b"\0" * len(self.shm.buf)

    def write_state(self, state: dict) -> None:
        encoded = json.dumps(state, separators=(",", ":"), allow_nan=False).encode("utf-8")
        if len(encoded) > self.payload_size:
            raise ValueError("State JSON exceeds configured IPC metadata size")
        frame_id = int(state["frame_id"])
        index = frame_id % self.slots
        offset = index * self.slot_size
        # Mark unavailable before replacing a slot, then publish the header last.
        _STATE_HEADER.pack_into(self.shm.buf, offset, 0, frame_id, 0, 0)
        self.shm.buf[offset + _STATE_HEADER.size:offset + _STATE_HEADER.size + len(encoded)] = encoded
        timestamp_ns = int(float(state["timestamp"]) * 1_000_000_000)
        _STATE_HEADER.pack_into(self.shm.buf, offset, 1, frame_id, timestamp_ns, len(encoded))

    def read_latest(self, after_frame_id: int = -1) -> Optional[dict]:
        newest: tuple[int, bytes] | None = None
        for index in range(self.slots):
            offset = index * self.slot_size
            ready, frame_id, _timestamp_ns, length = _STATE_HEADER.unpack_from(self.shm.buf, offset)
            if not ready or frame_id <= after_frame_id or length > self.payload_size:
                continue
            payload = bytes(self.shm.buf[offset + _STATE_HEADER.size:offset + _STATE_HEADER.size + length])
            # A writer may have just reused this slot; require the header to be stable.
            if _STATE_HEADER.unpack_from(self.shm.buf, offset)[:2] != (ready, frame_id):
                continue
            if newest is None or frame_id > newest[0]:
                newest = (frame_id, payload)
        if newest is None:
            return None
        return json.loads(newest[1].decode("utf-8"))

    def close(self) -> None:
        self.shm.close()
        if self._creator:
            try:
                self.shm.unlink()
            except FileNotFoundError:
                pass

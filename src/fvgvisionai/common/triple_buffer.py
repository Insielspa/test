import threading
from enum import Enum
from typing import Optional, List

import numpy as np


class FrameType(Enum):
    FRAME_NEW = 0
    FRAME_READY = 1


class TripleBuffer:
    def __init__(self):
        self._buffers: List[Optional[np.ndarray]] = [None, None, None]
        self._id = [0, 0, 0]
        self._indices = [0, 1, 2]
        self._lock = threading.Lock()

    def get_ready_frame(self) -> (int, bytes):
        with self._lock:
            return self._get_id(FrameType.FRAME_READY), self._get_frame(FrameType.FRAME_READY)

    def set_new_frame(self, frame_id: int, frame: np.ndarray):
        with self._lock:
            self._id[self._indices[FrameType.FRAME_NEW.value]] = frame_id
            self._buffers[self._indices[FrameType.FRAME_NEW.value]] = frame

    def swap_buffers(self):
        with self._lock:
            self._indices[0], self._indices[1], self._indices[2] = self._indices[2], self._indices[0], \
                self._indices[1]

    def _get_id(self, index: FrameType) -> Optional[int]:
        return self._id[self._indices[index.value]]

    def _get_frame(self, index: FrameType) -> Optional[np.ndarray]:
        return self._buffers[self._indices[index.value]]

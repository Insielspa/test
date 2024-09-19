import logging
import threading
from abc import ABC, abstractmethod
from typing import Optional

from fvgvisionai.common.video_observable import VideoObservable
from fvgvisionai.config.app_settings import AppSettings


class AbstractVideoSource(ABC):
    def __init__(self, input_file: str, video_observable: VideoObservable, app_settings: AppSettings):
        self._input_file = input_file
        self._frame_index = 0
        self._running = False
        self._app_settings = app_settings
        self._video_observable = video_observable

        self._source_forced_fps_enabled = app_settings.video_source_forced_fps_enabled
        self._source_forced_fps = app_settings.video_source_forced_fps

        self._exit_signal: Optional[threading.Event] = None

        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def read_source(self, exit_event):
        pass

    def continue_to_read(self, frame_index: int) -> bool:
        if self._exit_signal is not None and self._exit_signal.is_set():
            return False
        else:
            if self._app_settings.benchmark_enabled:
                return frame_index < self._app_settings.benchmark_duration_time_ms
            else:
                return True

    def stop(self):
        self._running = False


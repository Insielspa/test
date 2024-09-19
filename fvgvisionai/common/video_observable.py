from abc import ABC, abstractmethod
from typing import List, Optional

from numpy import ndarray


class VideoObserver(ABC):

    @abstractmethod
    def setup_video_parameters(self, video_width: int, video_height: int, video_fps: int):
        pass

    @abstractmethod
    def receive_video_frame(self, frame_index: int, video_frame: Optional[ndarray], elapsed_time: int):
        pass


class VideoObservable:
    def __init__(self):
        self._video_observers: List[VideoObserver] = list()

    def add_video_observer(self, observer: VideoObserver):
        if observer not in self._video_observers:
            self._video_observers.append(observer)

    def notify_video_parameters(self, video_width: int, video_height: int, video_fps: int):
        for observer in self._video_observers:
            observer.setup_video_parameters(video_width, video_height, video_fps)

    def notify_video_frame(self, frame_index: int, video_frame: ndarray, elapsed_time: int):
        for observer in self._video_observers:
            observer.receive_video_frame(frame_index, video_frame, elapsed_time)

    def remove_video_observer(self, observer: VideoObserver):
        self._video_observers.remove(observer)

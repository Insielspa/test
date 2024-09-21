import threading
import traceback

import cv2
from numpy import ndarray

from common.app_timer import AppTimer
from common.utils import compute_elapsed_time_ms, wait_frame_duration
from common.video_observable import VideoObservable
from config.app_settings import AppSettings
from input.abstract_video_source import AbstractVideoSource
from input.frame_resizer import FrameResizer
from input.input_costants import DEFAULT_SOURCE_FPS


class StaticImageSourceReader(AbstractVideoSource):
    def __init__(self, input_file: str, video_observable: VideoObservable, app_settings: AppSettings):
        super(StaticImageSourceReader, self).__init__(input_file, video_observable, app_settings)
        self._frame_resizer = FrameResizer(app_settings)

    def read_source(self, exit_signal: threading.Event):
        self._running = True

        try:
            read_frame_timer = AppTimer()

            self._frame_index = 0
            self._exit_signal = exit_signal

            image_frame: ndarray = cv2.imread(self._input_file)

            if image_frame is not None:
                self._logger.info(f"video_source source {self._input_file} is opened")

                image_source_width, image_source_height, image_source_fps = self.extract_image_info(image_frame)

                declared_elapsed_time = compute_elapsed_time_ms(image_source_fps)
                image_width, image_height = self._frame_resizer.init_image_size(image_source_width, image_source_height)

                self._video_observable.notify_video_parameters(image_width, image_height, declared_elapsed_time)

                read_frame_timer.start()
                while self.continue_to_read(self._frame_index):
                    self._frame_index = (self._frame_index + 1) % 1_000_000_000

                    frame = self._frame_resizer.resize_frame(image_frame)
                    time_to_acquire_frame = round(read_frame_timer.stop())

                    self._logger.debug(
                        f"read # {self._frame_index} frame time {time_to_acquire_frame:5.2f} declared {declared_elapsed_time:5.2f} ms")
                    self._video_observable.notify_video_frame(self._frame_index, frame,
                                                              max(declared_elapsed_time, time_to_acquire_frame))

                    wait_frame_duration(declared_elapsed_time, time_to_acquire_frame)

                    read_frame_timer.start()
                self._logger.warning("frame_read thread is shutting down")
            else:
                self._logger.error(f"Source video_source {self._input_file} is not available!")
                self._exit_signal.set()
        except Exception as e:
            self._logger.error(f"Si è verificata un'eccezione: {e}")
            traceback.print_exc()
        finally:
            self._running = False

    def extract_image_info(self, image: ndarray) -> (int, int, int):
        # Ottieni le dimensioni dell'immagine
        image_source_height, image_source_width, canali = image.shape
        return image_source_width, image_source_height, DEFAULT_SOURCE_FPS
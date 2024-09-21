import logging
import subprocess
import threading
import time
import traceback
from typing import Optional

import cv2

from common.app_timer import AppTimer
from common.loading_image_utils import create_error_no_connection
from common.utils import compute_elapsed_time_ms, wait_frame_duration
from common.video_observable import VideoObservable
from config.app_settings import AppSettings
from input.abstract_video_source import AbstractVideoSource
from input.frame_resizer import FrameResizer
from input.input_costants import DEFAULT_SOURCE_FPS, NO_CONNECTION_FRAME_INDEX, TIME_TO_WATI_BEFORE_RECONNECT


class Cv2StreamReader(AbstractVideoSource):
    def __init__(self, input_file: str, video_observable: VideoObservable, app_settings: AppSettings):
        super(Cv2StreamReader, self).__init__(input_file, video_observable, app_settings)
        self._frame_resizer = FrameResizer(app_settings)
        self._ffmpeg_process: Optional[subprocess] = None
        self._logger = logging.getLogger(__name__)

    def read_source(self, exit_signal: threading.Event):
        self._running = True

        cap: Optional[cv2.VideoCapture] = None
        try:
            read_frame_timer = AppTimer()

            self._frame_index = 0
            self._exit_signal = exit_signal

            cap = cv2.VideoCapture(self._input_file)
            #cap = cv2.VideoCapture(f'ffmpeg-nvdec:{self._input_file}')

            video_recovery_mode = True

            if cap.isOpened():
                self._logger.info(f"video_source source {self._input_file} is opened")
                image_source_width, image_source_height, image_source_fps, codec = self.extract_video_info(cap)
                self._logger.info(f"codec {codec} is used")

                declared_elapsed_time = compute_elapsed_time_ms(image_source_fps)
                image_width, image_height = self._frame_resizer.init_image_size(image_source_width, image_source_height)
                no_connection_image = create_error_no_connection(image_width, image_height)

                self._video_observable.notify_video_parameters(image_width, image_height, declared_elapsed_time)

                read_frame_timer.start()
                while self.continue_to_read(self._frame_index):
                    ret, frame = cap.read()

                    if not ret:
                        if not video_recovery_mode:
                            video_recovery_mode = True
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        else:
                            attempt = 1
                            opened = False

                            while attempt < 60 and not opened:
                                self._logger.warning(
                                    f"source video_source is not available. Try to reconnect after in {TIME_TO_WATI_BEFORE_RECONNECT} seconds. Attempt # {attempt}")
                                if cap is not None:
                                    cap.release()
                                time.sleep(TIME_TO_WATI_BEFORE_RECONNECT)

                                self._video_observable.notify_video_frame(NO_CONNECTION_FRAME_INDEX,
                                                                          no_connection_image,
                                                                          max(declared_elapsed_time,
                                                                              round(read_frame_timer.elapsed_time)))

                                attempt += 1
                                cap = cv2.VideoCapture(self._input_file)
                                if cap.isOpened():
                                    self._logger.warning(
                                        "source video_source is again available.")
                                    opened = True

                            if not opened:
                                self._logger.error("source video_source is not available, closing program")
                                self._exit_signal.set()
                                break
                    else:
                        video_recovery_mode = False

                    self._frame_index = (self._frame_index + 1) % 1_000_000_000

                    frame = self._frame_resizer.resize_frame(frame)
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
            if cap is not None:
                cap.release()

    def continue_to_read(self, frame_index: int) -> bool:
        if self._exit_signal is not None and self._exit_signal.is_set():
            return False
        else:
            if self._app_settings.benchmark_enabled:
                return frame_index < self._app_settings.benchmark_duration_time_ms
            else:
                return True

    def extract_video_info(self, cap: cv2.VideoCapture) -> (int, int, float, str):
        if not self._source_forced_fps_enabled:
            fps_from_source = cap.get(cv2.CAP_PROP_FPS)
            if fps_from_source == 0:
                self._logger.warning(
                    f"video_source source is {fps_from_source} fps so to be {DEFAULT_SOURCE_FPS} fps")
                fps_from_source = DEFAULT_SOURCE_FPS
        else:
            fps_from_source = self._source_forced_fps
            self._logger.warning(
                f"video_source source is forced to be {self._source_forced_fps} fps (original was {cap.get(cv2.CAP_PROP_FPS)})")

        image_source_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        image_source_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        codec_info = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec_str = "".join([chr((codec_info >> 8 * i) & 0xFF) for i in range(4)])

        return image_source_width, image_source_height, fps_from_source, codec_str

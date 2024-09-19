import logging
import subprocess
import threading
import time
import traceback
from typing import Optional

import cv2

from fvgvisionai.common.app_timer import AppTimer
from fvgvisionai.common.loading_image_utils import create_error_no_connection
from fvgvisionai.common.utils import compute_elapsed_time_ms, wait_frame_duration
from fvgvisionai.common.video_observable import VideoObservable
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.input.abstract_video_source import AbstractVideoSource
from fvgvisionai.input.frame_resizer import FrameResizer
from fvgvisionai.input.input_costants import DEFAULT_SOURCE_FPS, NO_CONNECTION_FRAME_INDEX, TIME_TO_WATI_BEFORE_RECONNECT


class CudaStreamReader(AbstractVideoSource):
    def __init__(self, input_file: str, video_observable: VideoObservable, app_settings: AppSettings):
        super(CudaStreamReader, self).__init__(input_file, video_observable, app_settings)
        self._frame_resizer = FrameResizer(app_settings)
        self._ffmpeg_process: Optional[subprocess] = None
        self._logger = logging.getLogger(__name__)

    def read_source(self, exit_signal: threading.Event):
        self._running = True

        reader: Optional[cv2.cudacodec.VideoReader] = None
        try:
            read_frame_timer = AppTimer()

            self._frame_index = 0
            self._exit_signal = exit_signal

            # https://docs.opencv.org/4.x/dd/d7d/structcv_1_1cudacodec_1_1VideoReaderInitParams.html
            init_params = cv2.cudacodec_VideoReaderInitParams()
            if self._input_file.startswith("rtsp"):
                init_params.udpSource = True
                init_params.allowFrameDrop = True

            reader = cv2.cudacodec.createVideoReader(self._input_file, params=init_params)
            video_recovery_mode = True

            is_opened, _ = reader.nextFrame()

            if is_opened:
                self._logger.info(f"video_source source {self._input_file} is opened")
                image_source_width, image_source_height, image_source_fps, codec = self.extract_video_info(reader)
                self._logger.info(f"codec {codec} is used")

                declared_elapsed_time = compute_elapsed_time_ms(image_source_fps)
                image_width, image_height = self._frame_resizer.init_image_size(image_source_width, image_source_height)
                no_connection_image = create_error_no_connection(image_width, image_height)

                self._video_observable.notify_video_parameters(image_width, image_height, declared_elapsed_time)

                read_frame_timer.start()
                cuda_frame = cv2.cuda.GpuMat(image_height, image_width, cv2.CV_8UC3)

                while self.continue_to_read(self._frame_index):
                    ret, cuda_frame = reader.nextFrame(cuda_frame)
                    frame = cuda_frame.download()

                    if not ret:
                        if not video_recovery_mode:
                            video_recovery_mode = True

                            continue
                        else:
                            attempt = 1
                            opened = False

                            while attempt < 60 and not opened:
                                self._logger.warning(
                                    f"source video_source is not available. Try to reconnect after in {TIME_TO_WATI_BEFORE_RECONNECT} seconds. Attempt # {attempt}")

                                time.sleep(TIME_TO_WATI_BEFORE_RECONNECT)

                                self._video_observable.notify_video_frame(NO_CONNECTION_FRAME_INDEX,
                                                                          no_connection_image,
                                                                          max(declared_elapsed_time,
                                                                              round(read_frame_timer.elapsed_time)))

                                attempt += 1
                                reader = cv2.cudacodec.createVideoReader(self._input_file,
                                                                         params=cv2.cudacodec_VideoReaderInitParams())
                                is_opened, _ = reader.nextFrame(cuda_frame)
                                if is_opened:
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

    def continue_to_read(self, frame_index: int) -> bool:
        if self._exit_signal is not None and self._exit_signal.is_set():
            return False
        else:
            if self._app_settings.benchmark_enabled:
                return frame_index < self._app_settings.benchmark_duration_time_ms
            else:
                return True

    def extract_video_info(self, cap: cv2.cudacodec.VideoReader) -> (int, int, float, str):
        format = cap.format()
        if not self._source_forced_fps_enabled:
            fps_from_source = format.fps
            if fps_from_source == 0:
                self._logger.warning(
                    f"video_source source is {fps_from_source} fps so to be {DEFAULT_SOURCE_FPS} fps")
                fps_from_source = DEFAULT_SOURCE_FPS
        else:
            fps_from_source = self._source_forced_fps
            self._logger.warning(
                f"video_source source is forced to be {self._source_forced_fps} fps (original was {format.fps})")

        image_source_width, image_source_height = (format.width, format.height)

        codec_str = "[UNDEFINED]"

        return image_source_width, image_source_height, fps_from_source, codec_str

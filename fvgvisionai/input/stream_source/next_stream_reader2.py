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


class NextStreamReader(AbstractVideoSource):
    def __init__(self, input_file: str, video_observable: VideoObservable, app_settings: AppSettings):
        super(NextStreamReader, self).__init__(input_file, video_observable, app_settings)
        self._frame_resizer = FrameResizer(app_settings)
        self._ffmpeg_process: Optional[subprocess] = None
        self._logger = logging.getLogger(__name__)

    def print_video_info(self, video_capture: cv2.VideoCapture):
        codec_info = video_capture.get(cv2.CAP_PROP_FOURCC)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("Codec: {}".format(codec_info))
        print("Resolution: {}x{}".format(width, height))

    def read_source(self, exit_signal: threading.Event):
        self._running = True

        cap: Optional[cv2.VideoCapture] = None
        try:
            read_frame_timer = AppTimer()

            self._frame_index = 0
            self._exit_signal = exit_signal

            use_cuda = True

            if use_cuda:
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-hwaccel", "cuda",
                    "-c:v", "h264_cuvid",
                    '-an', '-sn',
                    "-i", self._input_file,
                    "-pix_fmt", "rgb24",  # Specifica il formato pixel RGB24
                    "-vf", "format=rgb24",  # Assicura che l'output sia nel formato RGB24
                    "-c:v", "rawvideo",
                    "-f", "rawvideo",
                    "-"
                ]

                self._logger.warning(f'{" ".join(ffmpeg_cmd)}')

                # Avvia il processo ffmpeg
                self._ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE)
                time.sleep(2)
                # Inizializza il VideoCapture utilizzando il processo ffmpeg
                # Inizializza VideoCapture utilizzando il processo ffmpeg
                cap = cv2.VideoCapture(f'pipe:{self._ffmpeg_process.stdout.fileno()}', cv2.CAP_FFMPEG)
            else:
                # Impostazione manuale del codec per la decodifica con NVidia
                CAP_PROP_FFMPEG_HWACCEL=0x17  # 0x17 corrisponde a CAP_PROP_FFMPEG_HWACCEL
                CAP_PROP_FFMPEG_HWACCEL_DEVICE=0x39  # 0x39 corrisponde a CAP_PROP_FFMPEG_HWACCEL_DEVICE

                # Configurazione del codec per la decodifica con NVidia
                codec_config = "h264_cuvid"
                cap = cv2.VideoCapture(self._input_file,  cv2.CAP_FFMPEG)
                # Configura il codec per la decodifica NVIDIA (CUVID)
                #cap.set(CAP_PROP_FFMPEG_HWACCEL, 1)
                #cap.set(CAP_PROP_FFMPEG_HWACCEL_DEVICE, codec_config)
            # cap = cv2.VideoCapture(self._input_file, apiPreference=cv2.CAP_FFMPEG)

            self.print_video_info(cap)

            video_recovery_mode = True

            if cap.isOpened():
                self._logger.info(f"video_source source {self._input_file} is opened")

                image_source_width, image_source_height, image_source_fps = self.extract_video_info(cap)

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

    def extract_video_info(self, cap: cv2.VideoCapture):
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
        return image_source_width, image_source_height, fps_from_source

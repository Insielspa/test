import cv2
import os
import subprocess
import logging
import threading
import traceback
import time
from abc import ABC
from typing import Optional

import numpy as np
from numpy import ndarray

from fvgvisionai.common.app_timer import AppTimer
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.common.video_observable import VideoObserver
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.output.hls.hls_commons import WAIT_TIME_IN_SEC


class GStreamerOutputStreamer(VideoObserver, ABC):
    def __init__(self, buffer: TripleBuffer, app_settings: AppSettings):
        # Buffer video per la ricezione dei frame
        self._local_buffer = buffer
        # Impostazioni dell'applicazione
        self._local_app_settings = app_settings
        # Cliente RTMP per l'invio dei frame
        self._hls_client = GStreamerHlsGenerator(app_settings.video_output_stream_path,
                                                 app_settings.video_output_stream_bandwidth,
                                                 app_settings.video_output_stream_hls_gop,
                                                 app_settings.video_output_stream_hls_time)
        self._hls_client.delete_files_in_dir()

        # Parametri video locali
        self._output_video_fps = app_settings.video_output_fps
        self._video_width = 0
        self._video_height = 0
        self._time_to_acquire_frame = 0

        # Parametri video output
        self._video_bandwidth = app_settings.video_output_stream_bandwidth

        # Immagine di caricamento
        # self._loading_image: np.ndarray = create_loading_image()

        # Logger per la registrazione di eventi e errori
        self._logger = logging.getLogger(__name__)

    def is_video_parameters_defined(self):
        # Verifica se i parametri video sono definiti
        return self._video_width > 0 and self._video_height > 0 and self._time_to_acquire_frame > 0

    def setup_video_parameters(self, video_width: int, video_height: int, time_to_acquire_frame: int):
        # Aggiorna i parametri video e inizializza il client RTMP
        self._video_width = video_width
        self._video_height = video_height
        self._time_to_acquire_frame = time_to_acquire_frame

        self._logger.info(f"updating video parameters {self._video_width}x{self._video_height}")

        self._hls_client.init(self._video_width, self._video_height, self._output_video_fps)

    def receive_video_frame(self, frame_index: int, video_frame: Optional[ndarray], elapsed_time: int):
        # Metodo astratto per l'aggiornamento dei frame video
        pass

    def build_frame(self, exit_signal: threading.Event):
        try:
            # Imposta la frequenza di frame desiderata in FPS
            frame_interval = 1000.0 / self._output_video_fps
            # Inizializza l'angolo di rotazione
            angle = 0
            fps_timer = AppTimer()

            while not self.is_video_parameters_defined() and not exit_signal.is_set():
                time.sleep(WAIT_TIME_IN_SEC)
                self._logger.warning(f"waiting {WAIT_TIME_IN_SEC} s for video input")

            self._logger.info("start generating hls output")

            sent_frame = False

            while not exit_signal.is_set():
                fps_timer.start()
                next_frame_id, next_frame = self._local_buffer.get_ready_frame()

                if next_frame is not None:
                    sent_frame = self._hls_client.send_frame(next_frame)
                # else:
                #    # Se non ci sono frame disponibili, invia un'immagine di caricamento rotante
                #    rotated_image = rotate_loading_image(self._loading_image, angle)
                #    # Incrementa l'angolo di rotazione
                #    angle = (angle - 30) % 360
                #    sent_frame = self._hls_client.send_frame(rotated_image)

                elapsed_time = fps_timer.stop()
                if frame_interval > elapsed_time:
                    time.sleep((frame_interval - elapsed_time) / 1000.0)

                self._logger.debug(f"build hls-frame #{next_frame_id} in {elapsed_time:.0f}"
                                   f" (sleep: {frame_interval - elapsed_time:.0f}) ms")

                if next_frame is not None and not sent_frame:
                    # try to reconnect
                    self._logger.warning("Broken connection to RTMP server. Trying to reconnect in few seconds")
                    time.sleep(2)
                    self._hls_client.connect()

            self._hls_client.close()
            self._logger.warning("HLS thread is shutting down")
        except Exception as e:
            # Gestisci le eccezioni
            logging.error(f"Si è verificata un'eccezione: {e}")
            traceback.print_exc()


class GStreamerHlsGenerator:
    def __init__(self, hls_path: str, video_bandwidth: int, hls_gop: int, hls_time: int):
        self._width, self._height, self._fps = 0, 0, 0
        self._hls_path = hls_path
        self._video_bandwidth = video_bandwidth
        self._hls_gop = hls_gop
        self._hls_time = hls_time
        self._pipeline = None
        self._logger = logging.getLogger(__name__)

    def init(self, width, height, fps):
        self._width, self._height, self._fps = width, height, fps
        self.connect()

    def connect(self):
        command = self._build_gstreamer_pipeline()
        self._logger.info(f'HLS stream opened with pipeline: {command}')
        self._pipeline = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    def _build_gstreamer_pipeline(self):
        command = [
            'gst-launch-1.0', 'fdsrc',
            '!', f'video/x-raw, format=I420,width={self._width},height={self._height},framerate={self._fps}/1',
            '!', 'nvvidconv',
            '!', 'nvv4l2h264enc', f'bitrate={str(self._video_bandwidth * 1000)}',
            '!', f'h264parse',
            '!', 'mpegtsmux',
            '!', 'hlssink', f'location={self._hls_path}/segment_%05d.ts',
            f'playlist-location={self._hls_path}/live.m3u8',
            f'target-duration={self._hls_time}', f'max-files=3',
        ]
        return command

    def is_pipe_ready(self):
        if self._pipeline is None or self._pipeline.poll() is not None:
            self._logger.warning("Il processo GStreamer non è in esecuzione.")
            return False
        if self._pipeline.stdin is None or self._pipeline.stdin.closed:
            self._logger.warning("La pipe stdin del processo GStreamer è chiusa o non disponibile.")
            return False
        return True

    def send_frame(self, frame: ndarray):
        try:
            converted_frame = self._bgr_to_i420(frame)
            sent_bytes = self._pipeline.stdin.write(converted_frame.tobytes())
            if sent_bytes <= 0:
                self._logger.warning(f"byte inviati al server hls: {sent_bytes}")
            else:
                self._logger.debug(f"frame's byte converted in hls: {sent_bytes}")
            return True
        except BrokenPipeError as e:
            if self._pipeline.poll() is not None:
                stderr_output = self._pipeline.stderr.read()
                if stderr_output:
                    self._logger.error(f"Broken Pipe Error: {stderr_output.decode()}")
                self.close()
                self.connect()
            else:
                self._logger.error(f"Si è verificata un'eccezione: {e}")
            traceback.print_exc()
            return False

    def close(self):
        if self._pipeline:
            self._pipeline.stdin.close()
            self._pipeline.wait()
            self._logger.warning("External GStreamer process is shutting down")

    def delete_files_in_dir(self):
        # Verifica che la cartella esista
        if os.path.exists(self._hls_path):
            # Lista tutti i file nella cartella
            files = os.listdir(self._hls_path)

            # Elimina ogni file
            for file in files:
                file_path = os.path.join(self._hls_path, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self._logger.debug(f"File {file_path} successfully deleted")
                except Exception as e:
                    message_error = f"Error during deletion of file {file}: {e}"
                    self._logger.error(message_error)
                    raise PermissionError(message_error)
        else:
            message_error = f"Folder {self._hls_path} does not exists."
            self._logger.error(message_error)
            raise FileNotFoundError(message_error)

    def _bgr_to_i420(self, bgr_frame: ndarray) -> ndarray:
        height, width, _ = bgr_frame.shape

        # Convert BGR to YUV
        yuv_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2YUV_I420)

        return yuv_frame

import logging
import threading
import time
import traceback

import cv2
from flask import Flask, Response, request
from flask_wtf import CSRFProtect
from waitress import serve

from fvgvisionai.common.app_timer import AppTimer
from fvgvisionai.common.loading_image_utils import create_loading_image, rotate_loading_image
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.config.app_settings import AppSettings


class WebServer:
    def __init__(self, buffer: TripleBuffer, app_settings: AppSettings):
        self.local_buffer: TripleBuffer = buffer
        self.app_settings: AppSettings = app_settings

        self.local_image_mime_type = app_settings.video_output_image_type.value['mime-type']
        self.local_image_extension = app_settings.video_output_image_type.value['extension']
        self.local_image_quality_param_name = app_settings.video_output_image_type.value['quality_param']
        self.local_image_quality_param_value = app_settings.video_output_image_quality
        self.local_video_fps = app_settings.video_output_fps

        self.cached_data_id: int = -1
        self.cached_data: bytes = bytes()
        self.local_lock = threading.Lock()

        self.loading_image = create_loading_image(800, 600)
        self._logger = logging.getLogger(__name__)

    def build_web_frame(self, exit_event: threading.Event):
        try:
            # Imposta la frequenza di frame desiderata in FPS
            frame_interval = 1000.0 / self.local_video_fps
            # Inizializza l'angolo di rotazione
            angle = 0
            fps_timer = AppTimer()

            while not exit_event.is_set():
                fps_timer.start()
                next_frame_id, next_frame = self.local_buffer.get_ready_frame()

                if self.cached_data_id != next_frame_id:
                    if next_frame is not None:
                        _, temp = cv2.imencode(self.local_image_extension,
                                               next_frame,
                                               [self.local_image_quality_param_name,
                                                self.local_image_quality_param_value])
                        frame = temp.tobytes()
                        content_type_header = f"Content-Type: {self.local_image_mime_type}\r\n\r\n"
                        with self.local_lock:
                            self.cached_data_id = next_frame_id
                            self.cached_data = b"--frame\r\n" + content_type_header.encode('utf-8') + frame + b"\r\n"
                    else:
                        # no id to set
                        rotated_image = rotate_loading_image(self.loading_image, angle)
                        # Incrementa l'angolo di rotazione
                        angle = (angle - 30) % 360
                        _, temp = cv2.imencode(self.local_image_extension,
                                               rotated_image,
                                               [self.local_image_quality_param_name,
                                                self.local_image_quality_param_value])
                        frame = temp.tobytes()

                        content_type_header = f"Content-Type: {self.local_image_mime_type}\r\n\r\n"
                        with self.local_lock:
                            self.cached_data = b"--frame\r\n" + content_type_header.encode('utf-8') + frame + b"\r\n"

                    elapsed_time = fps_timer.stop()
                    if frame_interval > elapsed_time:
                        time.sleep((frame_interval - elapsed_time) / 1000.0)
                    self._logger.debug(f"build web-frame #{self.cached_data_id} in {elapsed_time:.0f}"
                                       f" (sleep: {frame_interval - elapsed_time:.0f}) ms")
                else:
                    elapsed_time = fps_timer.stop()
                    if frame_interval > elapsed_time:
                        time.sleep((frame_interval - elapsed_time) / 1000.0)
                    self._logger.debug(
                        f"build web-frame #{self.cached_data_id} was already prepared in {elapsed_time:.0f}"
                        f" (sleep: {frame_interval - elapsed_time:.0f}) ms")

            self._logger.warning("web server thread is shutting down")
        except Exception as e:
            # Gestisci l'eccezione qui
            logging.error(f"Si è verificata un'eccezione: {e}")
            traceback.print_exc()

    @property
    def logger(self):
        return self._logger


app = Flask(__name__)
web_server: WebServer


# Video streaming page
@app.route('/video')
def video():
    def read_frames() -> bytes:
        try:
            # Imposta la frequenza di frame desiderata in FPS
            frame_interval = 1000 / web_server.local_video_fps
            fps_timer = AppTimer()

            while True:
                fps_timer.start()
                frame_uid = web_server.cached_data_id
                with web_server.local_lock:
                    yield web_server.cached_data
                elapsed_time = fps_timer.stop()
                if frame_interval > elapsed_time:
                    time.sleep((frame_interval - elapsed_time) / 1000)
                web_server.logger.debug(f"stream web-frame #{frame_uid} in {elapsed_time:.0f}"
                                        f" (sleep: {frame_interval - elapsed_time:.0f}) ms")
        except Exception as e:
            # Gestisci l'eccezione qui
            logging.error(f"Si è verificata un'eccezione: {e}")
            traceback.print_exc()

    login = request.args.get('login')

    if login is not None and login == web_server.app_settings.video_output_image_password:
        # If success return the video_source
        web_server.logger.info("new client requires video_source")
        return Response(read_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response('Invalid login', mimetype='text/plain')


# Homepage
@app.route('/')
def index():
    return 'Service is up!'


def run_web_server(buffer: TripleBuffer, app_settings: AppSettings, exit_event: threading.Event):
    global web_server, app
    web_server = WebServer(buffer, app_settings)
    web_streamer_thread = threading.Thread(target=web_server.build_web_frame,
                                           args=(exit_event,),
                                           name='WebServer')
    web_streamer_thread.daemon = True
    web_streamer_thread.start()

    csrf = CSRFProtect()
    csrf.init_app(app)

    # for parameter https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html
    serve(app, host='0.0.0.0', port=app_settings.video_output_image_port, threads=4)

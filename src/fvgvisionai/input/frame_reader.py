import threading
from typing import Optional

from fvgvisionai.benchmark.benchmark_monitor import BenchmarkMonitor
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.common.video_observable import VideoObservable
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.config.app_settings_utils import ModelLibrary, VideoSourceMode
from fvgvisionai.input.image_source.static_image_source_reader import StaticImageSourceReader
from fvgvisionai.input.stream_source.cv2_stream_reader import Cv2StreamReader
from fvgvisionai.notify.notification_client import NotificationClient
from fvgvisionai.processor.passthrough_processor import PassthroughProcessor
from fvgvisionai.processor.ultralytics_processor import UltralyticsFrameProcessor


def run_reader(video_observable: VideoObservable, buffer: TripleBuffer,
               notification_client: Optional[NotificationClient],
               benchmark_monitor: Optional[BenchmarkMonitor],
               app_settings: AppSettings, exit_event: threading.Event) -> int:
    if app_settings.model_library == ModelLibrary.ULTRALYTICS:
        video_observable.add_video_observer(
            UltralyticsFrameProcessor(buffer, notification_client, benchmark_monitor, app_settings))
    elif app_settings.model_library == ModelLibrary.PASSTHROUGH:
        video_observable.add_video_observer(
            PassthroughProcessor(buffer, notification_client, benchmark_monitor, app_settings))
    else:
        return -1

    if app_settings.video_source_mode == VideoSourceMode.STREAM:
        Cv2StreamReader(app_settings.video_source, video_observable, app_settings).read_source(exit_event)
    #elif app_settings.video_source_mode == VideoSourceMode.FFMPEG:
    #    FFMpegStreamReader(app_settings.video_source, video_observable, app_settings).read_source(exit_event)
    #elif app_settings.video_source_mode == VideoSourceMode.CUDA:
    #    CudaStreamReader(app_settings.video_source, video_observable, app_settings).read_source(exit_event)
    elif app_settings.video_source_mode == VideoSourceMode.IMAGE:
        StaticImageSourceReader(app_settings.video_source_image, video_observable, app_settings).read_source(exit_event)
    else:
        raise ValueError(f"VIDEO_SOURCE_MODE={app_settings.video_source_mode} is not a valid decoder value")
    return 0

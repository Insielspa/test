import logging
import threading
import traceback
from abc import abstractmethod, ABC
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

from numpy import ndarray

from fvgvisionai.benchmark.benchmark_monitor import BenchmarkMonitor
from fvgvisionai.common.app_timer import AppTimer
from fvgvisionai.common.atomic_boolean import AtomicBoolean
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.common.video_observable import VideoObserver
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.input.input_costants import NO_CONNECTION_FRAME_INDEX
from fvgvisionai.notify.notification_client import NotificationClient
from fvgvisionai.processor.data_aggregator import DataAggregator
from fvgvisionai.processor.decorators.time_decorator import TimeDecorator
from fvgvisionai.processor.subprocessors.in_zone_sub_processor import AlarmStatus


class AbstractFrameProcessor(VideoObserver, ABC):
    def __init__(self, buffer: TripleBuffer, notification_client: Optional[NotificationClient],
                 benchmark_monitor: Optional[BenchmarkMonitor],
                 app_settings: AppSettings):
        super().__init__()
        self._app_settings = app_settings
        self._logger = logging.getLogger(__name__)
        self._process_executor = ThreadPoolExecutor(thread_name_prefix="process")

        self._ready = AtomicBoolean()
        self._ready.set(True)

        self._buffer = buffer

        self._notification_client = notification_client
        if self.is_notification_enabled():
            self._notification_client.start()

        self._benchmark = benchmark_monitor
        if self.is_benchmark_enabled():
            self._benchmark.start()

        self._data_aggregator = DataAggregator()

        self._global_process_timer = AppTimer()
        self._global_process_timer.start()

        self.processor_timer = AppTimer()

        self._time_decorator = TimeDecorator()

        self._data_aggregation_datetime_start = datetime.now()
        self._processor_ready_event = threading.Event()

        # Indica se il frame che e' arrivato e' valido o meno (vedi mancanza di rete)
        self._video_source_available = True

    def receive_video_frame(self, frame_index: int, video_frame: Optional[ndarray], elapsed_time: int):
        if video_frame is not None and self.is_ready():
            self._process_executor.submit(self.process_frame,
                                          frame_index, video_frame,
                                          elapsed_time)

    def process_frame(self, frame_index: int, source_frame: ndarray, acquisition_frame_time: int):
        try:
            self._ready.set(False)
            self._video_source_available = frame_index != NO_CONNECTION_FRAME_INDEX

            # Se sorgente video_source non disponibile, impostiamo frame di cortesia ed usciamo
            if not self._video_source_available:
                self._buffer.set_new_frame(frame_index, source_frame)
                self._buffer.swap_buffers()
                return

            self.processor_timer.start()

            # Puoi fare qualcosa con il frame all'esterno della classe
            self._logger.debug(f"elaborazione frame #{frame_index} - start")

            if source_frame is not None and source_frame.size > 0:
                raised_hand_alarm_status, zone_alarm_status = self._evaluate_frame(frame_index, source_frame)
            else:
                self._logger.warning("frame is None")
                zone_alarm_status = AlarmStatus.NORMAL
                raised_hand_alarm_status = AlarmStatus.NORMAL

            # Benchmark e notification non saranno mai abilitate assieme, quindi uno dei due si deve prender carico
            # di pulire i dati aggregati
            if self.is_benchmark_enabled():
                benchmark_registered = self._benchmark.measure_performance(frame_index, source_frame,
                                                                           self._data_aggregator)
                # Puliamo i dati
                if benchmark_registered:
                    self._data_aggregation_datetime_start = datetime.now()
                    self._data_aggregator.clear_data()

            if self.is_notification_enabled():
                self._notification_client.handle_alarms(raised_hand_alarm_status, zone_alarm_status)

                notification_sent = self._notification_client.handle_notification(self._data_aggregation_datetime_start,
                                                                                  self._data_aggregator)
                # Puliamo i dati
                if notification_sent:
                    self._data_aggregation_datetime_start = datetime.now()
                    self._data_aggregator.clear_data()

            process_time = self.processor_timer.stop()
            self._data_aggregator.measure_time_frame_acquisition(acquisition_frame_time)
            self._data_aggregator.measure_time_frame_processing(process_time)

            self._logger.debug(f"elaborazione frame #{frame_index} in {process_time:.0f} ms  - end")

        except Exception as e:
            self._logger.error("unexpected error %s " % e)
            traceback.print_exc()
        finally:
            self._ready.set(True)

    def _evaluate_frame(self, frame_index: int, source_frame: ndarray) -> (AlarmStatus, AlarmStatus):
        current_frame, zone_alarm_status, raised_hand_alarm_status = self._execute_frame_analysis(source_frame,
                                                                                                  self._data_aggregator)
        if current_frame is not None:
            self._buffer.set_new_frame(frame_index, current_frame)
            self._buffer.swap_buffers()
        return raised_hand_alarm_status, zone_alarm_status

    def is_benchmark_enabled(self):
        return self._app_settings.benchmark_enabled

    def is_notification_enabled(self):
        return self._notification_client is not None

    def setup_video_parameters(self, video_width: int, video_height: int, source_frame_rate_declared: int):
        self._data_aggregator.time_frame_source_declared = source_frame_rate_declared

        self._time_decorator.init_image_size(video_width, video_height)

    @abstractmethod
    def _execute_frame_analysis(self, frame: ndarray, data_aggregator: DataAggregator) -> \
            (Optional[ndarray], AlarmStatus, AlarmStatus):
        pass

    def _show_time_box(self, source_frame: ndarray):
        if self._app_settings.show_time:
            self._time_decorator.draw(source_frame)

    def is_ready(self):
        return self._ready.get()

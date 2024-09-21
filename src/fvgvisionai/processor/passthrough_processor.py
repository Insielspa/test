import traceback
from abc import ABC
from typing import Optional

import numpy as np
import torch
from numpy import ndarray

from benchmark.benchmark_monitor import BenchmarkMonitor
from common.app_timer import AppTimer
from common.triple_buffer import TripleBuffer
from config.app_settings import AppSettings
from notify.notification_client import NotificationClient
from processor.abstract_frame_processor import AbstractFrameProcessor
from processor.data_aggregator import DataAggregator
from processor.decorators.fps_frame_decorator import FpsFrameDecorator
from processor.decorators.video_info_decorator import VideoInfoDecorator
from processor.subprocessors.in_zone_sub_processor import AlarmStatus
from processor.ultralytics_processor import boolean_array_to_binary_sequences


class PassthroughProcessor(AbstractFrameProcessor, ABC):
    def __init__(self, buffer: TripleBuffer,
                 notification_client: Optional[NotificationClient],
                 benchmark_monitor: Optional[BenchmarkMonitor],
                 app_settings: AppSettings):
        super().__init__(buffer=buffer,
                         notification_client=notification_client,
                         benchmark_monitor=benchmark_monitor,
                         app_settings=app_settings)

        self._image_source_width = 0
        self._image_source_height = 0

        self._fps_decorator = FpsFrameDecorator()
        self._video_info_decorator = VideoInfoDecorator(
            model_file_name="<UNDEFINED>",
            model_library=app_settings.model_library,
            model_precision=app_settings.model_precision,
            cuda_enabled=torch.cuda.is_available(),
            tensor_enabled=app_settings.model_use_tensort,
            model_skip_frames=boolean_array_to_binary_sequences(app_settings.model_skip_frames_enabled,
                                                                app_settings.model_skip_frames_mask),
            model_size=app_settings.model_size,
            tracking_enabled=False,
            zone_enabled=False,
            door_enabled=False,
            pose_enabled=False
        )

        self._zone_poly = np.array([])
        self._ratio_width = 1
        self._ratio_height = 1

        self.performance_timer = AppTimer()

    def setup_video_parameters(self, video_width: int, video_height: int, source_frame_rate_declared: int):
        super().setup_video_parameters(video_width, video_height, source_frame_rate_declared)
        self._image_source_width = video_width
        self._image_source_height = video_height

        self._fps_decorator.init_image_size(video_width, video_height)
        self._video_info_decorator.init_image_size(video_width, video_height)

    def _execute_frame_analysis(self, source_frame: ndarray,
                                data_aggregator: DataAggregator) -> (Optional[ndarray], AlarmStatus, AlarmStatus):
        try:

            # Process scenario zone
            objects_in_zone, min_time_in_zone, max_time_in_zone, avg_time_in_zone = 0, 0, 0, 0
            data_aggregator.measure_items_in_zone(objects_in_zone,
                                                  min_time_in_zone, max_time_in_zone, avg_time_in_zone)

            # Process scenario door
            people_entering, people_leaving = 0, 0
            data_aggregator.measure_people_near_door(people_entering, people_leaving)

            # Process scenario raise hands
            people_raised_hand = 0
            data_aggregator.measure_people_with_raised_hands(people_raised_hand)

            #
            # Drawing operations
            #
            if self._app_settings.show_video_info_enabled:
                self._video_info_decorator.draw(source_frame,
                                                self._image_source_width, self._image_source_height,
                                                0, 0)
            if self._app_settings.show_fps_enabled:
                self._fps_decorator.draw(source_frame,
                                         data_aggregator.time_frame_source_declared,
                                         data_aggregator.time_frame_acquisition_average,
                                         data_aggregator.time_frame_processing_average,
                                         self._app_settings.video_output_fps)

            self._show_time_box(source_frame)

            return source_frame, AlarmStatus.NORMAL, AlarmStatus.NORMAL

        except Exception as e:
            self._logger.error("Unexpected error %s " % e)
            traceback.print_exc()
            return None, None
import logging
from typing import List, Set, Dict

import cv2
from numpy import ndarray

from common.app_alarm import AlarmStatus, AppAlarm
from common.app_timer import AppTimer
from config.app_settings import AppSettings
from processor.detected_object import DetectedObject
from processor.subprocessors.abstract_sub_processor import AbstractSubProcessor


class InZoneSubProcessor(AbstractSubProcessor):

    def __init__(self, app_settings: AppSettings):
        super().__init__(app_settings.scenario_zone_enabled)
        self._app_settings = app_settings
        self._zone_poly = app_settings.scenario_zone_coords
        self._category_set = set(obj.model_class for obj in app_settings.scenario_zone_categories)

        self._process_timer = AppTimer()
        self._process_timer.start()
        self._start_time_for_entities_in_zone: Dict[int, float] = {}

        def is_danger(people_in_zone: int) -> bool:
            return people_in_zone > app_settings.scenario_zone_danger_limit

        self._alarm = AppAlarm(is_danger,
                               app_settings.scenario_zone_cold_down_time,
                               app_settings.scenario_zone_time_limit)
        self._logger = logging.getLogger(__name__)

    def detected_objects_in_zone(self, in_frame_objects: List[DetectedObject]) -> [AlarmStatus, int, int, int, int]:
        entities_in_zone = 0
        current_elapsed_time = self._process_timer.elapsed_time
        people_in_scene: Set[int] = set()

        min_time_in_zone = 1_000_000.0
        max_time_in_zone = 0.0
        total_time_in_zone = 0.0
        for obj in (obj for obj in in_frame_objects if obj.label_num in self._category_set):
            people_in_scene.add(obj.id)
            if self.is_in_zone(obj):
                obj.is_in_zone = True
                entities_in_zone += 1
                if obj.id not in self._start_time_for_entities_in_zone:
                    self._start_time_for_entities_in_zone[obj.id] = current_elapsed_time
                obj.time_in_zone = round((current_elapsed_time - self._start_time_for_entities_in_zone[obj.id]) / 1000)
            else:
                obj.is_in_zone = False
                obj.time_in_zone = 0
                if obj.id in self._start_time_for_entities_in_zone:
                    self._start_time_for_entities_in_zone.pop(obj.id)

            if obj.time_in_zone > 0:
                max_time_in_zone = max(max_time_in_zone, obj.time_in_zone)
                min_time_in_zone = min(min_time_in_zone, obj.time_in_zone)
                total_time_in_zone += obj.time_in_zone

        if entities_in_zone > 0:
            avg_time_in_zone = round(total_time_in_zone / max(entities_in_zone, 1))
        else:
            min_time_in_zone = 0
            max_time_in_zone = 0
            avg_time_in_zone = 0

        # Rimuove gli elementi dal dizionario che non sono presenti nel set
        self._start_time_for_entities_in_zone = {k: v for k, v in self._start_time_for_entities_in_zone.items() if
                                                 k in people_in_scene}
        alarm_status = self._alarm.manage(entities_in_zone)

        return alarm_status, entities_in_zone, min_time_in_zone, max_time_in_zone, avg_time_in_zone

    def is_in_zone(self, obj: DetectedObject) -> bool:
        x, y, _, h = obj.bbox_wh
        point_in_polygon = cv2.pointPolygonTest(contour=self._zone_poly,
                                                pt=(x, y + int((h / 2))),
                                                measureDist=False)
        return point_in_polygon >= 0

    def draw(self, frame: ndarray) -> ndarray:
        cv2.polylines(img=frame, pts=[self._zone_poly], isClosed=True, color=(255, 0, 0), thickness=2)

        return frame

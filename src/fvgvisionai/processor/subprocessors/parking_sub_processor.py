import logging
from typing import List, Set, Dict

import cv2
import numpy as np
from numpy import ndarray

from common.app_alarm import AlarmStatus, AppAlarm
from common.app_timer import AppTimer
from common.video_utils import draw_icon
from config.app_settings import AppSettings
from processor.detected_object import DetectedObject
from processor.subprocessors.abstract_sub_processor import AbstractSubProcessor


class ParkingSubProcessor(AbstractSubProcessor):

    def __init__(self, app_settings: AppSettings):
        super().__init__(app_settings.scenario_parking_enabled)
        self._app_settings = app_settings
        self._parking_icon = cv2.imread('assets/images/parking.png', -1)
        self._parking_icon_height, self._parking_icon_width, _ = self._parking_icon.shape
        self._parking_poly = app_settings.scenario_parking_coords
        self._parking_busy = set()
        self._category_set = set(obj.model_class for obj in app_settings.scenario_parking_categories)

        self._process_timer = AppTimer()
        self._process_timer.start()
        self._start_time_for_entities_in_parking: Dict[int, float] = {}

        def is_danger(item_in_zone: int) -> bool:
            return item_in_zone > app_settings.scenario_parking_danger_limit

        self._alarm = AppAlarm(is_danger,
                               app_settings.scenario_parking_cold_down_time,
                               app_settings.scenario_parking_time_limit)
        self._logger = logging.getLogger(__name__)

    def detected_objects_parked(self, in_frame_objects: List[DetectedObject]) -> [AlarmStatus, int, int, int, int]:
        entities_in_zone = 0
        current_elapsed_time = self._process_timer.elapsed_time
        people_in_scene: Set[int] = set()

        min_time_in_zone = 1_000_000.0
        max_time_in_zone = 0.0
        total_time_in_zone = 0.0

        self._parking_busy.clear()
        for obj in (obj for obj in in_frame_objects if obj.label_num in self._category_set):
            people_in_scene.add(obj.id)
            if self.is_in_parking(obj):
                obj.is_in_zone = True
                entities_in_zone += 1
                if obj.id not in self._start_time_for_entities_in_parking:
                    self._start_time_for_entities_in_parking[obj.id] = current_elapsed_time
                obj.time_in_zone = round(
                    (current_elapsed_time - self._start_time_for_entities_in_parking[obj.id]) / 1000)
            else:
                obj.is_in_zone = False
                obj.time_in_zone = 0
                if obj.id in self._start_time_for_entities_in_parking:
                    self._start_time_for_entities_in_parking.pop(obj.id)

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
        self._start_time_for_entities_in_zone = {k: v for k, v in self._start_time_for_entities_in_parking.items() if
                                                 k in people_in_scene}
        alarm_status = self._alarm.manage(entities_in_zone)

        return alarm_status, entities_in_zone, min_time_in_zone, max_time_in_zone, avg_time_in_zone

    def is_in_parking(self, obj: DetectedObject) -> bool:
        x, y, _, h = obj.bbox_wh

        # Inizializziamo una variabile per verificare la presenza del punto in almeno un poligono
        point_in_any_polygon = False
        index = 0

        # Iteriamo attraverso tutti i poligoni
        for polygon in self._parking_poly:
            point_in_polygon = cv2.pointPolygonTest(contour=polygon,
                                                    pt=(x, y + int((h / 2))),
                                                    measureDist=False)

            # Se il punto è dentro al poligono corrente, settiamo la variabile a True e usciamo dal loop
            if point_in_polygon >= 0:
                self._parking_busy.add(index)
                point_in_any_polygon = True
                break

            index += 1

        return point_in_any_polygon

    def draw(self, frame: ndarray) -> ndarray:
        index = 0
        for polygon in self._parking_poly:
            cv2.polylines(img=frame, pts=[polygon], isClosed=True, color=(255, 0, 0), thickness=2)

            if index not in self._parking_busy:
                punto_centrale = np.mean(polygon.squeeze(), axis=0)
                draw_icon(frame, int(punto_centrale[0] - self._parking_icon_height / 2),
                          int(punto_centrale[1] - self._parking_icon_width / 2), self._parking_icon)
            index += 1

        return frame

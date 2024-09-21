import logging
from typing import List, Set

import cv2
from numpy import ndarray

from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.processor.detected_object import DetectedObject
from fvgvisionai.processor.subprocessors.abstract_sub_processor import AbstractSubProcessor


class DoorSubProcessor(AbstractSubProcessor):

    def __init__(self, app_settings: AppSettings):
        super().__init__(app_settings.scenario_door_enabled)
        self._app_settings = app_settings
        self._door_poly1 = app_settings.scenario_door_leaving_poly
        self._door_poly2 = app_settings.scenario_door_enter_poly
        self._door_line = app_settings.scenario_door_line

        self._previous_people_in_leaving_zone: Set[int] = set()
        self._previous_people_in_entering_zone: Set[int] = set()

        self._category_set = set(obj.model_class for obj in app_settings.scenario_door_categories)

        self._total_people_entering: int = 0
        self._total_people_leaving: int = 0

        self._people_inside: int = 0
        self._logger = logging.getLogger(__name__)

    def detected_objects_near_door_zone(self, list_objects: List[DetectedObject]) -> [int, int, int, int]:
        entering_obj_set: Set[int] = set()
        leaving_obj_set: Set[int] = set()

        entering_obj_count = 0
        leaving_obj_count = 0
        for obj in (obj for obj in list_objects if obj.label_num in self._category_set):
            # lower point of bounding box, representing the feet
            feet_bb = (obj.bbox_x, obj.bbox_y + int(obj.bbox_h / 2))

            # people entering
            # if feet of person enter 1st threshold, add them to dict of people entering
            point_in_enter_polygon = cv2.pointPolygonTest(contour=self._app_settings.scenario_door_enter_poly,
                                                          pt=feet_bb,
                                                          measureDist=False)

            # people leaving
            # same logic as before but reversing the order of the thresholds
            point_in_leaving_polygon = cv2.pointPolygonTest(contour=self._app_settings.scenario_door_leaving_poly,
                                                            pt=feet_bb,
                                                            measureDist=False)

            obj.is_door_entering_zone = False
            obj.is_door_leaving_zone = False
            if point_in_enter_polygon >= 0:
                entering_obj_set.add(obj.id)

                if obj.id in self._previous_people_in_leaving_zone:
                    self._previous_people_in_leaving_zone.remove(obj.id)
                    self._people_inside += 1
                    entering_obj_count += 1
                    obj.is_door_entering_zone = True
                    obj.is_door_leaving_zone = False
            elif point_in_leaving_polygon >= 0:
                leaving_obj_set.add(obj.id)

                if obj.id in self._previous_people_in_entering_zone:
                    self._previous_people_in_entering_zone.remove(obj.id)
                    self._people_inside -= 1
                    if self._people_inside < 0:
                        self._people_inside = 0
                    leaving_obj_count += 1
                    obj.is_door_entering_zone = False
                    obj.is_door_leaving_zone = True

        self._previous_people_in_leaving_zone = leaving_obj_set
        self._previous_people_in_entering_zone = entering_obj_set

        self._total_people_entering = (self._total_people_entering + entering_obj_count) % 1_000
        self._total_people_leaving = (self._total_people_leaving + leaving_obj_count) % 1_000

        return self._total_people_entering, self._total_people_leaving, entering_obj_count, leaving_obj_count

    def draw(self, frame: ndarray) -> ndarray:
        color_zone_in = (0, 0, 255)  # Rosso
        color_zone_out = (0, 255, 0)  # Verde

        #cv2.polylines(img=frame, pts=[self._door_poly1], isClosed=True, color=color_zone_in, thickness=2)
        #cv2.polylines(img=frame, pts=[self._door_poly2], isClosed=True, color=color_zone_out, thickness=2)
        cv2.line(img=frame, pt1=self._door_line[0], pt2=self._door_line[1], color=(0, 204, 255), thickness=4)

        return frame

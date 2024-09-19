from typing import List

import cv2
from numpy import ndarray

from fvgvisionai.processor.categories import ModelCategory
from fvgvisionai.processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition
from fvgvisionai.processor.detected_object import DetectedObject
from fvgvisionai.processor.subprocessors.in_zone_sub_processor import AlarmStatus


class ParkingDecorator(AbstractFrameDecorator):
    def __init__(self,
                 parking_count: int,
                 show_category: List[ModelCategory],
                 sample_text="In zone avg time:     00:00:00"):
        super().__init__(FrameDecoratorPosition.TOP_LEFT, sample_text, 7 + len(show_category))
        self._parking_count = parking_count
        self._show_category_set = set(obj.model_class for obj in show_category)

    def draw(self, frame: ndarray,
             detected_objects: List[DetectedObject],
             in_zone_people: int,
             in_zone_avg_time: int,
             people_entering: int, people_leaving: int,
             people_raised_hand: int,
             zone_status: AlarmStatus, raised_hand_alarm_status: AlarmStatus):
        default_color = (255, 255, 255)
        lines_and_status: List[tuple] = []

        lines_and_status.append(("Tot parking :", f"{self._parking_count:3d}", default_color))
        lines_and_status.append(("  Available :", f"{self._parking_count - in_zone_people:3d}", default_color))
        lines_and_status.append(("  Occupied  :", f"{in_zone_people:3d}", default_color))

        cv2.rectangle(frame, (self.text_start_x, self.text_start_y - self.text_height - self.text_baseline),
                      (self.text_start_x + self.text_width,
                       self.text_start_y + (
                               self.text_height + self.text_row_spacing) * len(
                           lines_and_status) + self.text_row_spacing),
                      (0, 0, 0), -1)

        for index, (element_label, element_count, foreground_color) in enumerate(lines_and_status):
            cv2.putText(frame, element_label,
                        (self.text_start_x,
                         self.text_start_y + self.text_height + (self.text_height + self.text_row_spacing) * index),
                        cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                        foreground_color, self._font_thickness, lineType=cv2.LINE_AA)
            cv2.putText(frame, element_count,
                        (self.text_start_x + int(self.text_width * 0.7),
                         self.text_start_y + self.text_height + (self.text_height + self.text_row_spacing) * index),
                        cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                        foreground_color, self._font_thickness, lineType=cv2.LINE_AA)

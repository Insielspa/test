from typing import List

import cv2
from numpy import ndarray

from processor.categories import ModelCategory
from processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition
from processor.detected_object import DetectedObject
from processor.subprocessors.detected_object_sub_processor import format_duration
from processor.subprocessors.in_zone_sub_processor import AlarmStatus


class ObjectCounterDecorator(AbstractFrameDecorator):
    def __init__(self,
                 show_category: List[ModelCategory],
                 scenario_zone_enabled: bool,
                 scenario_time_in_zone_enabled: bool,
                 scenario_door_enabled: bool,
                 scenario_door_entering_enabled: bool,
                 scenario_door_entering_label: str,
                 scenario_door_leaving_enabled: bool,
                 scenario_door_leaving_label: str,
                 scenario_raise_hands_enabled: bool,
                 sample_text="In zone avg time:     00:00:00"):
        super().__init__(FrameDecoratorPosition.TOP_LEFT, sample_text, 7 + len(show_category))
        self._show_category_list = show_category
        self._show_category_set = set(obj.model_class for obj in show_category)
        self._scenario_zone_enabled = scenario_zone_enabled
        self._scenario_time_in_zone_enabled = scenario_time_in_zone_enabled
        self._scenario_door_enabled = scenario_door_enabled
        self._scenario_door_entering_enabled = scenario_door_entering_enabled
        self._scenario_door_entering_label = scenario_door_entering_label
        self._scenario_door_leaving_enabled = scenario_door_leaving_enabled
        self._scenario_door_leaving_label = scenario_door_leaving_label
        self._scenario_raise_hands_enabled = scenario_raise_hands_enabled

    def draw(self, frame: ndarray,
             detected_objects: List[DetectedObject],
             in_zone_people: int,
             in_zone_avg_time: int,
             people_entering: int, people_leaving: int,
             people_raised_hand: int,
             zone_status: AlarmStatus, raised_hand_alarm_status: AlarmStatus):

        default_color = (255, 255, 255)
        lines_and_status: List[tuple] = []

        for category in self._show_category_list:
            counter = sum(1 for obj in detected_objects if obj.label_num == category.model_class)
            category_string = f"{category.label.title()} #:".ljust(10)
            counter_string = f"{counter:3d}"
            lines_and_status.append((category_string, counter_string, default_color))

        if self._scenario_raise_hands_enabled:
            lines_and_status.append(("  Hand up:", f"{people_raised_hand:3d}", raised_hand_alarm_status.value["color"]))
        if self._scenario_zone_enabled:
            lines_and_status.append(("  In zone:", f"{in_zone_people:3d}", zone_status.value["color"]))
            if self._scenario_time_in_zone_enabled:
                lines_and_status.append(("  In zone avg time:", f"{format_duration(in_zone_avg_time)}", default_color))
        if self._scenario_door_enabled:
            if self._scenario_door_entering_enabled:
                lines_and_status.append(
                    (f"  {self._scenario_door_entering_label}:",
                     f"{people_entering:3d}", default_color))
            if self._scenario_door_leaving_enabled:
                lines_and_status.append((f"  {self._scenario_door_leaving_label}:",
                                         f"{people_leaving:3d}", default_color))

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

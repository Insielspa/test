from typing import List

from processor.detected_object import DetectedObject
from processor.measure import IntMeasure, FloatMeasure
from processor.ultralytics_classes import PERSON, BICYCLE, CAR


class DataAggregator:
    def __init__(self):
        self.people_down = IntMeasure()
        self.people_counter = IntMeasure()
        self.bikes_counter = IntMeasure()
        self.cars_counter = IntMeasure()
        self.people_in_zone_counter = IntMeasure()
        self.people_with_raised_hands = IntMeasure()

        self.door_people_entered = 0
        self.door_people_leaved = 0

        self.time_in_zone = IntMeasure()

        self.min_time_in_zone = 0
        self.max_time_in_zone = 0
        self.avg_time_in_zone = 0

        self.time_frame_source_declared = 0
        self.time_frame_acquisition = FloatMeasure()
        self.time_frame_processing = FloatMeasure()

    def clear_data(self):
        self.people_down.clear()
        self.people_counter.clear()
        self.bikes_counter.clear()
        self.cars_counter.clear()
        self.people_in_zone_counter.clear()

        self.door_people_entered = 0
        self.door_people_leaved = 0
        self.time_frame_acquisition.clear()
        self.time_frame_processing.clear()

    def measure_objects_counter(self, list_objects: List[DetectedObject]):
        self.people_counter.add(sum(1 for obj in list_objects if obj.label_num == PERSON))
        self.bikes_counter.add(sum(1 for obj in list_objects if obj.label_num == BICYCLE))
        self.cars_counter.add(sum(1 for obj in list_objects if obj.label_num == CAR))

    def measure_items_in_zone(self, value: int, min_time_in_zone: int, max_time_in_zone: int, avg_time_in_zone: int):
        self.people_in_zone_counter.add(value)

        self.min_time_in_zone = min_time_in_zone
        self.max_time_in_zone = max_time_in_zone
        self.avg_time_in_zone = avg_time_in_zone

    def measure_people_near_door(self, people_entering: int, people_leaving: int):
        self.door_people_entered += people_entering
        self.door_people_leaved += people_leaving

    def measure_time_frame_acquisition(self, time_acquired_frame: float):
        self.time_frame_acquisition.add(time_acquired_frame)

    def measure_time_frame_processing(self, process_time: float):
        self.time_frame_processing.add(process_time)

    def measure_people_with_raised_hands(self, people_raised_hand: int):
        self.people_with_raised_hands.add(people_raised_hand)

    @property
    def time_frame_acquisition_average(self) -> float:
        return self.time_frame_acquisition.average

    @property
    def time_frame_processing_average(self) -> float:
        return self.time_frame_processing.average

    @property
    def aggregation_size(self) -> float:
        return self.time_frame_processing.length

    def copy(self):
        copied_instance = DataAggregator()

        # Copy data from the current instance to the new instance
        copied_instance.people_counter = self.people_counter.copy()
        copied_instance.bikes_counter = self.bikes_counter.copy()
        copied_instance.cars_counter = self.cars_counter.copy()
        copied_instance.people_in_zone_counter = self.people_in_zone_counter.copy()
        copied_instance.door_people_entered = self.door_people_entered
        copied_instance.door_people_leaved = self.door_people_leaved

        copied_instance.min_time_in_zone = self.min_time_in_zone
        copied_instance.max_time_in_zone = self.max_time_in_zone
        copied_instance.avg_time_in_zone = self.avg_time_in_zone

        copied_instance.time_frame_source_declared = self.time_frame_source_declared
        copied_instance.time_frame_acquisition = self.time_frame_acquisition.copy()
        copied_instance.time_frame_processing = self.time_frame_processing.copy()
        copied_instance.people_with_raised_hands = self.people_with_raised_hands.copy()

        return copied_instance

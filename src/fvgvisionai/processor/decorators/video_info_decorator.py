from typing import List

import cv2
from numpy import ndarray

from config.app_settings import ModelSize
from config.app_settings_utils import ModelLibrary, ModelPrecision
from processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition


class VideoInfoDecorator(AbstractFrameDecorator):
    def __init__(self,
                 model_file_name: str,
                 model_library: ModelLibrary,
                 model_precision: ModelPrecision,
                 cuda_enabled: bool, tensor_enabled: bool, model_size: ModelSize,
                 tracking_enabled: bool,
                 zone_enabled: bool,
                 door_enabled: bool,
                 pose_enabled: bool,
                 model_skip_frames: str,
                 sample_text="MDL_FILE_NAME: yolov8n-pose-480x480-f16.engine", row=10):
        super().__init__(FrameDecoratorPosition.BOTTOM_LEFT, sample_text, row)
        self._model_file_name = model_file_name
        self._model_library = model_library
        self._model_precision = model_precision
        self._cuda_enabled = cuda_enabled
        self._tensor_enabled = tensor_enabled
        self._model_size = model_size
        self._model_skip_frames = model_skip_frames
        self._tracking_enabled = tracking_enabled
        self._pose_enabled = pose_enabled
        self._zone_enabled = zone_enabled
        self._door_enabled = door_enabled

    def draw(self, frame: ndarray, image_source_width, image_source_height, model_width: int, model_height: int):
        cv2.rectangle(frame,
                      (self.text_start_x, self.text_start_y - self.text_height - self.text_baseline),
                      (self.text_start_x + self.text_width,
                       self.text_start_y + (
                               self.text_height + self.text_row_spacing) * self.text_row + self.text_row_spacing),
                      (0, 0, 0), -1)

        lines: List[str] = [
            f"MDL_FILE: {self._model_file_name}",
            f"MDL: {self._model_library.value['name']} {self._model_precision.value['name']} {self._model_size.name}",
            f"TRACKING: {self._tracking_enabled}",
            f"ZONE: {self._zone_enabled}, DOOR: {self._door_enabled}, POSE: {self._pose_enabled}",
            f"CUDA: {self._cuda_enabled}, TENSOR: {self._tensor_enabled}, SKIP_FRAMES: {self._model_skip_frames}",
            f"IN res:   {image_source_width:4d} x {image_source_height:4d}",
            f"MDL res: {model_width:4d} x {model_height:4d}",
            f"OUT res: {self.image_out_width:4d} x {self.image_out_height:4d}"]

        for index, element in enumerate(lines):
            cv2.putText(frame, element,
                        (self.text_start_x, self.text_start_y + (self.text_height + self.text_row_spacing) * index),
                        cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                        (255, 255, 255), self._font_thickness, lineType=cv2.LINE_AA)

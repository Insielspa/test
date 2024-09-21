import logging

import cv2
from numpy import ndarray

from config.app_settings import AppSettings


class FrameResizer:
    def __init__(self, app_settings: AppSettings):
        self._logger = logging.getLogger(__name__)
        self._app_settings = app_settings
        # will be defined later
        self._image_source_width = -1
        self._image_source_height = -1

        self._image_source_force_resize = False

    def init_image_size(self, image_source_width: int, image_source_height: int) -> [int, int]:
        video_source_forced_width = self._app_settings.video_source_forced_width
        video_source_forced_height = self._app_settings.video_source_forced_height
        if self._app_settings.video_source_forced_resolution_enabled:
            image_source_original_width = image_source_width
            image_source_original_height = image_source_height
            if image_source_width > video_source_forced_width:
                ratio_height = (1.0 * video_source_forced_width / image_source_original_width)
                self._image_source_force_resize = True

                self._image_source_width = self._app_settings.video_source_forced_width
                self._image_source_height = int(ratio_height * image_source_original_height)
            elif image_source_height > video_source_forced_height:
                ratio_width = (1.0 * video_source_forced_height / image_source_original_height)
                self._image_source_force_resize = True

                self._image_source_width = int(ratio_width * image_source_original_width)
                self._image_source_height = self._app_settings.video_source_forced_height
            else:
                self._image_source_force_resize = False
                self._image_source_width = image_source_width
                self._image_source_height = image_source_height

            if self._image_source_force_resize:
                self._logger.warning(
                    f"source image size {image_source_original_width}x{image_source_original_height} is changed to"
                    f" {self._image_source_width}x{self._image_source_height}")
            else:
                self._logger.info(f"source image size is {self._image_source_width}x{self._image_source_height} ")

            return [self._image_source_width, self._image_source_height]
        else:
            self._image_source_width = image_source_width
            self._image_source_height = image_source_height
            self._logger.info(f"source image size is {self._image_source_width}x{self._image_source_height} ")
            return [self._image_source_width, self._image_source_height]

    def resize_frame(self, frame: ndarray) -> ndarray:
        if self._image_source_force_resize:
            return cv2.resize(frame, (self._image_source_width, self._image_source_height))
        return frame

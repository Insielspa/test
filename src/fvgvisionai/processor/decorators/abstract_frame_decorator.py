from enum import Enum

import cv2


class FrameDecoratorPosition(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3


class AbstractFrameDecorator:
    def __init__(self, position: FrameDecoratorPosition,
                 sample_text: str, row=3):
        self._font = cv2.FONT_HERSHEY_SIMPLEX
        self._font_scale = 0.5
        self._font_thickness = 1

        self.text_start_x = 0
        self.text_start_y = 0

        self.text_width = 0
        self.text_height = 0

        self.text_row_spacing = 0
        self.text_height = 0

        self.text_row = row

        self.image_out_width = 0
        self.image_out_height = 0

        self._text_sample = sample_text
        self._text_position = position
        self.text_baseline = 0

        self.init_image_size(0, 0)

    def init_image_size(self, image_width: int, image_height: int):
        # Calcola la posizione in basso a destra
        (text_width, text_height), baseline = cv2.getTextSize(self._text_sample, self._font, self._font_scale,
                                                              self._font_thickness)

        self.image_out_width = image_width
        self.image_out_height = image_height

        if self._text_position == FrameDecoratorPosition.TOP_LEFT:
            self.text_start_x = 0
            self.text_start_y = 0
        elif self._text_position == FrameDecoratorPosition.TOP_RIGHT:
            self.text_start_x = image_width - text_width - baseline
            self.text_start_y = 0
        elif self._text_position == FrameDecoratorPosition.BOTTOM_LEFT:
            self.text_start_x = 0
            self.text_start_y = image_height - baseline - text_height - text_height * self.text_row
        elif self._text_position == FrameDecoratorPosition.BOTTOM_RIGHT:
            self.text_start_x = image_width - text_width - baseline
            self.text_start_y = image_height - baseline - text_height * self.text_row

        self.text_width = text_width
        self.text_height = text_height
        self.text_row_spacing = baseline

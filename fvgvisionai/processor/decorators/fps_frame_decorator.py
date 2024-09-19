import cv2
from numpy import ndarray

from fvgvisionai.processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition


class FpsFrameDecorator(AbstractFrameDecorator):
    def __init__(self,
                 sample_text="MDL: 00000 fps, 00000 ms"):
        super().__init__(FrameDecoratorPosition.BOTTOM_RIGHT, sample_text, row=3)

    def draw(self, frame: ndarray,
             input_time_ms: float, stream_time_ms: float, process_time_ms: float, output_fps: float):
        cv2.rectangle(frame, (
            self.text_start_x - self.text_row_spacing,
            self.text_start_y - self.text_height - self.text_row_spacing),
                      (self.image_out_width, self.image_out_height),
                      (0, 0, 0), -1)

        cv2.putText(frame, f"IN:   {1000 / max(stream_time_ms, 1):#5.1f} fps, {stream_time_ms:#5.1f} ms",
                    (self.text_start_x, self.text_start_y + (self.text_height + self.text_row_spacing) * 0),
                    cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                    (255, 255, 255), self._font_thickness, lineType=cv2.LINE_AA)
        cv2.putText(frame, f"MDL: {1000 / max(process_time_ms, 1):#5.1f} fps, {max(process_time_ms, 1):#5.1f} ms",
                    (self.text_start_x, self.text_start_y + (self.text_height + self.text_row_spacing) * 1),
                    cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                    (255, 255, 255), self._font_thickness, lineType=cv2.LINE_AA)
        cv2.putText(frame, f"OUT: {output_fps:#5.1f} fps, {1000 / output_fps:#5.1f} ms",
                    (self.text_start_x, self.text_start_y + (self.text_height + self.text_row_spacing) * 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    self._font_scale,
                    (255, 255, 255), self._font_thickness, lineType=cv2.LINE_AA)

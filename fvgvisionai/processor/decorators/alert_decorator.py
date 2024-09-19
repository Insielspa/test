import cv2
from numpy import ndarray

from fvgvisionai.common.app_alarm import AlarmStatus
from fvgvisionai.common.video_utils import draw_icon
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition


def is_alarm_status(zone_alarm_status) -> bool:
    return (zone_alarm_status == AlarmStatus.ALARM_WITH_NOTIFICATION or
            zone_alarm_status == AlarmStatus.ALARM_ALREADY_NOTIFIED)


class AlertFrameDecorator(AbstractFrameDecorator):
    def __init__(self, app_settings: AppSettings, sample_text="MDL: 00000 fps, 00000 ms"):
        super().__init__(position=FrameDecoratorPosition.BOTTOM_RIGHT, sample_text=sample_text)
        # Carica l'immagine da sovrapporre
        self.in_zone_image = cv2.imread(app_settings.alert_in_zone_icon, -1)
        self.raised_hand_image = cv2.imread('assets/images/alert_raised_hand.png', -1)

    def draw(self, frame: ndarray, zone_alarm_status, raised_hand_alarm_status):
        if is_alarm_status(zone_alarm_status):
            overlay_image = self.in_zone_image
        elif is_alarm_status(raised_hand_alarm_status):
            overlay_image = self.raised_hand_image
        else:
            return

        # Calcola le coordinate per posizionare l'immagine nel bordo superiore in mezzo
        x_offset = (self.image_out_width - overlay_image.shape[1]) // 2
        y_offset = 0

        draw_icon(frame, x_offset, y_offset, overlay_image)

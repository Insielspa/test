from datetime import datetime

import cv2
import pytz
from numpy import ndarray

from processor.decorators.abstract_frame_decorator import AbstractFrameDecorator, FrameDecoratorPosition

# Specifica la zona oraria di Roma
zona_oraria_roma = "Europe/Rome"


def visualizza_ora_zona_oraria(zona_oraria):
    # Ottieni l'oggetto della data e ora corrente
    ora_corrente = datetime.now()

    # Imposta la zona oraria desiderata (Roma in questo caso)
    zona_oraria_desiderata = pytz.timezone(zona_oraria)

    # Converti l'ora corrente nella zona oraria desiderata
    ora_corrente_zona_oraria = ora_corrente.astimezone(zona_oraria_desiderata)

    # Formatta l'ora nella stringa desiderata
    formato_ora = "%Y-%m-%d %H:%M:%S"
    ora_formattata = ora_corrente_zona_oraria.strftime(formato_ora)

    return ora_formattata


class TimeDecorator(AbstractFrameDecorator):
    def __init__(self,
                 sample_text="9999-99-99 99:99:99"):
        super().__init__(position=FrameDecoratorPosition.TOP_RIGHT, sample_text=sample_text, row=3)

    def draw(self, frame: ndarray):
        cv2.rectangle(frame, (
            self.text_start_x - self.text_row_spacing,
            self.text_start_y - self.text_height - self.text_row_spacing),
                      (self.image_out_width, self.text_start_y + self.text_height + self.text_row_spacing),
                      (0, 0, 0), -1)

        ora_corrente = visualizza_ora_zona_oraria(zona_oraria_roma)

        cv2.putText(frame, ora_corrente,
                    (self.text_start_x, self.text_start_y + self.text_height),
                    cv2.FONT_HERSHEY_SIMPLEX, self._font_scale,
                    (255, 255, 255), self._font_thickness, lineType=cv2.LINE_AA)

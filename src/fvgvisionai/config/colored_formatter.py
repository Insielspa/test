# Crea un formatter personalizzato
import logging

from fvgvisionai.common.ansi_color import ANSI_RESET, ANSI_WHITE_BOLD_TEXT, ANSI_BG_GREEN, ANSI_BG_YELLOW, ANSI_BG_BLUE, \
    ANSI_BG_RED, ANSI_BG_CYAN


def _truncate(value: str, max_size: int) -> str:
    if len(value) > max_size:
        result = value[:(max_size - 3)] + '...'  # Limita a 20 caratteri e aggiungi puntini
    else:
        result = value.rjust(max_size)  # Allinea a sinistra con spazi
    return result


class ColoredFormatter(logging.Formatter):
    format = f"%(asctime)s.%(msecs)03d %(threadName)16s ##custom_package## ##custom_file_name##:%(lineno)4d %%LEVEL%% %(message)s{ANSI_RESET}"

    __OLD = "%%LEVEL%%"

    FORMATS = {
        logging.DEBUG: format.replace(__OLD,
                                      f"{ANSI_RESET}{ANSI_WHITE_BOLD_TEXT}{ANSI_BG_GREEN} D {ANSI_RESET}") + ANSI_RESET,
        logging.INFO: format.replace(__OLD,
                                     f"{ANSI_RESET}{ANSI_BG_BLUE}{ANSI_WHITE_BOLD_TEXT} I {ANSI_RESET}") + ANSI_RESET,
        logging.WARNING: format.replace(__OLD,
                                        f"{ANSI_RESET}{ANSI_BG_YELLOW}{ANSI_WHITE_BOLD_TEXT} W {ANSI_RESET}") + ANSI_RESET,
        logging.ERROR: format.replace(__OLD,
                                      f"{ANSI_RESET}{ANSI_BG_RED}{ANSI_WHITE_BOLD_TEXT} E {ANSI_RESET}") + ANSI_RESET,
        logging.CRITICAL: format.replace(__OLD,
                                         f"{ANSI_RESET}{ANSI_BG_CYAN}{ANSI_WHITE_BOLD_TEXT} F {ANSI_RESET}") + ANSI_RESET
    }

    def format(self, record):
        package = ".".join(record.name.split('.')[:-1])
        filename = record.filename

        log_fmt = self.FORMATS.get(record.levelno)
        log_fmt = log_fmt.replace("##custom_package##", _truncate(package, 30))
        log_fmt = log_fmt.replace("##custom_file_name##", _truncate(filename, 30))
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

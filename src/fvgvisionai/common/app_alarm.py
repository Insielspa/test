import logging
from enum import Enum
from typing import Callable

from common.app_timer import AppTimer


class AlarmStatus(Enum):
    NORMAL = {"value": 0, "color": (255, 255, 255), "message": "NORMAL"}
    WARM_UP = {"value": 1, "color": (0, 255, 255), "message": "\tWARMUP"}
    ALARM_WITH_NOTIFICATION = {"value": 3, "color": (0, 0, 255), "message": "\t\t\tALARM_WITH_NOTIFICATION"}
    ALARM_ALREADY_NOTIFIED = {"value": 4, "color": (0, 0, 255), "message": "\t\tALARM"}


class AppAlarm:
    def __init__(self, is_danger_check: Callable[[int], bool],
                 scenario_zone_cold_down_time=2,
                 scenario_zone_time_limit=10):
        self._warm_up_timer = AppTimer()
        self._alert_timer = AppTimer()
        self._cold_down_timer = AppTimer()
        self._status = AlarmStatus.NORMAL
        self._is_danger_check = is_danger_check
        self.COLD_DOWN_TIME_LIMIT_MS = scenario_zone_cold_down_time * 1_000.0
        self.TIME_LIMIT_MS = scenario_zone_time_limit * 1_000.0
        self._logger = logging.getLogger(__name__)

    def manage(self, value: int) -> AlarmStatus:
        if self._status == AlarmStatus.NORMAL:
            # se situazione di pericolo, avvio WARM_UP e timer
            if not self._is_danger_check(value):
                self._status = AlarmStatus.NORMAL
            else:
                self._status = AlarmStatus.WARM_UP
                self._warm_up_timer.start()
        elif self._status == AlarmStatus.WARM_UP:
            self._status = self._state_and_cold_down_handler(measure=value,
                                                             state_timer=self._warm_up_timer,
                                                             current_status=AlarmStatus.WARM_UP,
                                                             previous_status=AlarmStatus.NORMAL,
                                                             nexus_status=AlarmStatus.ALARM_WITH_NOTIFICATION)
        elif self._status == AlarmStatus.ALARM_WITH_NOTIFICATION:
            # cambio per inviare notifica (dura 1 frame)
            self._cold_down_timer.stop()
            self._alert_timer.start()
            self._status = AlarmStatus.ALARM_ALREADY_NOTIFIED
        elif self._status == AlarmStatus.ALARM_ALREADY_NOTIFIED:
            self._status = self._state_and_cold_down_handler(measure=value,
                                                             state_timer=self._alert_timer,
                                                             current_status=AlarmStatus.ALARM_ALREADY_NOTIFIED,
                                                             previous_status=AlarmStatus.NORMAL,
                                                             nexus_status=AlarmStatus.NORMAL)
        return self._status

    def _state_and_cold_down_handler(self, measure: int,
                                     state_timer: AppTimer,
                                     current_status: AlarmStatus,
                                     previous_status: AlarmStatus,
                                     nexus_status: AlarmStatus) -> AlarmStatus:
        if self._is_danger_check(measure):
            # blocchiamo timer per sicurezza
            self._cold_down_timer.stop()
            if state_timer.elapsed_time > self.TIME_LIMIT_MS:
                state_timer.stop()
                return nexus_status
        else:
            if not self._cold_down_timer.is_running:
                self._cold_down_timer.start()
            else:
                if self._cold_down_timer.elapsed_time > self.COLD_DOWN_TIME_LIMIT_MS:
                    self._cold_down_timer.stop()
                    return previous_status

        return current_status

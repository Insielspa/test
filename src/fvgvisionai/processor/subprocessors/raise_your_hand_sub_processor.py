import logging
import traceback
from typing import List

import numpy as np

from common.app_alarm import AppAlarm, AlarmStatus
from config.app_settings import AppSettings
from processor.detected_object import DetectedObject
from processor.subprocessors.abstract_sub_processor import AbstractSubProcessor

# coco keypoint indexes
KP_NOSE = 0
KP_LEFT_EYE = 1
KP_RIGHT_EYE = 2
KP_LEFT_EAR = 3
KP_RIGHT_EAR = 4
KP_LEFT_SHOULDER = 5
KP_RIGHT_SHOULDER = 6
KP_LEFT_ELBOW = 7
KP_RIGHT_ELBOW = 8
KP_LEFT_WRIST = 9
KP_RIGHT_WRIST = 10
KP_LEFT_HIP = 11
KP_RIGHT_HIP = 12
KP_LEFT_KNEE = 13
KP_RIGHT_KNEE = 14
KP_LEFT_ANKLE = 15
KP_RIGHT_ANKLE = 16


def is_danger(raised_hands: int) -> bool:
    return raised_hands > 0


class RaiseYourHandSubProcessor(AbstractSubProcessor):
    def __init__(self, app_settings: AppSettings):
        super().__init__(app_settings.scenario_pose_enabled)
        self._app_settings = app_settings
        self._alarm = AppAlarm(is_danger)
        self._logger = logging.getLogger(__name__)

    def detected_raised_hands(self, list_objects: List[DetectedObject]) -> [AlarmStatus, int]:
        counter = 0
        for obj in (obj for obj in list_objects if obj.label_num == 0):
            obj.raised_hands = False
            for bboxe_pose, keyps_pose in zip(obj.bbox_xy, obj.keypoints):
                h = keyps_pose.orig_shape[0]
                w = keyps_pose.orig_shape[1]

                # keypoint data
                xyn = keyps_pose.xyn[0]

                # useful keypoint coordinates
                nose_x, nose_y = self._extract_kp_xy(xyn, KP_NOSE, w, h)
                lwri_x, lwri_y = self._extract_kp_xy(xyn, KP_LEFT_WRIST, w, h)
                rwri_x, rwri_y = self._extract_kp_xy(xyn, KP_RIGHT_WRIST, w, h)
                lelb_x, lelb_y = self._extract_kp_xy(xyn, KP_LEFT_ELBOW, w, h)
                relb_x, relb_y = self._extract_kp_xy(xyn, KP_RIGHT_ELBOW, w, h)
                lear_x, lear_y = self._extract_kp_xy(xyn, KP_LEFT_EAR, w, h)
                rear_x, rear_y = self._extract_kp_xy(xyn, KP_RIGHT_EAR, w, h)
                leye_x, leye_y = self._extract_kp_xy(xyn, KP_LEFT_EYE, w, h)
                reye_x, reye_y = self._extract_kp_xy(xyn, KP_RIGHT_EYE, w, h)

                # select one point among eyes, ears and nose as height threshold point to determine raised hand (some may be undefined)
                ref_x, ref_y = 0, 0
                for point in [(nose_x, nose_y), (leye_x, leye_y)], (reye_x, reye_y), (lear_x, lear_y), (rear_x, rear_y):
                    if point != (0, 0):
                        ref_x, ref_y = point[0], point[1]

                # start of raised hand logic: evaluation of wrist height with respect to the selected reference and forearm angle with respect to the vertical
                # tolerance in degrees for the angle of the arm relative to the vertical
                threshold = 30
                # detected object flag

                # ref_y puo' essere una tupla
                if isinstance(ref_y, tuple):
                    ref_y = ref_y[1]

                if ref_x != 0:
                    # right arm
                    if rwri_y != 0 and rwri_x != 0 and relb_y != 0 and relb_x != 0:
                        r_angle = round(np.degrees(np.arctan2((rwri_y - relb_y), (rwri_x - relb_x))))
                        if abs(-90 - r_angle) <= threshold and rwri_y < ref_y:
                            obj.raised_hands = True

                    # left arm
                    if lwri_y != 0 and lwri_x != 0 and lelb_y != 0 and lelb_x != 0:
                        l_angle = round(np.degrees(np.arctan2((lwri_y - lelb_y), (lwri_x - lelb_x))))
                        if abs(-90 - l_angle) <= threshold and lwri_y < ref_y:
                            obj.raised_hands = True
            if obj.raised_hands:
                counter += 1

        alarm_status = self._alarm.manage(counter)

        return alarm_status, counter

    def _extract_kp_xy(self, t, i, w, h):
        """
        Keypoint extraction from xyn tensor contained in pose results
        Args:
            t (tensor): xyn object from pose result
            i (int): index of the keypoint to extract
            w,h (int): frame dimensions, necessary to calculate the kp in pixels
        """
        try:
            return int(t[i][0] * w), int(t[i][1] * h)
        except Exception as e:
            self._logger.error("Unexpected error %s " % e)
            traceback.print_exc()
            return 0, 0

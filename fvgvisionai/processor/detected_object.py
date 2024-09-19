from typing import List, Optional

from numpy import int32
from ultralytics.engine.results import Keypoints


class DetectedObject:
    def __init__(self, object_id: int, label_num: int, label_str: str, color: list, conf: float, bbox_xy: List[int32],
                 bbox_wh: List[int32], keypoints: Optional[Keypoints]) -> None:
        """
        class of objects detected by the object detection algorithm

        attributes:
            __init__ id: id assigned to object, useful only with tracking
            __init__ label_num: number of object category
            __init__ label_str: label of object category
            __init__ conf: confidence of the detection
            __init__ bbox_xy: bounding box corners coordinates [x1,y1,x2,y2]
            __init__ bbox_wh: bounding box center and width/height [x,y,w,h]
            TODO
            is_down: bool variable telling if person is on the ground
            is_in_zone: bool variable telling if object is inside zone
            time_in_zone: amount of time inside the zone
            info: empty dict to fill with object's information
        """
        self.id = object_id
        self.label_num = label_num
        self.label_str = label_str
        self.conf = conf
        self.color = color
        self.bbox_xy = bbox_xy  # left upper corner and right lower corner
        self.bbox_wh = bbox_wh  # center of bbox together with width and height
        self.keypoints: Optional[Keypoints] = keypoints
        self.track = []
        self.is_moving = False
        self.direction = "-"
        self.speed = 0
        self.is_down = False
        self.is_in_zone = False
        self.time_in_zone = 0
        self.info = {}

        self.raised_hands = False
        self.is_door_entering_zone = False
        self.is_door_leaving_zone = False

        self.bbox_x1, self.bbox_y1, self.bbox_x2, self.bbox_y2 = self.bbox_xy
        self.bbox_x, self.bbox_y, self.bbox_w, self.bbox_h = self.bbox_wh

from enum import Enum


class NodeTemplateEnum(Enum):
    IOT_HUB_NOTIFICATION = "IOT_HUB_NOTIFICATION"
    INPUT_RESIZER = "INPUT_RESIZER"
    DISPLAY = "DISPLAY"
    INPUT_STREAM_FPS_LIMITER = "INPUT_STREAM_FPS_LIMITER"
    INPUT_STREAM = "INPUT_STREAM"
    OUTPUT_IMAGE = "OUTPUT_IMAGE"
    OUTPUT_STREAM = "OUTPUT_STREAM"
    OUTPUT_STREAM_FPS_LIMITER = "OUTPUT_STREAM_FPS_LIMITER"
    SKIP_FRAMES = "SKIP_FRAMES"
    SCENARIO_DOOR = "SCENARIO_DOOR"
    SCENARIO_IN_ZONE = "SCENARIO_IN_ZONE"
    SCENARIO_PARKING = "SCENARIO_PARKING"
    SCENARIO_RAISED_HANDS = "SCENARIO_RAISED_HANDS"
    ULTRALYTICS_PROCESSING = "ULTRALYTICS_PROCESSING"
    ULTRALYTICS_CUSTOM_MODEL_PROCESSING = "ULTRALYTICS_CUSTOM_MODEL_PROCESSING"

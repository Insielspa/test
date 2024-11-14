# Settings

There are many parameters to customize FVG Vision AI behaviour. Parameters are subdivided in sections.

## Configuration File Structure

The configuration file consists of several sections. Each section is responsible for different settings such as
application details, video input and output, model configurations, and alert management.

---

### Section: `application`

This section contains basic information about the application.

- **name**: Name of the application.
    - **Default**: `FVG Vision AI`
- **version**: Current version of the application.
    - **Default**: `0.1.0`

---

### Section: `settings`

General configuration for logging, video input, and display options.

- **LOGGING_LEVEL**: Log level.
    - **Possible values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`
    - **Default**: `INFO`
- **VIDEO_SOURCE**: Path to the video file for the input stream.
    - **Default**: `assets/videos/trieste_800x600.mp4`
- **VIDEO_SOURCE_FORCED_FPS_ENABLED**: If `true`, forces FPS setting.
    - **Default**: `false`
- **VIDEO_SOURCE_FORCED_FPS_VALUE**: Forces FPS value for the input stream.
    - **Default**: `12`

---

### Section: `video_source`

Settings for the video source.

- **VIDEO_SOURCE_MODE**: Input video mode.
    - **Possible values**: `STREAM`, `IMAGE`, `NEXT`
    - **Default**: `STREAM`
- **VIDEO_SOURCE_IMAGE**: Path to the image (only if `VIDEO_SOURCE_MODE` is `IMAGE`).
    - **Default**: `assets/images/static_sources_800x600.png`
- **VIDEO_SOURCE_FORCED_RESOLUTION_ENABLED**: If `true`, forces resolution.
    - **Default**: `true`
- **VIDEO_SOURCE_FORCED_RESOLUTION_VALUE**: Forced resolution (e.g., `800, 600`).
    - **Default**: `800, 600`

---

### Section: `display`

Display configuration options.

- **DISPLAY_COUNT_ENABLED**: If `true`, displays object count.
    - **Default**: `true`
- **DISPLAY_COUNT_CATEGORIES**: Categories for which to display counts.
    - **Possible values**: `PERSON`, `CAR`, `MOTORCYCLE`, `BICYCLE`
    - **Default**: `PERSON | CAR | MOTORCYCLE | BICYCLE`
- **DISPLAY_TIME_IN_ZONE_ENABLED**: If `true`, displays time in the zone.
    - **Default**: `false`
- **DISPLAY_FPS_ENABLED**: If `true`, displays FPS.
    - **Default**: `true`
- **DISPLAY_TIME**: If `true`, displays time.
    - **Default**: `true`
- **DISPLAY_VIDEO_INFO_ENABLED**: If `true`, displays video information.
    - **Default**: `false`
- **DISPLAY_ALERT_ICON_ENABLED**: If `true`, displays alert icon.
    - **Default**: `true`

---

### Section: `video_output`

Settings for video output.

- **VIDEO_OUTPUT_STREAM**: If `true`, enables HLS stream output.
    - **Default**: `true`
- **VIDEO_OUTPUT_FPS**: FPS for the video output.
    - **Default**: `10`
- **VIDEO_OUTPUT_STREAM_PATH**: Path to store the HLS output stream.
    - **Default**: `/mnt/hls`
- **VIDEO_OUTPUT_STREAM_HLS_BANDWIDTH**: Bandwidth for HLS streaming in KB.
    - **Default**: `1800`
- **VIDEO_OUTPUT_STREAM_HLS_TIME**: HLS segment duration in seconds.
    - **Default**: `1`
- **VIDEO_OUTPUT_STREAM_HLS_GOP**: HLS GOP length in seconds.
    - **Default**: `2`

#### Image Output Settings

- **VIDEO_OUTPUT_IMAGE**: If `true`, enables image output.
    - **Default**: `true`
- **VIDEO_OUTPUT_IMAGE_TYPE**: Image format for output.
    - **Possible values**: `JPEG`, `WEBP`
    - **Default**: `WEBP`
- **VIDEO_OUTPUT_IMAGE_QUALITY**: Image quality (0-100).
    - **Default**: `50`
- **VIDEO_OUTPUT_IMAGE_PORT**: Port for image output.
    - **Default**: `5000`
- **VIDEO_OUTPUT_IMAGE_PASSWORD**: Password for image output access.
    - **Default**: `simple_access1`

---

### Section: `model`

Model configuration settings.

- **MODEL_LIBRARY**: Library to use for the model.
    - **Possible values**: `ultralytics`, `passthrough`
    - **Default**: `ultralytics`
- **MODEL_SIZE**: Size of the model.
    - **Possible values**: `nano`, `small`, `medium`, `large`, `xlarge`
    - **Default**: `nano`
- **MODEL_PRECISION**: Precision for the model.
    - **Possible values**: `float32`, `float16`, `int8`
    - **Default**: `float16`
- **MODEL_IMAGE_SIZE**: Image size for the model.
    - **Possible values**: `640x640`, `512x512`, `480x480`
    - **Default**: `640x640`
- **MODEL_USE_TENSORRT**: If `true`, enables TensorRT for inference.
    - **Default**: `true`
- **MODEL_FILENAME**: Path to custom model file (if any).
    - **Default**: `None`
- **MODEL_ID**: Model identifier to use.
    - **Possible values**: `yolo8`, `yolo11`
    - **Default**: `yolo8`
- **MODEL_SKIP_FRAMES**: Skip frames for faster inference.
    - **Default**: `false`
- **MODEL_SKIP_FRAMES_MASK**: Mask for skipped frames. When enabled, this setting allows you to skip certain frames to
  reduce processing load. You can
  define the frames to skip using a mask where: **0** indicates a frame to skip (not analyzed); **1** indicates a frame to analyze (processed).
  
  **Example**: `0111 1101 1011 0111` would process frames at positions 1, 2, 3, 5, 6, 8, and so on, while skipping
        others.

- **MODEL_CONFIDENCE**: Confidence threshold for detection.
    - **Default**: `0.15`
- **MODEL_IOU**: IoU threshold for detection.
    - **Default**: `0.40`
- **MODEL_CATEGORIES**: Categories to detect.
    - **Possible values**: `ALL`, `PERSON`, `BICYCLE`, `CAR`, `MOTORCYCLE`, `BUS`, `TRUCK`
    - **Default**: `ALL`
- **MODEL_DO_TRACKING**: If `true`, enables object tracking.
    - **Default**: `false`

---

### Section: `space_analysis`

Space analysis settings.

- **SCENARIO_IN_ZONE**: If `true`, enables zone analysis.
    - **Default**: `false`
- **SCENARIO_IN_ZONE_COORDS**: Coordinates of the monitored zone.
    - **Default**: `31,298|495,226|699,318|11,489`
- **SCENARIO_IN_ZONE_COLD_DOWN_TIME_S**: Cooldown time in seconds after zone detection.
    - **Default**: `2`
- **SCENARIO_IN_ZONE_TIME_LIMIT_S**: Time limit for detection in the zone.
    - **Default**: `10`
- **SCENARIO_IN_ZONE_DANGER_LIMIT**: Limit for the number of objects in the zone.
    - **Default**: `4`
- **SCENARIO_IN_ZONE_CATEGORIES**: Categories to track in the zone.
    - **Default**: `PERSON`

#### Parking Space Analysis

- **SCENARIO_PARKING**: If `true`, enables parking analysis.
    - **Default**: `false`
- **SCENARIO_PARKING_COORDS**: Coordinates for parking space analysis.
    - **Default**: `31,298|495,226|699,318|11,489`
- **SCENARIO_PARKING_COLD_DOWN_TIME_S**: Cooldown time for parking analysis.
    - **Default**: `2`
- **SCENARIO_PARKING_TIME_LIMIT_S**: Time limit for parking analysis.
    - **Default**: `10`
- **SCENARIO_PARKING_DANGER_LIMIT**: Limit for parking analysis.
    - **Default**: `4`
- **SCENARIO_PARKING_CATEGORIES**: Categories for parking analysis.
    - **Default**: `PERSON`

#### Raised Hand Detection

- **SCENARIO_RAISED_HAND**: If `true`, enables hand raising detection.
    - **Default**: `false`

#### Door Detection

- **SCENARIO_DOOR**: If `true`, enables door detection.
    - **Default**: `false`
- **SCENARIO_DOOR_COORDS**: Coordinates for door detection.
    - **Default**: `198,400|700,405`
- **SCENARIO_DOOR_ENTERING_ENABLED**: If `true`, enables entering detection.
    - **Default**: `true`
- **SCENARIO_DOOR_ENTERING_LABEL**: Label for entering detection.
    - **Default**: `Door_entering`
- **SCENARIO_DOOR_LEAVING_ENABLED**: If `true`, enables leaving detection.
    - **Default**: `true`
- **SCENARIO_DOOR_LEAVING_LABEL**: Label for leaving detection.
    - **Default**: `Door_leaving`

---

### Section: `alert`

Alert configuration.

- **ALERT_IN_ZONE_ICON**: Path to the alert icon.
    - **Default**: `assets/images/alert_people_in_zone.png`

---

### Section: `notification`

Notification configuration.

- **NOTIFICATION_AZURE_CONNECTION_STRING**: Connection string to Azure iot hub.
    - **Default**: `INVALID VALUE`
- **NOTIFICATION_DEVICE_ID**: device name from the azure point of view.
    - **Default**: `INVALID VALUE`
- **NOTIFICATION_ENABLED**: enable or disable notification system throw Azure.
    - **Default**: `false`
- **NOTIFICATION_CAMERA_ID**: camera id from the azure point of view.
    - **Default**: `insecam`
- **NOTIFICATION_DATA_AGGREGATION_TIME_MS**: the data sent to Iot Hub is grouped. This parameter specifies the duration
  of the data aggregation.
    - **Default**: `10000 ms`

---

### Section: `benchmark`

Benchmarking settings.

- **BENCHMARK_DURATION_TIME_MS**: Duration of the benchmark test in milliseconds.
    - **Default**: `60_000`

- **BENCHMARK_WARMUP_TIME_MS**: Warm-up time for the benchmark test in milliseconds.
    - **Default**: `10_000`

- **BENCHMARK_RESULTS_FILE_NAME**: File name for storing benchmark results.
    - **Default**: `./benchmark.xlsx`

- **BENCHMARK_DATA_AGGREGATION_TIME_MS**: Data aggregation time for benchmarking in milliseconds.
    - **Default**: `2_000`

---

### Section: `logging`

Module-specific logging settings.

The following log levels are available:

- **DEBUG**: Detailed information for diagnosing issues.
- **INFO**: General operational information, typically to track the progress of the application.
- **WARNING**: Information about potential issues that are not errors but should be looked into.
- **ERROR**: Information about errors that are preventing parts of the application from functioning.
- **CRITICAL**: Serious errors that may cause the application to stop or behave unexpectedly.

- **PIL**: Logging level for PIL (Python Imaging Library).
    - **Default**: `ERROR`

- **azure.iot**: Logging level for Azure IoT.
    - **Default**: `ERROR`

- **paho**: Logging level for Paho MQTT client.
    - **Default**: `ERROR`

- **pongo.config**: Logging level for Pongo configuration.
    - **Default**: `INFO`

- **pongo.input**: Logging level for Pongo input module.
    - **Default**: `INFO`

- **pongo.notify**: Logging level for Pongo notifications.
    - **Default**: `WARNING`

---

Each section provides flexibility in configuring different aspects of the application, from source and output settings
to model parameters, space analysis, notifications, and benchmarking.

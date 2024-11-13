# Settings

There are many parameters to customize FVG Vision AI behaviour. Parameters are subdivided in sections.

## [application]

- **name**: Specifies the name of the application.
- **version**: Indicates the current version of the application.

---

## [settings]

- **LOGGING_LEVEL**: Sets the logging verbosity level for the application. Acceptable values are `DEBUG`, `INFO`,
  `WARNING`, and `ERROR`, where `DEBUG` is the most verbose and `ERROR` is the least.

---

## [video_source]

- **VIDEO_SOURCE**: Path to the video file or stream source used as input.
- **VIDEO_SOURCE_FORCED_FPS_ENABLED**: Boolean option to force a specific frame-per-second (FPS) rate on the video
  source if enabled.
- **VIDEO_SOURCE_FORCED_FPS_VALUE**: The FPS value to apply if `VIDEO_SOURCE_FORCED_FPS_ENABLED` is set to `true`.
- **VIDEO_SOURCE_MODE**: Defines the source mode for video input. Options are `STREAM`, `IMAGE`, or `NEXT`.
- **VIDEO_SOURCE_IMAGE**: Path to a static image file if `VIDEO_SOURCE_MODE` is set to `IMAGE`.
- **VIDEO_SOURCE_FORCED_RESOLUTION_ENABLED**: Boolean to enable forced resolution resizing of the video source.
- **VIDEO_SOURCE_FORCED_RESOLUTION_VALUE**: Resolution value (width, height) to use if
  `VIDEO_SOURCE_FORCED_RESOLUTION_ENABLED` is enabled. Examples: `1920,1080` or `800,600`.

---

## [display]

- **DISPLAY_COUNT_ENABLED**: Enables on-screen counting of detected objects.
- **DISPLAY_COUNT_CATEGORIES**: Specifies which object categories to count on display. Options include `PERSON`, `CAR`,
  `MOTORCYCLE`, `BICYCLE`, `BUS`, and `TRUCK`.
- **DISPLAY_TIME_IN_ZONE_ENABLED**: Enables display of time spent by objects in specified zones.
- **DISPLAY_FPS_ENABLED**: Shows the frame rate of the video source on-screen.
- **DISPLAY_TIME**: Displays the current time overlay on the video output.
- **DISPLAY_VIDEO_INFO_ENABLED**: Enables the display of additional video information on-screen.
- **DISPLAY_ALERT_ICON_ENABLED**: Shows alert icons when certain conditions are met.

---

## [video_output]

- **VIDEO_OUTPUT_STREAM**: Enables streaming output of video.
- **VIDEO_OUTPUT_FPS**: Sets the frame rate for the output video stream.
- **VIDEO_OUTPUT_STREAM_PATH**: File path or network location where the video stream will be output.
- **VIDEO_OUTPUT_STREAM_HLS_BANDWIDTH**: Sets the bandwidth for HLS (HTTP Live Streaming) output in KB. Typical values:
  `500`, `1000`, `2000`.
- **VIDEO_OUTPUT_STREAM_HLS_TIME**: Duration in seconds for each HLS video segment.
- **VIDEO_OUTPUT_STREAM_HLS_GOP**: Sets the Group of Pictures (GOP) for the HLS stream, affecting streaming performance
  and quality.
- **VIDEO_OUTPUT_IMAGE**: Enables output as static image snapshots.
- **VIDEO_OUTPUT_IMAGE_TYPE**: Format of output images, either `JPEG` or `WEBP`.
- **VIDEO_OUTPUT_IMAGE_QUALITY**: Compression quality for output images (0-100).
- **VIDEO_OUTPUT_IMAGE_PORT**: Port number for serving image output over HTTP.
- **VIDEO_OUTPUT_IMAGE_PASSWORD**: Password for securing image access.

---

## [model]

- **MODEL_LIBRARY**: Specifies the AI model library. Options are `ultralytics` or `passthrough`.
- **MODEL_SIZE**: Defines the model size: `nano`, `small`, `medium`, `large`, or `xlarge`.
- **MODEL_PRECISION**: Precision type for model processing. Options: `float32`, `float16`, `int8`.
- **MODEL_IMAGE_SIZE**: Image size used by the model for inference, e.g., `640x640`, `512x512`, `480x480`.
- **MODEL_USE_TENSORT**: Boolean to enable TensorRT for model acceleration.
- **MODEL_FILENAME**: Specifies a custom model file path, or `None` for the default.
- **MODEL_ID**: Identifier for the model version. Options include `yolo8`, `yolo11`.
- **MODEL_SKIP_FRAMES**: Enables skipping frames during processing to improve performance.
- **MODEL_SKIP_FRAMES_MASK**: Binary mask pattern for frames to skip during inference.
- **MODEL_CONFIDENCE**: Confidence threshold for detections, with 0.0 being least confident and 1.0 being most.
- **MODEL_IOU**: Intersection-over-Union threshold for non-max suppression in object detection.
- **MODEL_CATEGORIES**: Specifies which categories to detect. Options include `ALL`, `PERSON`, `BICYCLE`, `CAR`,
  `MOTORCYCLE`, `BUS`, `TRUCK`.
- **MODEL_DO_TRACKING**: Enables tracking of detected objects.

---

## [space_analysis]

- **SCENARIO_IN_ZONE**: Enables in-zone counting for specified areas.
- **SCENARIO_IN_ZONE_COORDS**: Defines coordinates for a custom in-zone area.
- **SCENARIO_IN_ZONE_COLD_DOWN_TIME_S**: Cooldown time in seconds for in-zone alerts.
- **SCENARIO_IN_ZONE_TIME_LIMIT_S**: Maximum allowed time in seconds for objects in a specified zone before alerting.
- **SCENARIO_IN_ZONE_DANGER_LIMIT**: Threshold count for triggering danger alert in a zone.
- **SCENARIO_IN_ZONE_CATEGORIES**: Object categories applicable for in-zone analysis.
- **SCENARIO_PARKING**: Enables parking analysis for free or occupied parking spaces.
- **SCENARIO_PARKING_COORDS**: Defines coordinates for parking analysis areas.
- **SCENARIO_PARKING_COLD_DOWN_TIME_S**: Cooldown time for parking alerts.
- **SCENARIO_PARKING_TIME_LIMIT_S**: Maximum allowed time for vehicles in a parking area before alerting.
- **SCENARIO_PARKING_DANGER_LIMIT**: Threshold for triggering alerts for overcrowded parking areas.
- **SCENARIO_PARKING_CATEGORIES**: Object categories for parking analysis.
- **SCENARIO_RAISED_HAND**: Enables detection of raised hands (for person category only).
- **SCENARIO_DOOR**: Enables door analysis for entry/exit events.
- **SCENARIO_DOOR_CATEGORIES**: Specifies the categories for door analysis.
- **SCENARIO_DOOR_COORDS**: Coordinates for the door detection area.
- **SCENARIO_DOOR_ENTERING_ENABLED**: Enables detection of objects entering through the door.
- **SCENARIO_DOOR_ENTERING_LABEL**: Label for door-entering events.
- **SCENARIO_DOOR_LEAVING_ENABLED**: Enables detection of objects leaving through the door.
- **SCENARIO_DOOR_LEAVING_LABEL**: Label for door-leaving events.

---

## [alert]

- **ALERT_IN_ZONE_ICON**: Path to an image icon shown during in-zone alerts.

---

## [notification]

- **NOTIFICATION_AZURE_CONNECTION_STRING**: Connection string for Azure IoT notifications, sourced from environment
  variables or file.
- **NOTIFICATION_DEVICE_ID**: Device ID used in notifications, sourced from environment variables or file.
- **NOTIFICATION_ENABLED**: Enables notifications for events.
- **NOTIFICATION_CAMERA_ID**: Camera ID for identification in notifications.
- **NOTIFICATION_DATA_AGGREGATION_TIME_MS**: Time in milliseconds to aggregate data for notifications.

---

## [benchmark]

- **BENCHMARK_DURATION_TIME_MS**: Total duration for running benchmarks in milliseconds.
- **BENCHMARK_WARMUP_TIMS_MS**: Warmup time before collecting benchmark data.
- **BENCHMARK_RESULTS_FILE_NAME**: File path for saving benchmark results.
- **BENCHMARK_DATA_AGGREGATION_TIME_MS**: Time interval for aggregating benchmark data.

---

## [logging]

- **PIL**: Logging level for PIL (Python Imaging Library).
- **azure.iot**: Logging level for Azure IoT.
- **paho**: Logging level for Paho MQTT.
- **urllib3**: Logging level for urllib3 (used in network requests).
- **pongo.config**: Logging level for application configuration logs.
- **pongo.input**: Logging level for input processing.
- **pongo.notify**: Logging level for notification handling.
- **pongo.output**: Logging level for output processes.
- **pongo.output.hls**: Logging level for HLS output processing.
- **pongo.processor**: Logging level for processing tasks.
- **pongo.webserver**: Logging level for the web server.

---

Each section provides flexibility in configuring different aspects of the application, from source and output settings
to model parameters, space analysis, notifications, and benchmarking.

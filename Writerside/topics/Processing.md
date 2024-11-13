# Processing

## Description
The `UltralyticsProcessor` class is designed to process video streams using the Ultralytics YOLO model. It handles both network streams and local video files, providing a unified interface for object detection and analysis.

## Functionality

### Initialization
The class initializes by loading the YOLO model based on the provided settings. It configures various parameters such as model dimensions, tracking options, and scenario-specific settings (e.g., pose detection, zone monitoring, door monitoring, and parking monitoring).

### Video Source Setup
When a video source is provided, the class sets up the video parameters, including the source dimensions and frame rate. It adjusts the model's input size to be compatible with the source video and initializes various decorators for drawing information on the frames.

### Frame Analysis
The core functionality of the class revolves around analyzing each frame of the video stream. For each frame, the following steps are performed:

1. **Frame Resizing**: The source frame is resized to match the model's input dimensions.
2. **Object Detection**: The YOLO model processes the resized frame to detect objects. If tracking is enabled, it also tracks the detected objects across frames.
3. **Object Extraction**: The detected objects are extracted, including their bounding boxes, labels, and confidence scores. If pose detection is enabled, keypoints are also extracted.
4. **Object Counting**: The class counts the detected objects and measures various metrics such as the number of people, bikes, and cars.
5. **Scenario Processing**: Depending on the enabled scenarios, the class processes specific conditions:
    - **Zone Monitoring**: Detects objects within a predefined zone and measures their time spent in the zone.
    - **Parking Monitoring**: Detects parked objects and measures their time spent in the parking area.
    - **Door Monitoring**: Detects people entering or leaving through a door.
    - **Raise Hand Detection**: Detects people raising their hands.
6. **Drawing Operations**: The class draws various information on the frame, including detected objects, scenario-specific indicators, and performance metrics.

### Reconnection Logic
For network streams, the class implements reconnection logic to handle interruptions. If the stream becomes unavailable, it attempts to reconnect multiple times with a delay between attempts.

### Handling Local Video Files
For local video files, the class reads frames sequentially. If the end of the file is reached or an error occurs, it attempts to restart from the beginning of the file.

## Example Usage

```python
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.input.stream_source.ultralytics_processor import UltralyticsProcessor
from fvgvisionai.common.video_observable import VideoObservable

app_settings = AppSettings(...)
video_observable = VideoObservable()
ultralytics_processor = UltralyticsProcessor("input_file.mp4", video_observable, app_settings)

exit_signal = threading.Event()
ultralytics_processor.process_source(exit_signal)
```

## Notes
- Ensure the input file path or stream URL is correct and accessible.
- Properly configure the `AppSettings` class with necessary settings before initializing `UltralyticsProcessor`.
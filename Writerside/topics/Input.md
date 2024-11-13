# Input module

## Description
The `Cv2StreamReader` class is an input module designed to read video streams using OpenCV. It handles both network streams and local video files, providing a unified interface for video input.

## Functionality

### Initialization
The class is initialized with:
- `input_file`: Path to the video file or network stream URL.
- `video_observable`: An instance of `VideoObservable` to notify about video frames and parameters.
- `app_settings`: An instance of `AppSettings` containing configuration settings.

### Reading the Video Source
The `read_source` method is responsible for reading frames from the video source. It performs the following steps:
1. **Open the Video Source**: Attempts to open the video source using OpenCV's `cv2.VideoCapture`.
2. **Extract Video Information**: Retrieves video properties such as width, height, FPS, and codec.
3. **Notify Video Parameters**: Notifies the `video_observable` with the video parameters.
4. **Read Frames in a Loop**: Continuously reads frames from the video source until an exit signal is received or an error occurs.
5. **Handle Frame Reading**: If a frame is successfully read, it is resized and notified to the `video_observable`. If reading fails, it attempts to reconnect to the video source.
6. **Reconnection Logic**: If the video source becomes unavailable, it tries to reconnect multiple times with a delay between attempts. If reconnection fails, it sets the exit signal to stop the reading process.

## Handling Network Streams
For network streams, the class:
- Opens the stream URL using `cv2.VideoCapture`.
- Implements reconnection logic to handle interruptions. If the stream becomes unavailable, it attempts to reconnect multiple times with a delay between attempts.
- Notifies the `video_observable` with a "no connection" image if reconnection attempts fail.

## Handling Local Video Files
For local video files, the class:
- Opens the file path using `cv2.VideoCapture`.
- Reads frames sequentially from the file.
- If the end of the file is reached or an error occurs, it attempts to restart from the beginning of the file.
- Notifies the `video_observable` with the read frames.

## Example Usage

```python
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.input.stream_source.cv2_stream_reader import Cv2StreamReader
from fvgvisionai.common.video_observable import VideoObservable

app_settings = AppSettings(...)
video_observable = VideoObservable()
cv2_stream_reader = Cv2StreamReader("input_file.mp4", video_observable, app_settings)

exit_signal = threading.Event()
cv2_stream_reader.read_source(exit_signal)
```

## Notes
- Ensure the input file path or stream URL is correct and accessible.
- Properly configure the `AppSettings` class with necessary settings before initializing `Cv2StreamReader`.
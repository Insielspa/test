# HLS streamer

## Description
The `HLS Streamer` module is designed to stream video frames to an HLS (HTTP Live Streaming) server using FFmpeg. It handles both network streams and local video files, providing a unified interface for video output.

## Functionality

### Initialization
The module initializes by setting up the necessary components:
- **TripleBuffer**: A buffer to hold video frames.
- **VideoObservable**: An observable to notify about video frames.
- **AppSettings**: Configuration settings for the application.

### Video Streaming Setup
When the HLS streamer is started, it sets up the video parameters, including the source dimensions and frame rate. It initializes the FFmpeg process with the appropriate command to handle the video streaming.

### Frame Streaming
The core functionality of the module revolves around streaming each frame of the video. For each frame, the following steps are performed:

1. **Frame Retrieval**: The frame is retrieved from the `TripleBuffer`.
2. **Frame Sending**: The frame is sent to the FFmpeg process through a pipe.
3. **Error Handling**: If an error occurs (e.g., broken pipe), the module attempts to reconnect and restart the FFmpeg process.

### Reconnection Logic
For network streams, the module implements reconnection logic to handle interruptions. If the stream becomes unavailable, it attempts to reconnect multiple times with a delay between attempts.

### Handling Local Video Files
For local video files, the module reads frames sequentially. If the end of the file is reached or an error occurs, it attempts to restart from the beginning of the file.

## Example Usage

```python
import threading
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.common.video_observable import VideoObservable
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.output.hls.ffmpeg_output_streamer import FFMpegOutputStreamer

# Function to run the HLS streamer in a separate thread
def run_hls_streamer_thread(video_observable: VideoObservable, buffer: TripleBuffer, app_settings: AppSettings,
                            exit_event: threading.Event) -> threading.Thread:
    frame_builder = FFMpegOutputStreamer(buffer, app_settings)
    video_observable.add_video_observer(frame_builder)

    hls_streamer_thread = threading.Thread(target=frame_builder.build_frame,
                                           args=(exit_event,),
                                           name='OutputThread')
    hls_streamer_thread.daemon = True
    hls_streamer_thread.start()

    return hls_streamer_thread
```

## Notes
- Ensure the input file path or stream URL is correct and accessible.
- Properly configure the `AppSettings` class with necessary settings before initializing the HLS streamer.
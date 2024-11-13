# Image sequence

## Description

The `WebServer` class is designed to provide a sequence of video frames as a stream of JPEG or WebP images through a
specific URL. It uses Flask to handle HTTP requests and serves the video frames in a multipart response format.

## Functionality

### Initialization

The class initializes with:

- **TripleBuffer**: A buffer to hold video frames.
- **AppSettings**: Configuration settings for the application, including video output parameters such as image type,
  quality, and frame rate.

### Frame Preparation

The class prepares frames for web streaming by:

1. **Frame Retrieval**: Retrieving the next frame from the `TripleBuffer`.
2. **Frame Encoding**: Encoding the frame as JPEG or WebP based on the configured settings.
3. **Frame Caching**: Caching the encoded frame to optimize repeated access.

### Frame Streaming

The core functionality of the class revolves around streaming frames to clients. For each frame, the following steps are
performed:

1. **Frame Retrieval**: The next frame is retrieved from the buffer.
2. **Frame Encoding**: The frame is encoded to the specified image format (JPEG or WebP).
3. **Frame Caching**: The encoded frame is cached to avoid redundant processing.
4. **Frame Sending**: The cached frame is sent to the client as part of a multipart HTTP response.

### Handling HTTP Requests

The class uses Flask to handle HTTP requests:

- **/video**: Streams the video frames to authenticated clients.
- **/**: Provides a simple status message indicating the service is up.

### Example Usage

```python
import threading
from fvgvisionai.common.triple_buffer import TripleBuffer
from fvgvisionai.config.app_settings import AppSettings
from fvgvisionai.webserver.web_server import WebServer

app_settings = AppSettings(...)
buffer = TripleBuffer()
exit_event = threading.Event()

web_server = WebServer(buffer, app_settings)
web_server_thread = threading.Thread(target=web_server.build_web_frame, args=(exit_event,))
web_server_thread.start()

# Flask app setup and run
from flask import Flask
app = Flask(__name__)

@app.route('/video')
def video():
    return web_server.video()

@app.route('/')
def index():
    return 'Service is up!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app_settings.video_output_image_port)
```

## Notes

- Ensure the input buffer is correctly populated with video frames.
- Properly configure the `AppSettings` class with necessary settings before initializing the `WebServer`.
# Output module

## Overview

The `WebServer` and `HLS Streamer` classes are integral components of the `fvg-vision-ai` application. The `WebServer`
serves video frames as a sequence of images via HTTP, while the `HLS Streamer` uses FFmpeg to stream video frames to an
HLS server.

## WebServer

The `WebServer` class is designed to provide a sequence of video frames as a stream of JPEG or WebP images through a
specific URL. It uses Flask to handle HTTP requests and serves the video frames in a multipart response format.

### Key Features {id="key-features_1"}

- **Frame Retrieval and Encoding**: Retrieves frames from a `TripleBuffer`, encodes them as JPEG or WebP, and caches the
  encoded frames.
- **HTTP Streaming**: Streams the encoded frames to clients via a Flask endpoint.
- **Reconnection Logic**: Handles reconnection attempts for network streams.
- **Frame Rate Control**: Manages the frame rate to ensure smooth streaming.

### How It Works {id="how-it-works_1"}

1. **Initialization**: The `WebServer` is initialized with a `TripleBuffer` and `AppSettings`.
2. **Frame Preparation**: Frames are retrieved from the buffer, encoded, and cached.
3. **HTTP Request Handling**: The Flask app handles HTTP requests, streaming the cached frames to clients.

## HLS Streamer

The `HLS Streamer` module is designed to stream video frames to an HLS (HTTP Live Streaming) server using FFmpeg. It
handles both network streams and local video files, providing a unified interface for video output.

### Key Features

- **Frame Retrieval**: Retrieves frames from a `TripleBuffer`.
- **FFmpeg Integration**: Uses FFmpeg to stream frames to an HLS server.
- **Reconnection Logic**: Handles reconnection attempts for network streams.
- **Error Handling**: Manages errors and attempts to restart the FFmpeg process if necessary.

### How It Works

1. **Initialization**: The HLS streamer is initialized with a `TripleBuffer` and `AppSettings`.
2. **Frame Streaming**: Frames are retrieved from the buffer and sent to the FFmpeg process through a pipe.
3. **Reconnection Logic**: Handles interruptions and attempts to reconnect to the HLS server.

## Conclusion

Both the `WebServer` and `HLS Streamer` classes play crucial roles in the `fvg-vision-ai` application, providing
different methods to stream video content to clients. The `WebServer` serves video frames as images via HTTP, while the
`HLS Streamer` uses FFmpeg to stream video to an HLS server, ensuring flexible and robust video output capabilities.
# Overview of FVG Vision AI

**FVG Vision AI** is a modular computer vision application designed for real-time video analysis, capable of running on
both
high-performance PCs with NVIDIA GPUs and Jetson ORIN AGX devices. The system is built using Python and heavily relies
on frameworks such as OpenCV for image processing and Ultralytics for object detection and tracking.

The application is containerized using Docker, enabling seamless deployment across various environments. FVG Vision AI
is designed with flexibility in mind, allowing users to customize configurations via a combination of default files,
environment variables, and command-line arguments. This ensures adaptability to various use cases and hardware setups.

The core functionality of FVG Vision AI includes the ability to process video streams from local sources or RTSP feeds.
The system supports two main output formats: HTTP Live Streaming (HLS) via FFmpeg for continuous video streaming, or
JPEG snapshots served via HTTP. Additionally, the application features a built-in Nginx server to handle the
distribution of these outputs.

FVG Vision AI is built around four primary modules:

- Input: Captures and processes video streams.
- Processing: Uses Ultralytics to perform object detection and scenario-specific analytics.
- Notification: Sends event-based notifications to Azure IoT Hub.
- Output: Provides video streams or images via HTTP in HLS or JPEG format.

The application includes pre-configured scenarios for specific use cases such as:

- Counting people in a designated area.
- Monitoring the availability of parking spots.
- Detecting raised hands.
- Tracking how many people cross a specific line in the video feed.

A benchmark mode is available for performance testing, allowing users to measure FPS and system load in different
operational scenarios.

FVG Vision AI is ideal for real-time applications such as crowd management, traffic monitoring, and automated
surveillance, providing a scalable and highly configurable solution for various computer vision tasks.
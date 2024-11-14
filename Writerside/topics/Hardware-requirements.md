# Hardware Requirements

Minimum Hardware Requirements
FVG Vision AI is optimized to run on specific hardware configurations, especially for applications requiring real-time
computer vision processing. Below are the minimum hardware requirements to ensure compatibility and satisfactory
performance:

- **Device Options**:
    - **NVIDIA Jetson AGX Orin**: The primary development platform for FVG Vision AI. The software is optimized to run
      on the
      Jetson AGX Orin series, providing robust real-time object detection and tracking capabilities.
    - **PC with NVIDIA Discrete GPU**: The software can also operate on standard PCs with NVIDIA GPUs that support CUDA.
      This
      setup allows for high-performance processing suitable for demanding tasks.
    - **PC without NVIDIA GPU**: While the software supports execution on systems without an NVIDIA GPU by using PyTorch
      models
      from Ultralytics, this setup is expected to reduce performance significantly due to the lack of CUDA support.

- Storage: 20 GB of free disk space to accommodate the containerized environment and associated models.

- **Memory (RAM)**: At least 8 GB of RAM. This is the standard configuration for the Jetson Orin platform, and it is the
  recommended minimum for efficient operation on PCs as well.

## NVIDIA Jetson Platform

For an optimized experience, **NVIDIA Jetson AGX Orin** has been chosen as the core platform for FVG Vision AI
development.
The platform is part of NVIDIA's family of AI-accelerated embedded devices, specifically designed for edge computing
with high-performance neural network processing and low power consumption.

- **Supported JetPack Version: JetPack 6** (link to NVIDIA Jetson AGX Orin and JetPack 6). This version includes CUDA,
  cuDNN,
  and TensorRT support, essential for deploying and running deep learning models efficiently.

- **Backward Compatibility**: While JetPack versions older than 6 may still be functional, support and development for
  these
  older versions have been phased out due to time constraints. Users on previous versions may experience reduced
  functionality and are encouraged to update.

## NVIDIA Discrete GPUs on PC

FVG Vision AI also supports operation on PCs equipped with NVIDIA discrete GPUs compatible with CUDA 12.6. Leveraging
CUDA allows for accelerated inference, and maintaining the CUDA version ensures compatibility and optimized
performance.

- **CUDA Version Requirement**: Version 12.6 is the tested and supported version. Switching to a different CUDA version
  may
  require re-compilation of TensorRT models used by the neural network, which can impact compatibility and performance.

## CPU-Only PC Configuration

For environments lacking an NVIDIA GPU, FVG Vision AI can run using PyTorch models from Ultralytics. In this
configuration, inference performance will be significantly slower, as CPU-only processing lacks the hardware
acceleration provided by CUDA-capable GPUs.

## Additional Considerations

When configuring hardware for FVG Vision AI, ensure that your system meets the minimum requirements, especially if high
performance and real-time processing are essential.
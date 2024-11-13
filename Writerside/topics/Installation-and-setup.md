# Installation and setup

## Using Docker (Recommended)

While it is possible to install all dependencies directly on your machine, it is strongly recommended to use the Docker
version of FVG Vision AI. Docker provides a controlled environment and simplifies dependency management and
installation.

Scripts for each supported platform are already included with the application and can be found in the following
directories:

- **docker/amd64**: for 64-bit x86 machines without a GPU.
- **docker/amd64-cuda**: for 64-bit x86 machines with CUDA support.
- **jetson-agx-jp6**: for NVIDIA Jetson AGX devices with JetPack 6.

## Available Docker Images

Docker images for each platform are ready on Docker Hub, available in both development (dev) and production (prod)
modes. To pull the desired image, use the following tag format:

```bash
docker pull xcesco/fvgvision-ai:<version>-<platform>-<flavour>
```

#### Example Tag

For example, to pull version `0.2.0` of the `dev` image for `amd64` platforms:

```bash
docker pull xcesco/fvgvision-ai:0.2.0-amd64-dev
```

## Setup and Build Scripts

The project includes scripts to facilitate configuration and management of Docker images:

- `setup.sh`: performs the initial setup, configuring the basic dependencies.
- `build.sh`: builds and creates a local Docker image tailored to the platform configuration.
- `docker_start_dev.sh`/`docker_stop_dev.sh`: runs and stops dev container, used to develop and test app.
- `docker_start_main.sh`/`docker_stop_main.sh`: runs and stops prod container, used to run app.

Using these scripts allows for quick and reliable setup, preventing dependency conflicts and missing requirements.
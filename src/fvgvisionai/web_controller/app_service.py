import base64

import cv2

DEFAULT_IMAGE_PATH = "/app/assets/images/no_image_available800x600.jpg"
CONFIG_WEB_JSON_FILENAME = './config-web.json'
ENV_WEB_FILENAME = './.env-main-web'
RUN_MAIN_WEB = "/app/run_main_web.sh"

import subprocess

from flask import Response, abort, jsonify

from fvgvisionai.common.pid_file import read_pid_from_file, terminate_process
from fvgvisionai.web_controller.controller_service import RUN_MAIN_WEB


def app_service_start(execution_type: str) -> tuple[Response, int]:
    # Verifica che il parametro 'type' sia valido
    if execution_type not in ['file', 'env']:
        abort(400, description="Invalid 'type' parameter. Must be 'file' or 'env'.")
    command = [RUN_MAIN_WEB]
    execute_fvgvision_ai(command)
    # Avvia il processo come demone, senza bloccare il processo principale
    status = "RUNNING"
    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


def app_service_stop() -> tuple[Response, int]:
    # Trova il PID del processo
    pid = read_pid_from_file()
    if pid is not None:
        terminate_process(pid)
        status = "TERMINATED"
    else:
        status = "NOT_FOUND"
    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


def app_service_restart(execution_type: str) -> tuple[Response, int]:
    # Trova il PID del processo
    pid = read_pid_from_file()
    if pid is not None:
        terminate_process(pid)

        # Verifica che il parametro 'type' sia valido
    if execution_type not in ['file', 'env']:
        abort(400, description="Invalid 'type' parameter. Must be 'file' or 'env'.")

        # Esegui il comando in base al valore di 'type'
    command = [RUN_MAIN_WEB]
    execute_fvgvision_ai(command)
    status = "RUNNING"
    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


def execute_fvgvision_ai(command=[RUN_MAIN_WEB]):
    # Esegui il comando per avviare l'app come processo in background
    subprocess.Popen(command, stdout=None,  # Non redirige l'output, lasciandolo su stdout
                     stderr=None,  # Non redirige gli errori, lasciandoli su stderr
                     close_fds=True)  # Chiude i file descriptor non necessari)


def generate_image_preview(url: str, width: int, height: int) -> [Response, int]:
    """
    Generates a preview image from a video stream URL.

    Args:
        url (str): The URL of the video stream.
        width (int): The desired width of the preview image.
        height (int): The desired height of the preview image.

    Returns:
        Response: A JSON response containing the base64 encoded image and its dimensions.
        int: The HTTP status code.
    """
    original_height = height
    original_width = width
    try:
        # Open the video stream with OpenCV
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise Exception("Unable to open video stream")

        # Capture the first frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Unable to capture frame from video stream")

        # Get the original dimensions of the image
        original_height, original_width = frame.shape[:2]

        # Resize the image if width and height are provided
        if width and height:
            frame = cv2.resize(frame, (width, height))
        else:
            width, height = original_width, original_height

        # Convert the frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_bytes = buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Close the video stream
        cap.release()
    except Exception:
        # In case of error, load the fallback image from disk
        img_base64, width, height = _get_default_image_base64()

    # Return the base64 image along with the dimensions
    return jsonify({"image": img_base64,
                    "width": width, "height": height,
                    "original_width": original_width, "original_height": original_height}), 200

def _get_default_image_base64() -> (str, int, int):
    """
    Loads the default image from disk and returns it in base64 format along with its dimensions.

    Returns:
        str: The base64 encoded image.
        int: The width of the image.
        int: The height of the image.

    Raises:
        FileNotFoundError: If the default image is not found.
    """
    try:
        # Read the image with OpenCV
        image = cv2.imread(DEFAULT_IMAGE_PATH)
        if image is None:
            raise FileNotFoundError("Default image not found")

        # Get the dimensions of the image
        height, width = image.shape[:2]

        # Convert the image to base64
        _, buffer = cv2.imencode('.jpg', image)
        img_bytes = buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64, width, height
    except FileNotFoundError:
        abort(500, description="Default image not found")
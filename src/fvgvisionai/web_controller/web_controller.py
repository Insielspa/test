from flask import request, abort, Flask, Response
from flask_cors import CORS
from werkzeug.datastructures import FileStorage

from fvgvisionai.web_controller.app_service import app_service_start, app_service_stop, app_service_restart
from fvgvisionai.web_controller.commons import decode_base64_to_url, app_service_verify_status
from fvgvisionai.web_controller.config_service import config_service_upload, config_service_download
from fvgvisionai.web_controller.controller_service import generate_image_preview
from fvgvisionai.web_controller.model_service import model_service_upload, model_service_delete, model_service_list
from fvgvisionai.web_controller.video_service import video_service_delete, video_service_upload, video_service_list

SWAGGER_URL = '/swagger'
API_URL = 'assets/static/openapi.yaml'

app = Flask(__name__)
CORS(app)

@app.route('/app/start', methods=['GET'])
def start_app() -> [Response, int]:
    """
    Starts the application with the specified execution type.

    Returns:
        Response: A JSON response indicating the result of the start operation.
        int: The HTTP status code.
    """
    execution_type = request.args.get('type', 'env')
    return app_service_start(execution_type)

@app.route('/app/stop', methods=['GET'])
def stop_app() -> [Response, int]:
    """
    Stops the application.

    Returns:
        Response: A JSON response indicating the result of the stop operation.
        int: The HTTP status code.
    """
    return app_service_stop()

@app.route('/app/restart', methods=['GET'])
def restart_app() -> [Response, int]:
    """
    Restarts the application with the specified execution type.

    Returns:
        Response: A JSON response indicating the result of the restart operation.
        int: The HTTP status code.
    """
    execution_type = request.args.get('type', 'env')
    return app_service_restart(execution_type)

@app.route('/app/status', methods=['GET'])
def verify_status():
    """
    Verifies the status of the application.

    Returns:
        Response: A JSON response indicating the status of the application.
        int: The HTTP status code.
    """
    return app_service_verify_status()

@app.route('/preview', methods=['GET'])
def preview() -> [Response, int]:
    """
    Generates a preview image from a base64 encoded video stream URL.

    Returns:
        Response: A JSON response containing the base64 encoded image and its dimensions.
        int: The HTTP status code.
    """
    base64_url = request.args.get('url')
    if not base64_url:
        abort(400, description="URL is required")
    url = decode_base64_to_url(base64_url)
    width = request.args.get('width', type=int, default=None)
    height = request.args.get('height', type=int, default=None)

    return generate_image_preview(url, width, height)

@app.route('/app/config', methods=['POST'])
def upload_config() -> [Response, int]:
    """
    Uploads a JSON configuration file.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    if 'file' not in request.files:
        abort(400, description="File is required")

    file = request.files['file']
    if not file.filename.endswith('.json'):
        abort(400, description="File must be a JSON")

    return config_service_upload(file)

@app.route('/app/config', methods=['GET'])
def download_config() -> [Response, int]:
    """
    Downloads the current configuration file.

    Returns:
        Response: The configuration file as an attachment.
        int: The HTTP status code.
    """
    return config_service_download()

@app.route('/models/list', methods=['GET'])
def model_list_files() -> [Response, int]:
    """
    Retrieves a list of model files with specific extensions from the models directory.

    Returns:
        Response: A JSON response containing the list of model filenames.
        int: The HTTP status code.
    """
    return model_service_list()

@app.route('/models/upload', methods=['POST'])
def model_upload_file() -> [Response, int]:
    """
    Uploads a model file to the models directory.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    if 'file' not in request.files:
        abort(400, description="File is required")

    file: FileStorage = request.files['file']
    if not (file.filename.endswith('.pt') or file.filename.endswith('.engine')):
        abort(400, description="File must have a .pt or .engine extension")

    return model_service_upload(file)

@app.route('/models/delete', methods=['DELETE'])
def model_delete_file() -> [Response, int]:
    """
    Deletes a model file from the video directory.

    Returns:
        Response: A JSON response indicating the result of the deletion.
        int: The HTTP status code.
    """
    file_name = request.args.get('file_name')
    if not file_name:
        abort(400, description="File name is required")

    return model_service_delete(file_name)


@app.route('/videos/list', methods=['GET'])
def video_list_files() -> [Response, int]:
    """
    Retrieves a list of video files with specific extensions from the models directory.

    Returns:
        Response: A JSON response containing the list of model filenames.
        int: The HTTP status code.
    """
    return video_service_list()

@app.route('/videos/upload', methods=['POST'])
def video_upload_file() -> [Response, int]:
    """
    Uploads a model file to the video directory.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    if 'file' not in request.files:
        abort(400, description="File is required")

    file: FileStorage = request.files['file']
    if not (file.filename.endswith('.pt') or file.filename.endswith('.engine')):
        abort(400, description="File must have a .pt or .engine extension")

    return video_service_upload(file)

@app.route('/videos/delete', methods=['DELETE'])
def video_delete() -> [Response, int]:
    """
    Deletes a model file from the video directory.

    Returns:
        Response: A JSON response indicating the result of the deletion.
        int: The HTTP status code.
    """
    file_name = request.args.get('file_name')
    if not file_name:
        abort(400, description="File name is required")

    return video_service_delete(file_name)
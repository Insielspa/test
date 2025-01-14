import json
import os

from flask import jsonify, abort, Response, send_file
from werkzeug.datastructures import FileStorage

from fvgvisionai.config.json_converter.convert_config_json_2_env import convert_config_json_2_env
from fvgvisionai.web_controller.controller_service import CONFIG_WEB_JSON_FILENAME, ENV_WEB_FILENAME

def config_service_upload(file: FileStorage) -> [Response, int]:
    """
    Uploads a configuration file and converts it to an environment file.

    Args:
        file (FileStorage): The configuration file to upload.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    try:
        # Load the JSON data from the uploaded file
        config_data = json.load(file)

        # Write the configuration data to a JSON file
        _write_config(CONFIG_WEB_JSON_FILENAME, config_data)

        # Convert the JSON configuration to an environment file
        convert_config_json_2_env(CONFIG_WEB_JSON_FILENAME, ENV_WEB_FILENAME)

        return jsonify({"status": "ok", "description": "Configuration uploaded successfully"}), 200
    except json.JSONDecodeError:
        abort(400, description="Invalid JSON file")

def config_service_download() -> Response:
    """
    Downloads the current configuration file.

    Returns:
        Response: The configuration file as an attachment.
        int: The HTTP status code.
    """
    if not _config_exists(CONFIG_WEB_JSON_FILENAME):
        abort(404, description="Configuration file not found")

    return send_file(CONFIG_WEB_JSON_FILENAME, as_attachment=True, download_name=CONFIG_WEB_JSON_FILENAME)

def _config_exists(filename: str) -> bool:
    """
    Checks if a configuration file exists.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return os.path.isfile(filename)

def _read_config(filename: str) -> dict:
    """
    Reads a configuration file and returns its contents.

    Args:
        filename (str): The name of the file to read.

    Returns:
        dict: The contents of the configuration file.
    """
    if not _config_exists(filename):
        return {}
    with open(filename, 'r') as file:
        return json.load(file)

def _write_config(json_filename: str, data: any):
    """
    Writes data to a configuration file.

    Args:
        json_filename (str): The name of the file to write to.
        data (any): The data to write to the file.
    """
    with open(json_filename, 'w') as file:
        json.dump(data, file, indent=4)
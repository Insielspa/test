import base64
import glob
import os
from typing import List

from flask import Response, abort, jsonify
from werkzeug.datastructures import FileStorage

from fvgvisionai.common.pid_file import read_pid_from_file


def decode_base64_to_url(base64_url: str) -> str:
    """
    Decodes a Base64 encoded URL.

    Args:
        base64_url (str): The Base64 encoded URL.

    Returns:
        str: The decoded URL.
    """
    decoded_bytes = base64.b64decode(base64_url)
    return decoded_bytes.decode('utf-8')

def get_filename_list(directory: str, extensions: List[str]) -> [Response, int]:
    """
    Retrieves a list of filenames with specified extensions from a directory.

    Args:
        directory (str): The directory to search in.
        extensions (List[str]): The list of file extensions to filter by.

    Returns:
        Response: A JSON response containing the list of filenames.
        int: The HTTP status code.
    """
    if not directory or not extensions:
        abort(400, description="Both 'directory' and 'extensions' parameters are required.")
    if not os.path.isdir(directory):
        abort(400, description="Invalid directory path.")

    files = get_files_with_extensions(directory, extensions)
    return jsonify({"status": "ok", "files": files}), 200

def get_files_with_extensions(directory: str, extensions: List[str]) -> List[str]:
    """
    Helper function to get files with specific extensions from a directory.

    Args:
        directory (str): The directory to search in.
        extensions (List[str]): The list of file extensions to filter by.

    Returns:
        List[str]: A list of filenames with the specified extensions.
    """
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(directory, f'*.{ext}')))
    return [os.path.basename(file) for file in files]

def manage_delete_file(directory: str, file_name: str) -> [Response, int]:
    """
    Deletes a file from a specified directory.

    Args:
        directory (str): The directory containing the file.
        file_name (str): The name of the file to delete.

    Returns:
        Response: A JSON response indicating the result of the deletion.
        int: The HTTP status code.
    """
    file_path = os.path.join(directory, file_name)

    if not os.path.isfile(file_path):
        abort(404, description="File not found")

    os.remove(file_path)
    return jsonify({"status": "ok", "description": f"File '{file_name}' deleted successfully"}), 200

def manage_upload_file(directory: str, file: FileStorage) -> [Response, int]:
    """
    Uploads a file to a specified directory.

    Args:
        directory (str): The directory to upload the file to.
        file (FileStorage): The file to upload.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, file.filename)
    file.save(file_path)

    return jsonify({"status": "ok", "description": f"File '{file.filename}' uploaded successfully"}), 200

def app_service_verify_status() -> [Response, int]:
    """
    Verifies the status of the application by checking the PID file.

    Returns:
        Response: A JSON response indicating the status of the application.
        int: The HTTP status code.
    """
    pid = read_pid_from_file()

    if pid is not None:
        status = "RUNNING"
    else:
        status = "STOPPED"

    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200
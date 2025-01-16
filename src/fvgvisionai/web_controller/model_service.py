from flask import Response
from werkzeug.datastructures import FileStorage

from fvgvisionai.web_controller.commons import manage_upload_file, manage_delete_file, get_filename_list

ASSETS_MODELS_CUSTOM_PATH = './assets/models/custom'

def model_service_list() -> [Response, int]:
    """
    Retrieves a list of model files with specific extensions from the models directory.

    Returns:
        Response: A JSON response containing the list of model filenames.
        int: The HTTP status code.
    """
    extensions = ['pt', 'engine']

    return get_filename_list(ASSETS_MODELS_CUSTOM_PATH, extensions)

def model_service_upload(file: FileStorage) -> [Response, int]:
    """
    Uploads a model file to the models directory.

    Args:
        file (FileStorage): The model file to upload.

    Returns:
        Response: A JSON response indicating the result of the upload.
        int: The HTTP status code.
    """
    return manage_upload_file(ASSETS_MODELS_CUSTOM_PATH, file)

def model_service_delete(file_name: str) -> [Response, int]:
    """
    Deletes a model file from the models directory.

    Args:
        file_name (str): The name of the model file to delete.

    Returns:
        Response: A JSON response indicating the result of the deletion.
        int: The HTTP status code.
    """
    return manage_delete_file(ASSETS_MODELS_CUSTOM_PATH, file_name)
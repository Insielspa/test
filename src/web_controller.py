import base64
import os
import subprocess

import cv2
from PIL.Image import Image
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from fvgvisionai.common.pid_file import read_pid_from_file, terminate_process

RUN_MAIN_ENV_SH = "/app/run_main_env.sh"

RUN_MAIN_SH = "/app/run_main.sh"

DEFAULT_IMAGE_PATH="/app/assets/images/no_image_available800x600.jpg"

app = Flask(__name__)
CORS(app)

@app.route('/start', methods=['GET'])
def start_app():
    # Ottieni il parametro 'type' dalla richiesta
    execution_type = request.args.get('type', 'env')

    # Verifica che il parametro 'type' sia valido
    if execution_type not in ['file', 'env']:
        abort(400, description="Invalid 'type' parameter. Must be 'file' or 'env'.")

    # Esegui il comando in base al valore di 'type'
    if execution_type == 'file':
        command = [RUN_MAIN_SH]
    elif execution_type == 'env':
        command = [RUN_MAIN_ENV_SH]

    execute_fvgvision_ai(command)

    # Avvia il processo come demone, senza bloccare il processo principale
    status = "RUNNING"
    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


def execute_fvgvision_ai(command=[RUN_MAIN_ENV_SH]):
    # Esegui il comando per avviare l'app come processo in background
    subprocess.Popen(command, stdout=None,  # Non redirige l'output, lasciandolo su stdout
                     stderr=None,  # Non redirige gli errori, lasciandoli su stderr
                     close_fds=True)  # Chiude i file descriptor non necessari)


@app.route('/stop', methods=['GET'])
def stop_app():
    # Trova il PID del processo
    pid = read_pid_from_file()

    if pid is not None:
        terminate_process(pid)
        status = "TERMINATED"
    else:
        status = "NOT_FOUND"

    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


@app.route('/status', methods=['GET'])
def verify_status():
    # Trova il PID del processo
    pid = read_pid_from_file()

    if pid is not None:
        status = "RUNNING"
    else:
        status = "STOPPED"

    return jsonify({"status": "ok", "result": status, "description": f"App is {status}"}), 200


@app.route('/preview', methods=['GET'])
def preview():
    base64_url = request.args.get('url')
    if not base64_url:
        abort(400, description="URL is required")
    url = decode_base64_to_url(base64_url)

    print(url)

    width = request.args.get('width', type=int, default=None)
    height = request.args.get('height', type=int, default=None)

    try:
        # Apri il flusso video con OpenCV
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            raise Exception("Unable to open video stream")

        # Cattura il primo frame
        ret, frame = cap.read()
        if not ret:
            raise Exception("Unable to capture frame from video stream")

        # Ottieni le dimensioni originali dell'immagine
        original_height, original_width = frame.shape[:2]

        # Ridimensiona l'immagine se altezza e larghezza sono forniti
        if width and height:
            frame = cv2.resize(frame, (width, height))
        else:
            width, height = original_width, original_height

        # Converti il frame in base64
        _, buffer = cv2.imencode('.jpg', frame)
        img_bytes = buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Chiudi il video stream
        cap.release()
    except Exception as e:
        # In caso di errore, carica l'immagine di fallback da disco
        img_base64, width, height = get_default_image_base64()

    # Restituisci l'immagine in base64 insieme alle dimensioni
    return jsonify({"image": img_base64, "width": width, "height": height}), 200

# Funzione per decodificare una stringa Base64
def decode_base64_to_url(base64_url: str) -> str:
    # Decodifica la stringa Base64
    decoded_bytes = base64.b64decode(base64_url)
    return decoded_bytes.decode('utf-8')


def get_default_image_base64():
    """
    Funzione per caricare l'immagine di default da disco e restituirla in formato base64 insieme alle dimensioni.
    """
    try:
        # Leggi l'immagine con OpenCV
        image = cv2.imread(DEFAULT_IMAGE_PATH)
        if image is None:
            raise FileNotFoundError("Default image not found")

        # Ottieni le dimensioni dell'immagine
        height, width = image.shape[:2]

        # Converti l'immagine in base64
        _, buffer = cv2.imencode('.jpg', image)
        img_bytes = buffer.tobytes()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return img_base64, width, height
    except FileNotFoundError:
        abort(500, description="Default image not found")


if __name__ == "__main__":
    execute_fvgvision_ai()
    app.run(host='0.0.0.0', port=8081)

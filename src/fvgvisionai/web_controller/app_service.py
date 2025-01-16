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

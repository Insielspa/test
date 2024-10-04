import os
import subprocess

from flask import Flask, request, abort

from fvgvisionai.common.pid_file import read_pid_from_file, terminate_process

RUN_MAIN_ENV_SH = "/app/run_main_env.sh"

RUN_MAIN_SH = "/app/run_main.sh"

app = Flask(__name__)


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

    return "App avviata con successo"


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
        return "App terminata con successo"
    else:
        return "Nessuna istanza in esecuzione"


@app.route('/status', methods=['GET'])
def verify_status():
    # Trova il PID del processo
    pid = read_pid_from_file()

    if pid is not None:
        return "RUNNING"
    else:
        return "STOPPED"


if __name__ == "__main__":
    execute_fvgvision_ai()
    app.run(host='0.0.0.0', port=8081)

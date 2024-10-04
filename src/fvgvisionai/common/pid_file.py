# Path del file che conterrà il PID
import os
import signal
import time
from typing import Optional

pid_file = "fvg_vision_ai.lock"


def read_pid_from_file() -> Optional[int]:
    """
    Legge il PID dal file specificato e lo restituisce.
    Restituisce None se il file non esiste o il contenuto non è valido.
    """
    if not os.path.exists(pid_file):
        print(f"PID file {pid_file} does not exist.")
        return None

    try:
        with open(pid_file, 'r') as f:
            return int(f.read().strip())
    except (ValueError, OSError) as e:
        print(f"Error reading PID file: {e}")
        return None


def terminate_process(pid: int) -> None:
    """
    Tenta di terminare il processo con il PID specificato.
    """
    try:
        # Controlla se il processo con quel PID esiste
        if os.path.exists(f"/proc/{pid}"):
            os.kill(pid, signal.SIGTERM)
            time.sleep(3)
            print(f"Process with PID {pid} has been terminated.")
        else:
            print(f"Process with PID {pid} is not running.")
    except ProcessLookupError:
        print(f"Process with PID {pid} does not exist.")
    except PermissionError:
        print(f"Permission denied to terminate process with PID {pid}.")


def write_pid_file():
    pid = os.getpid()  # Ottieni il PID del processo corrente
    with open(pid_file, 'w') as f:
        f.write(str(pid))  # Scrivi il PID su file

def remove_pid_file():
    if os.path.exists(pid_file):
        os.remove(pid_file)  # Rimuovi il file se esiste


def is_another_instance_running(app_name: str):
    if os.path.exists(pid_file):
        # Se il file esiste, leggere il PID
        with open(pid_file, 'r') as f:
            try:
                pid = int(f.read().strip())
            except ValueError:
                pid = None

        # Controllare se il processo associato al PID è ancora attivo
        if pid and os.path.exists(f"/proc/{pid}"):
            print(f"Another instance of {app_name} is already running with PID {pid}.")
            return True
        else:
            # Il processo non esiste più, rimuovi il file PID obsoleto
            os.remove(pid_file)
            return False
    return False

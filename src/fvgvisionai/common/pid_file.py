# Path del file che conterrà il PID
import os

pid_file = "fvg_vision_ai.pid"

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

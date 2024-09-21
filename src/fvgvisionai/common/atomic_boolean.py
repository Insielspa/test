import threading


class AtomicBoolean:
    def __init__(self, initial_value=False):
        self._value = initial_value
        self._lock = threading.Lock()

    def set(self, value):
        with self._lock:
            self._value = value

    def get(self):
        with self._lock:
            return self._value

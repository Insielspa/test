import time


class AppTimer:
    """Una classe per misurare il tempo trascorso tra due punti nel codice."""

    def __init__(self):
        """Inizializza un nuovo timer."""
        self.start_time = None

    def start(self):
        """Avvia il timer registrando il tempo di inizio."""
        self.start_time = time.time_ns()

    def stop(self) -> float:
        """Ferma il timer e restituisce il tempo trascorso in millisecondi.

        Returns:
            float: Il tempo trascorso in millisecondi.

        Raises:
            ValueError: Se il timer non è stato avviato prima di chiamare stop().
        """
        elapsed_milliseconds = self.elapsed_time
        self.start_time = None
        return elapsed_milliseconds

    @property
    def is_running(self) -> bool:
        return self.start_time is not None

    @property
    def elapsed_time(self) -> float:
        """Restituisce il tempo trascorso in millisecondi senza fermare il timer.

                Returns:
                    float: Il tempo trascorso in millisecondi.

                Raises:
                    ValueError: Se il timer non è stato avviato prima di chiamare stop().
                """
        if not self.is_running:
            return 0
        end_time = time.time_ns()
        elapsed_time = end_time - self.start_time

        # Calcola il tempo trascorso in millisecondi
        return round(elapsed_time / 1_000_000.0, 2)

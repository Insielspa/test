class MovingAverageCalculator:
    def __init__(self, size=10):
        self.values = []  # Lista per memorizzare gli ultimi 10 valori
        self.max_size = size

    def add_value(self, value):
        self.values.append(value)
        if len(self.values) > self.max_size:
            self.values.pop(0)  # Rimuovi il valore più vecchio se la lista ha più di 10 elementi

    def calculate_average(self):
        if not self.values:
            return 0  # Restituisci 0 se la lista è vuota
        return sum(self.values) / len(self.values)

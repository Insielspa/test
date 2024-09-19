from typing import List


class IntMeasure:
    def __init__(self):
        self._data: List[int] = []

    def add(self, value: int):
        self._data.append(value)

    def clear(self, ):
        self._data = []

    @property
    def average(self) -> int:
        if not self._data:
            return 0
        return round(sum(self._data) / len(self._data))

    @property
    def max(self) -> int:
        if not self._data:
            return 0
        return max(self._data)

    @property
    def min(self) -> int:
        if not self._data:
            return 0
        return min(self._data)

    @property
    def sum(self) -> int:
        return sum(self._data)

    @property
    def length(self) -> int:
        return len(self._data)

    @property
    def last_value(self) -> int:
        if not self._data:
            return 0
        return self._data[-1]

    def copy(self):
        copied_instance = IntMeasure()
        copied_instance._data = self._data.copy()  # Copia la lista _data

        return copied_instance


class FloatMeasure:
    def __init__(self):
        self._data: List[float] = []

    def add(self, value: float):
        self._data.append(value)

    def clear(self):
        self._data = []

    @property
    def average(self) -> float:
        if not self._data:
            return 0
        return round(sum(self._data) / len(self._data), 2)

    @property
    def max(self) -> float:
        if not self._data:
            return 0
        return max(self._data)

    @property
    def min(self) -> float:
        if not self._data:
            return 0
        return min(self._data)

    @property
    def sum(self) -> float:
        return sum(self._data)

    @property
    def length(self) -> int:
        return len(self._data)

    @property
    def last_value(self) -> float:
        if not self._data:
            return 0
        return self._data[-1]

    def copy(self):
        copied_instance = FloatMeasure()
        copied_instance._data = self._data.copy()  # Copia la lista _data

        return copied_instance

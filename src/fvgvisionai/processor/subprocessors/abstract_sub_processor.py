from abc import ABC


class AbstractSubProcessor(ABC):
    def __init__(self, enabled: bool):
        self._enabled = enabled

    @property
    def is_enabled(self):
        return self._enabled

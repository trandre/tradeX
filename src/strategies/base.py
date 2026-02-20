from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def generate_signal(self, data):
        """Returns 1 for buy, -1 for sell, 0 for hold."""
        pass

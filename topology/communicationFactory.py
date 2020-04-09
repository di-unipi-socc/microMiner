from abc import ABC, abstractmethod
from .communication import Communication

class CommunicationFactory(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def build(self, packet: dict) -> Communication:
        pass 

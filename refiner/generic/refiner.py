from abc import ABC, abstractmethod

class Refiner(ABC):

    def __init__(self):
        pass
    
    @classmethod
    @abstractmethod
    def recognize(cls, nodes: dict, args: dict):
        pass

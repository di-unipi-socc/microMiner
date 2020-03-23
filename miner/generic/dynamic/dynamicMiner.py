from abc import ABC, abstractmethod

class DynamicMiner(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        pass

from abc import ABC, abstractmethod

class StaticMiner(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        pass

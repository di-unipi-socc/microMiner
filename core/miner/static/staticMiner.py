from abc import ABC, abstractmethod

class StaticMiner(ABC):

    def __init__(self):
        pass

    @abstractmethod
    @staticmethod
    def updateTopology(info: dict, nodes: dict):
        pass

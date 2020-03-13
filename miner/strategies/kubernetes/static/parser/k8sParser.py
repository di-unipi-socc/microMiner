from abc import ABC, abstractmethod

class K8sParser(ABC):

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def parse(contentDict: dict, contentStr: str) -> dict:
        pass

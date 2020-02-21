from abc import ABC, abstractmethod

class K8sParser(ABC):

    def __init__(self):
        pass

    @abstractmethod
    @staticmethod
    def parse(content: dict) -> dict:
        pass

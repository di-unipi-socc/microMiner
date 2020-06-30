from abc import ABC, abstractmethod

class DynamicMiner(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        '''
        Crea/aggiorna la topologia attuale

        :param source: files dell'applicazione
        :param info: dizionario opaco che contiene gli argomenti, varia a seconda della strategia
        :param nodes: topologia attuale, può essere vuota
        '''
        pass

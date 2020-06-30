from abc import ABC, abstractmethod

class K8sParser(ABC):

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def parse(contentDict: dict, contentStr: str) -> dict:
        '''
        Effettua il parsing del file YAML/JSON

        :param contentDict: contenuto del file come dizionario
        :param contentStr: contenuto del file come stringa

        :return un dizionario opaco con le informazioni estratte
        '''
        pass

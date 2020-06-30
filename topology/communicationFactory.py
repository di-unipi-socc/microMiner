from abc import ABC, abstractmethod
from .communication import Communication

class CommunicationFactory(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def build(self, packet: dict) -> Communication:
        '''
        Costruisce un istanza di Communication

        :param packet: dizionario che contiene il pacchetto della rete
        :return un'istanza di Communication
        '''
        pass 

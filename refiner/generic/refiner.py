from abc import ABC, abstractmethod

class Refiner(ABC):

    def __init__(self):
        pass
    
    @classmethod
    @abstractmethod
    def recognize(cls, nodes: dict, args: dict):
        '''
        Riconosce un determinato design pattern

        :param nodes: la topologia
        :param args: dizionario opaco con i parametri della strategia concreta
        '''
        pass

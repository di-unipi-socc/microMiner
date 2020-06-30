from abc import ABC, abstractmethod
from topology.node import Node
from topology.microToscaTypes import NodeType, RelationshipProperty
from typing import List, Optional
 
class Exporter(ABC):
    
    @classmethod
    @abstractmethod
    def export(cls, topology: dict, path: str, modelName: Optional[str] = 'Generic application'):
        '''
        Esporta la topologia rappresentata in microTOSCA in un file

        :param topology: dizionario  che associa al nome del nodo, il nodo
        :param path: path dove salvare il microTOSCA
        :param modelName: Descrizione o nome dell'applicazione, di default Generic application
        '''
        pass

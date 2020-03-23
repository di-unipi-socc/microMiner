from abc import ABC, abstractmethod
from topology.node import Node
from topology.microToscaTypes import NodeType, RelationshipProperty
from typing import List
 
class Exporter(ABC):
    
    @classmethod
    @abstractmethod
    def Export(cls, topology: List[Node], modelName: str, path: str):
        pass

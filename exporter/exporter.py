from abc import ABC, abstractmethod
from topology.node import Node
from topology.microToscaTypes import NodeType, RelationshipProperty
from typing import List, Optional
 
class Exporter(ABC):
    
    @classmethod
    @abstractmethod
    def export(cls, topology: dict, path: str, modelName: Optional[str] = 'Generic application'):
        pass

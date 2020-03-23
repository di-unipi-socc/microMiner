from enum import Enum
from typing import Optional
from typing import List
from .microToscaTypes import NodeType, RelationshipProperty
from .communication import Communication

class Direction(Enum):
    INCOMING = 0
    OUTGOING = 1

class Node:

    def __init__(self, spec):
        self.spec = spec
        self.type = NodeType.MICROTOSCA_NODES_SERVICE
        self.isEdge = False
        self.incomingEdges = {}
        self.outgoingEdges = {}
        
    def getSpec(self) -> dict:
        return self.spec

    def getType(self) -> NodeType:
        return self.type

    def setType(self, nodeType: NodeType):
        if nodeType is None:
            raise TypeError
        self.type = nodeType
    
    def getIsEdge(self) -> bool:
        return self.isEdge
    
    def setIsEdge(self, isEdge: bool):
        self.isEdge = isEdge

    def addEdge(self, nodeName: str, direction: Direction, communications: Optional[List[Communication]] = [], relationshipProperties: Optional[List[RelationshipProperty]] = []):
        if not nodeName:
            raise TypeError

        if direction is Direction.INCOMING:
            self.incomingEdges[nodeName] = communications
        elif direction is Direction.OUTGOING:
            edge = {'properties': relationshipProperties, 'communications': communications}
            self.outgoingEdges[nodeName] = edge
        else:
            raise ValueError

    def addCommunication(self, nodeName: str, communication: Communication, direction: Direction):
        if communication is None:
            raise TypeError
        
        if direction is Direction.INCOMING:
            self.incomingEdges[nodeName].append(communication)
        elif direction is Direction.OUTGOING:
            self.outgoingEdges[nodeName]['communications'].append(communication)
        else:
            raise ValueError

    def addRelationshipProperty(self, nodeName: str, relationshipProperty: RelationshipProperty):
        if not nodeName:
            raise TypeError

        self.outgoingEdges[nodeName]['properties'].append(relationshipProperty)

    def getRelationshipProperties(self, nodeName: str):
        if not nodeName:
            raise TypeError

        return self.outgoingEdges[nodeName]['properties']
    
    def getEdges(self, direction: Direction) -> dict:
        if direction is Direction.INCOMING:
            return self.incomingEdges
        elif direction is Direction.OUTGOING:
            return self.outgoingEdges
        else:
            raise ValueError
    
    def dump(self) -> str:
        return {'type': self.type, 'spec': self.spec, 'isEdge': self.isEdge, 'incomingEdges': self.incomingEdges, 'outgoingEdges': self.outgoingEdges}

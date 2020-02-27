from enum import Enum
from typing import Optional
from typing import List
from .types import NodeType, RelationshipProperty
from .communication import Communication

class Direction(Enum):
    INCOMING = 0
    OUTGOING = 1

class Node:

    def __init__(self, info: Optional(dict) = {}):
        self.info = info
        self.type = NodeType.MICROTOSCA_NODES_SERVICE
        self.incomingEdges = {}
        self.outgoingEdges = {}
        
    def getInfo(self) -> dict:
        return self.info

    def getType(self) -> NodeType:
        return self.type

    def setType(self, nodeType: nodeType):
        if nodeType is None:
            raise TypeError
        self.type = nodeType

    def addEdge(self, nodeName: str, direction: Direction, communications: Optional[List[Communication]] = []):
        if nodeName is None:
            raise TypeError

        if direction is Direction.INCOMING:
            self.incomingEdges[nodeName] = communications
        elif direction is Direction.OUTGOING:
            self.outgoingEdges[nodeName] = communications
        else:
            raise ValueError

    def addCommunication(self, nodeName: str, communication: Communication, direction: Direction):
        if communication is None:
            raise TypeError
        
        if direction is Direction.INCOMING:
            self.incomingEdges[nodeName].append(communication)
        elif direction is Direction.OUTGOING:
            self.outgoingEdges[nodeName].append(communication)
        else:
            raise ValueError
    
    def getEdges(self, direction: Direction) -> dict:
        if direction is Direction.INCOMING:
            return self.incomingEdges
        elif direction is Direction.OUTGOING:
            return self.outgoingEdges
        else:
            raise ValueError

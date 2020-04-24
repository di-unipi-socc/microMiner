from enum import Enum
from typing import Optional
from typing import List
from .microToscaTypes import NodeType, RelationshipProperty
from .communication import Communication
from .errors import EdgeExistsError, EdgeNotExistsError
import copy

class Direction(Enum):
    INCOMING = 0
    OUTGOING = 1

class Node:

    def __init__(self, name: str, spec: dict):
        self.frontendName = name
        self.spec = spec
        self.type = NodeType.MICROTOSCA_NODES_SERVICE
        self.isEdge = False
        self.incomingEdges = {}
        self.outgoingEdges = {}

    def getFrontendName(self) -> str:
        return self.frontendName

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

    def addEdge(self, nodeName: str, direction: Direction, communications: Optional[List[Communication]] = [], relationshipProperties: Optional[List[RelationshipProperty]] = [], isMicroToscaEdge: Optional[bool] = True):
        if direction is Direction.INCOMING:
            if not nodeName in self.incomingEdges:
                self.incomingEdges[nodeName] = communications
            else:
                raise EdgeExistsError('')
        elif direction is Direction.OUTGOING:
            if not nodeName in self.outgoingEdges:
                edge = {'isMicroToscaEdge': isMicroToscaEdge, 'properties': relationshipProperties, 'communications': communications}
                self.outgoingEdges[nodeName] = edge
            else:
                raise EdgeExistsError('')

    def addCommunication(self, nodeName: str, communication: Communication):
        if communication is None:
            raise TypeError
        
        if nodeName in self.incomingEdges:
            self.incomingEdges[nodeName].append(communication)
        if nodeName in self.outgoingEdges:
            self.outgoingEdges[nodeName]['communications'].append(communication)
        elif not nodeName in self.incomingEdges and not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

    def getCommunications(self, nodeName: str):
        communications = []
        if nodeName in self.incomingEdges:
            communications.extend(self.incomingEdges[nodeName])
        if nodeName in self.outgoingEdges:
            communications.extend(self.outgoingEdges[nodeName]['communications'])
        return communications

    def addRelationshipProperty(self, nodeName: str, relationshipProperty: RelationshipProperty):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        self.outgoingEdges[nodeName]['properties'].append(relationshipProperty)

    def getRelationshipProperties(self, nodeName: str):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        return self.outgoingEdges[nodeName]['properties']

    def getIsMicroToscaEdge(self, nodeName: str) -> bool:
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        return self.outgoingEdges[nodeName]['isMicroToscaEdge']
    
    def setIsMicroToscaEdge(self, nodeName: str, isMicroToscaEdge: bool):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        self.outgoingEdges[nodeName]['isMicroToscaEdge'] = isMicroToscaEdge
    
    def getEdges(self, direction: Direction) -> dict:
        if direction is Direction.INCOMING:
            return copy.deepcopy(self.incomingEdges)
        elif direction is Direction.OUTGOING:
            return copy.deepcopy(self.outgoingEdges)
        else:
            raise ValueError
    
    def dump(self) -> dict:
        return {'name': self.frontendName, 'type': self.type, 'spec': self.spec, 'isEdge': self.isEdge, 'incomingEdges': self.incomingEdges, 'outgoingEdges': self.outgoingEdges}

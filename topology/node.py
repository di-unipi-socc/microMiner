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
        return copy.copy(self.frontendName)

    def getSpec(self) -> dict:
        return copy.deepcopy(self.spec)

    def getType(self) -> NodeType:
        return copy.deepcopy(self.type)

    def setType(self, nodeType: NodeType):
        if nodeType is None:
            raise TypeError
        self.type = copy.deepcopy(nodeType)
    
    def getIsEdge(self) -> bool:
        return copy.copy(self.isEdge)
    
    def setIsEdge(self, isEdge: bool):
        self.isEdge = copy.copy(isEdge)

    def addEdge(self, nodeName: str, direction: Direction, communications: Optional[List[Communication]] = [], relationshipProperties: Optional[List[RelationshipProperty]] = [], isMicroToscaEdge: Optional[bool] = True):
        if direction is Direction.INCOMING:
            if not nodeName in self.incomingEdges:
                self.incomingEdges[nodeName] = copy.deepcopy(communications)
            else:
                raise EdgeExistsError('')
        elif direction is Direction.OUTGOING:
            if not nodeName in self.outgoingEdges:
                edge = {'isMicroToscaEdge': copy.copy(isMicroToscaEdge), 'properties': copy.deepcopy(relationshipProperties), 'communications': copy.deepcopy(communications)}
                self.outgoingEdges[nodeName] = edge
            else:
                raise EdgeExistsError('')

    def addCommunication(self, nodeName: str, communication: Communication):
        if communication is None:
            raise TypeError
        
        if nodeName in self.incomingEdges:
            self.incomingEdges[nodeName].append(copy.deepcopy(communication))
        if nodeName in self.outgoingEdges:
            self.outgoingEdges[nodeName]['communications'].append(copy.deepcopy(communication))
        elif not nodeName in self.incomingEdges and not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

    def getCommunications(self, nodeName: str):
        communications = []
        if nodeName in self.incomingEdges:
            communications.extend(self.incomingEdges[nodeName])
        if nodeName in self.outgoingEdges:
            communications.extend(self.outgoingEdges[nodeName]['communications'])
        return copy.deepcopy(communications)

    def addRelationshipProperty(self, nodeName: str, relationshipProperty: RelationshipProperty):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        self.outgoingEdges[nodeName]['properties'].append(copy.deepcopy(relationshipProperty))

    def getRelationshipProperties(self, nodeName: str):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        return copy.deepcopy(self.outgoingEdges[nodeName]['properties'])

    def getIsMicroToscaEdge(self, nodeName: str) -> bool:
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        return copy.copy(self.outgoingEdges[nodeName]['isMicroToscaEdge'])
    
    def setIsMicroToscaEdge(self, nodeName: str, isMicroToscaEdge: bool):
        if not nodeName in self.outgoingEdges:
            raise EdgeNotExistsError('')

        self.outgoingEdges[nodeName]['isMicroToscaEdge'] = copy.copy(isMicroToscaEdge)
    
    def getEdges(self, direction: Direction) -> dict:
        if direction is Direction.INCOMING:
            return copy.deepcopy(self.incomingEdges)
        elif direction is Direction.OUTGOING:
            return copy.deepcopy(self.outgoingEdges)
        else:
            raise ValueError
    
    def dump(self) -> dict:
        return {'name': self.frontendName, 'type': self.type, 'spec': self.spec, 'isEdge': self.isEdge, 'incomingEdges': self.incomingEdges, 'outgoingEdges': self.outgoingEdges}

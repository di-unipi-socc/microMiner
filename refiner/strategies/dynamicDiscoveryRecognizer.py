from ..generic.refiner import Refiner
from topology.communication import Communication
from topology.node import Node, Direction
from topology.microToscaTypes import RelationshipProperty
from topology.protocols import IP
import ipaddress

class DynamicDiscoveryRecognizer(Refiner):

    def __init__(self):
        pass

    @classmethod
    def recognize(cls, nodes: dict, args: dict):
        for node in nodes.values():
            edges = node.getEdges(Direction.OUTGOING)
            for adjacentName in edges.keys():
                communications = node.getCommunications(adjacentName, Direction.OUTGOING)
                ipAddress = None
                for communication in communications:
                    protocol = communication.getNetworkLayer()
                    if 'ip' in protocol:
                        actualIP = protocol['ip'].getReceiverIP()
                        if actualIP != ipAddress:
                            node.addRelationshipProperty(adjacentName, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY)
                            break

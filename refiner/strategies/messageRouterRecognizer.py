from refiner.generic.refiner import Refiner
from topology.communication import Communication
from topology.node import Node, Direction
from topology.microToscaTypes import NodeType, RelationshipProperty
from topology.protocols import IP, HTTP
import ipaddress

class MessageRouterRecognizer(Refiner):

    def __init__(self):
        pass

    @classmethod
    def recognize(cls, nodes: dict, args: dict):
        for nodeName, node in nodes.items():
            if node.getType() is NodeType.MICROTOSCA_NODES_SERVICE:
                edges = node.getEdges(Direction.INCOMING)
                edges.update(node.getEdges(Direction.OUTGOING))
                for adjacentName in edges.keys():
                    communications = node.getCommunications(adjacentName)
                    for communication in communications:
                        networkProtocol = communication.getNetworkLayer()
                        if not 'ip' in networkProtocol:
                            continue
                        applicationProtocol = communication.getApplicationLayer()
                        if not 'http' in applicationProtocol:
                            continue
                        xForwardedFor = applicationProtocol['http'].getXForwardedForHeader()
                        if xForwardedFor.len() < 2:
                            continue
                        i = 1
                        while i < xForwardedFor.len():
                            if nodeName == networkProtocol['ip'].getSenderHost() and xForwardedFor[i] == str(networkProtocol['ip'].getSenderIP()):
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER)
                                break
                        if node.getType() is NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER:
                            break
                    if node.getType() is NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER:
                            break

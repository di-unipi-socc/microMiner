from refiner.generic.refiner import Refiner
from topology.communication import Communication
from topology.node import Node, Direction
from topology.microToscaTypes import NodeType, RelationshipProperty
from topology.protocols import IP
import ipaddress

class DynamicDiscoveryRecognizer(Refiner):

    def __init__(self):
        pass

    @classmethod
    def recognize(cls, nodes: dict, args: dict):
        for nodeName, node in nodes.items():
            if node.getType() == NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER:
                continue
            edges = node.getEdges(Direction.OUTGOING)
            for adjacentName in edges.keys():
                if nodes[adjacentName].getType() == NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER or not node.getIsMicroToscaEdge(adjacentName):
                    continue
                communications = node.getCommunications(adjacentName)
                ipAddress = ''
                for communication in communications:
                    protocol = communication.getNetworkLayer()
                    actualIP = ''
                    '''
                    print('senderHost: ' + protocol['ip'].getSenderHost())
                    print('receiverHost: ' + protocol['ip'].getReceiverHost())
                    print('nodeName: ' + nodeName)
                    print('adjacentName: ' + adjacentName)
                    '''
                    if 'ip' in protocol and nodeName == protocol['ip'].getSenderHost():
                        #print(adjacentName + '!=' + protocol['ip'].getReceiverHost())
                        #assert adjacentName == protocol['ip'].getReceiverHost()
                        actualIP = str(protocol['ip'].getReceiverIP())
                    elif 'ip' in protocol and nodeName == protocol['ip'].getReceiverHost():
                        #print(adjacentName + '!=' + protocol['ip'].getSenderHost())
                        #assert adjacentName == protocol['ip'].getSenderHost()
                        actualIP = str(protocol['ip'].getSenderIP())
                    if ipAddress == '':
                        ipAddress = actualIP
                    elif actualIP != ipAddress:
                        node.addRelationshipProperty(adjacentName, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY)
                        break

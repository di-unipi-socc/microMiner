from refiner.generic.refiner import Refiner
from topology.node import Node, Direction
from topology.communication import Communication
from topology.microToscaTypes import NodeType
from topology.protocols import AMQP, MQTT, STOMP, IP

class MessageBrokerRecognizer(Refiner):

    AMQP =  {
                10: {   
                        11: 'client', 21: 'client', 31: 'client', 40: 'client',
                        10: 'server', 20: 'server', 30: 'server', 41: 'server'  
                    },   
                20: {
                        10: 'client', 11: 'server'             
                    },
                40: {
                        10: 'client', 20: 'client',
                        11: 'server', 21: 'server'
                    },
                50: {
                        10: 'client', 20: 'client', 50: 'client', 30: 'client', 40: 'client',                
                        11: 'server', 21: 'server', 51: 'server', 31: 'server', 41: 'server'
                    },
                60: {
                        10: 'client', 20: 'client', 30: 'client', 40: 'client', 70: 'client', 80: 'client', 90: 'client', 100: 'client', 110: 'client',
                        11: 'server', 21: 'server', 31: 'server', 50: 'server', 60: 'server', 71: 'server', 72: 'server', 111: 'server'
                    },
                90: {
                        10: 'client', 20: 'client', 30: 'client',
                        11: 'server', 21: 'server', 31: 'server'     
                    },
            }

    STOMP = {
                'CONNECT': 'client', 'SEND' : 'client', 'SUBSCRIBE': 'client', 'UNSUBSCRIBE': 'client', 
                'BEGIN': 'client', 'COMMIT': 'client', 'ABORT': 'client', 
                'ACK': 'client', 'NACK': 'client', 'DISCONNECT': 'client', 
                'CONNECTED': 'server', 'MESSAGE': 'server', 'RECEIPT': 'server', 'ERROR': 'server'
            }
    
    MQTT =  {
                1: 'client', 8: 'client', 10: 'client', 12: 'client',
                2: 'server', 9: 'server', 11: 'server', 13: 'server'
            }

    def __init__(self):
        pass
    
    @classmethod
    def recognize(cls, nodes: dict, args: dict):
        for nodeName, node in nodes.items():
            if node.getType() is NodeType.MICROTOSCA_NODES_SERVICE:
                edges = node.getEdges(Direction.INCOMING)
                edges.update(node.getEdges(Direction.OUTGOING))
                isAClient = False
                for adjacentName in edges.keys():
                    communications = node.getCommunications(adjacentName)
                    for communication in communications:
                        networkProtocol = communication.getNetworkLayer()
                        if not 'ip' in networkProtocol:
                            continue
                        applicationProtocol = communication.getApplicationLayer()
                        if 'amqp' in applicationProtocol and applicationProtocol['amqp'].getVersion() == '0.9.1':
                            classID = applicationProtocol['amqp'].getClassID()
                            methodID = applicationProtocol['amqp'].getMethodID()
                            if methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'client' and nodeName == networkProtocol['ip'].getReceiverHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'server' and nodeName == networkProtocol['ip'].getSenderHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'client' and nodeName == networkProtocol['ip'].getSenderHost():
                                isAClient = True
                                break
                            elif methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'server' and nodeName == networkProtocol['ip'].getReceiverHost():
                                isAClient = True
                                break
                        elif 'amqp' in applicationProtocol and applicationProtocol['amqp'].getVersion() == '1.0.0':
                            pass
                        elif 'mqtt' in applicationProtocol:
                            controlPacketType = applicationProtocol['mqtt'].getControlPacketType()
                            if controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'client' and nodeName == networkProtocol['ip'].getReceiverHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'server' and nodeName == networkProtocol['ip'].getSenderHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'client' and nodeName == networkProtocol['ip'].getSenderHost():
                                isAClient = True
                                break
                            elif controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'server' and nodeName == networkProtocol['ip'].getReceiverHost():
                                isAClient = True
                                break
                        elif 'stomp' in applicationProtocol:
                            command = applicationProtocol['stomp'].getCommand()
                            if command in cls.STOMP and cls.STOMP[command] == 'client' and nodeName == networkProtocol['ip'].getReceiverHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif command in cls.STOMP and cls.STOMP[command] == 'server' and nodeName == networkProtocol['ip'].getSenderHost():
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif command in cls.STOMP and cls.STOMP[command] == 'client' and nodeName == networkProtocol['ip'].getSenderHost():
                                isAClient = True
                                break
                            elif command in cls.STOMP and cls.STOMP[command] == 'server' and nodeName == networkProtocol['ip'].getReceiverHost():
                                isAClient = True
                                break
                    if isAClient:
                        break

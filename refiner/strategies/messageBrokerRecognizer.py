from ..generic.refiner import Refiner
from topology.node import Node, Direction
from topology.communication import Communication
from topology.microToscaTypes import NodeType
from topology.protocols import AMQP, MQTT, STOMP

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
                'SEND' : 'client', 'SUBSCRIBE': 'client', 'UNSUBSCRIBE': 'client', 
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
        
        # Per ogni nodo della topologia
        # Itero sulle comunicazioni di un nodo e controllo se c'è uno dei protocolli che supporto
        # Se si tratta di AMQP 0.9.1, MQTT, STOMP, allora mi bastano solo gli outgoing edges
        # Se si tratta di AMQP 1.0.0 mi servono anche gli incoming edges e devo eseguire l'algoritmo

        for node in nodes.values():
            edges = node.getEdges(Direction.OUTGOING)
            if node.getType() is NodeType.MICROTOSCA_NODES_SERVICE:
                for adjacentName in edges.keys():
                    communications = node.getCommunication(adjacentName, Direction.OUTGOING)
                    for communication in communications:
                        protocol = communication.getApplicationLayer()
                        if 'amqp' in protocol and protocol['amqp'].version() == '0.9.1':
                            classID = protocol['amqp'].getClassID()
                            methodID = protocol['amqp'].getMethodID()
                            if methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'client':
                                nodes[adjacentName].setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif methodID in cls.AMQP[classID] and cls.AMQP[classID][methodID] == 'server':
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                        elif 'amqp' in protocol and protocol['amqp'].version() == '1.0.0':
                            pass
                        elif 'mqtt' in protocol:
                            controlPacketType = protocol['mqtt'].getControlPacketType()
                            if controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'client':
                                nodes[adjacentName].setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif controlPacketType in cls.MQTT and cls.MQTT[controlPacketType] == 'server':
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                        elif 'stomp' in protocol:
                            command = protocol['stomp'].getCommand()
                            if command in cls.STOMP and cls.STOMP[command] == 'client':
                                nodes[adjacentName].setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break
                            elif command in cls.STOMP and cls.STOMP[command] == 'server':
                                node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_BROKER)
                                break

from topology.node import Node, Direction
from topology.communication import Communication
from topology.concreteCommunicationFactory import ConcreteCommunicationFactory
from refiner.strategies.messageBrokerRecognizer import MessageBrokerRecognizer
from exporter.ymlExporter import YMLExporter
import copy

def test():
    AMPQPacket = {
                "_source": {
                    "layers": {
                        "ip": {
                            "ip.version": "4",
                            "ip.hdr_len": "20",
                            "ip.dsfield": "0x00000000",
                            "ip.dsfield_tree": {
                                "ip.dsfield.dscp": "0",
                                "ip.dsfield.ecn": "0"
                            },
                            "ip.len": "585",
                            "ip.id": "0x00009a48",
                            "ip.flags": "0x00004000",
                            "ip.flags_tree": {
                                "ip.flags.rb": "0",
                                "ip.flags.df": "1",
                                "ip.flags.mf": "0"
                            },
                            "ip.frag_offset": "0",
                            "ip.ttl": "64",
                            "ip.proto": "6",
                            "ip.checksum": "0x0000a064",
                            "ip.checksum.status": "2",
                            "ip.src": "127.0.0.1",
                            "ip.addr": "127.0.0.1",
                            "ip.src_host": "B",
                            "ip.host": "127.0.0.1",
                            "ip.dst": "127.0.0.1",
                            "ip.addr": "127.0.0.1",
                            "ip.dst_host": "A",
                            "ip.host": "127.0.0.1"
                            },
                        "amqp": {
                            "amqp.type": "1",
                            "amqp.channel": "0",
                            "amqp.length": "454",
                            "amqp.method.class": "10",
                            "amqp.method.method": "10",
                            "amqp.method.arguments": {
                                "amqp.method.arguments.version_major": "0",
                                "amqp.method.arguments.version_minor": "9",
                                "amqp.method.arguments.server_properties": {
                                "amqp.field": {
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": "",
                                    "amqp.field": ""
                                },
                                "amqp.field": "",
                                "amqp.field": "",
                                "amqp.field": "",
                                "amqp.field": "",
                                "amqp.field": "",
                                "amqp.field": ""
                                },
                                "amqp.method.arguments.mechanisms": "41:4d:51:50:4c:41:49:4e:20:50:4c:41:49:4e",
                                "amqp.method.arguments.locales": "65:6e:5f:55:53"
                            }
                        }
                    }
                }
            }

    MQTTPAcket = {
                "_source": {
                    "layers": {
                        "ip": {
                            "ip.version": "4",
                            "ip.hdr_len": "20",
                            "ip.dsfield": "0x00000000",
                            "ip.dsfield_tree": {
                                "ip.dsfield.dscp": "0",
                                "ip.dsfield.ecn": "0"
                            },
                            "ip.len": "151",
                            "ip.id": "0x000086b2",
                            "ip.flags": "0x00004000",
                            "ip.flags_tree": {
                                "ip.flags.rb": "0",
                                "ip.flags.df": "1",
                                "ip.flags.mf": "0"
                            },
                            "ip.frag_offset": "0",
                            "ip.ttl": "53",
                            "ip.proto": "6",
                            "ip.checksum": "0x0000a158",
                            "ip.checksum.status": "2",
                            "ip.src": "5.196.95.208",
                            "ip.addr": "5.196.95.208",
                            "ip.src_host": "A",
                            "ip.host": "5.196.95.208",
                            "ip.dst": "172.100.11.94",
                            "ip.addr": "172.100.11.94",
                            "ip.dst_host": "C",
                            "ip.host": "172.100.11.94"
                            },
                        "mqtt": {
                            "mqtt.hdrflags": "0x00000030",
                            "mqtt.hdrflags_tree": {
                                "mqtt.msgtype": "8",
                                "mqtt.dupflag": "0",
                                "mqtt.qos": "0",
                                "mqtt.retain": "0"
                            },
                            "mqtt.len": "109",
                            "mqtt.topic_len": "19",
                            "mqtt.topic": "ASN_Mobile__LifeBit",
                            "mqtt.msg": "7b:22:64:61:74:61:74:79:70:65:22:3a:22:42:4f:4f:4c:22:2c:22:6e:61:6d:65:22:3a:22:5f:4c:49:46:45:42:49:54:22:2c:22:76:61:6c:75:65:22:3a:22:30:22:2c:22:74:69:6d:65:73:74:61:6d:70:22:3a:22:32:30:32:30:2d:30:34:2d:30:33:54:31:35:3a:32:36:3a:34:37:2e:32:35:30:5a:22:7d"
                        }
                    }
                }
            }


    STOMPPacket = {
                "_source": {
                    "layers": {
                        "ip": {
                            "ip.version": "4",
                            "ip.hdr_len": "20",
                            "ip.dsfield": "0x00000000",
                            "ip.dsfield_tree": {
                                "ip.dsfield.dscp": "0",
                                "ip.dsfield.ecn": "0"
                            },
                            "ip.len": "114",
                            "ip.id": "0x00007817",
                            "ip.flags": "0x00004000",
                            "ip.flags_tree": {
                                "ip.flags.rb": "0",
                                "ip.flags.df": "1",
                                "ip.flags.mf": "0"
                            },
                            "ip.frag_offset": "0",
                            "ip.ttl": "64",
                            "ip.proto": "6",
                            "ip.checksum": "0x0000c468",
                            "ip.checksum.status": "2",
                            "ip.src": "127.0.0.1",
                            "ip.addr": "127.0.0.1",
                            "ip.src_host": "A",
                            "ip.host": "127.0.0.1",
                            "ip.dst": "127.0.0.5",
                            "ip.addr": "127.0.0.5",
                            "ip.dst_host": "D",
                            "ip.host": "127.0.0.5"
                            },
                        "stomp": {
                            "stomp.command": "CONNECT",
                            "stomp.header": "accept-version:1.1,1.0",
                            "stomp.header_tree": {
                                "stomp.header.key": "accept-version",
                                "stomp.header.value": "1.1,1.0"
                            },
                            "stomp.header": "heart-beat:10000,10000",
                            "stomp.header_tree": {
                                "stomp.header.key": "heart-beat",
                                "stomp.header.value": "10000,10000"
                            },
                            "stomp.body": ""
                        }
                    }
                }
            }

    A = Node('A', {})
    B = Node('B', {})
    C = Node('C', {})
    D = Node('D', {})
    A.addEdge('B', Direction.OUTGOING)
    B.addEdge('A', Direction.INCOMING)
    A.addEdge('C', Direction.OUTGOING)
    C.addEdge('A', Direction.INCOMING)
    A.addEdge('D', Direction.OUTGOING)
    D.addEdge('A', Direction.INCOMING)

    commFactory = ConcreteCommunicationFactory()
    commAMQP = commFactory.build(AMPQPacket)
    commMQTT = commFactory.build(MQTTPAcket)
    commSTOMP = commFactory.build(STOMPPacket)

    A.addCommunication('B', commAMQP)
    B.addCommunication('A', commAMQP)
    A.addCommunication('C', commMQTT)
    C.addCommunication('A', commMQTT)
    A.addCommunication('D', commSTOMP)
    D.addCommunication('A', commSTOMP)

    topology = {'A': A, 'B': B, 'C': C, 'D': D}

    MessageBrokerRecognizer.recognize(topology, {})

    YMLExporter.export(topology, './tests/refiner/messageBrokerRecognizer/microTOSCA.yml')

if __name__ == '__main__':
    test()

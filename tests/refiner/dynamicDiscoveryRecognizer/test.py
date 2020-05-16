from topology.node import Node, Direction
from topology.communication import Communication
from topology.concreteCommunicationFactory import ConcreteCommunicationFactory
from refiner.strategies.dynamicDiscoveryRecognizer import DynamicDiscoveryRecognizer
from exporter.ymlExporter import YMLExporter
import copy

def test():
    
    packet1 = {
            "_index": "packets-2004-05-13",
            "_type": "pcap_file",
            "_score": "null",
            "_source": {
                "layers": {
                    "frame": {
                        "frame.encap_type": "1",
                        "frame.time": "May 13, 2004 12:17:07.311224000 ora legale Europa occidentale",
                        "frame.offset_shift": "0.000000000",
                        "frame.time_epoch": "1084443427.311224000",
                        "frame.time_delta": "0.000000000",
                        "frame.time_delta_displayed": "0.000000000",
                        "frame.time_relative": "0.000000000",
                        "frame.number": "1",
                        "frame.len": "62",
                        "frame.cap_len": "62",
                        "frame.marked": "0",
                        "frame.ignored": "0",
                        "frame.protocols": "eth:ethertype:ip:tcp",
                        "frame.coloring_rule.name": "HTTP",
                        "frame.coloring_rule.string": "http || tcp.port == 80 || http2"
                        },
                        "eth": {
                        "eth.dst": "fe:ff:20:00:01:00",
                        "eth.dst_tree": {
                            "eth.dst_resolved": "fe:ff:20:00:01:00",
                            "eth.addr": "fe:ff:20:00:01:00",
                            "eth.addr_resolved": "fe:ff:20:00:01:00",
                            "eth.lg": "1",
                            "eth.ig": "0"
                        },
                        "eth.src": "00:00:01:00:00:00",
                        "eth.src_tree": {
                            "eth.src_resolved": "Xerox_00:00:00",
                            "eth.addr": "00:00:01:00:00:00",
                            "eth.addr_resolved": "Xerox_00:00:00",
                            "eth.lg": "0",
                            "eth.ig": "0"
                        },
                        "eth.type": "0x00000800"
                        },
                        "ip": {
                        "ip.version": "4",
                        "ip.hdr_len": "20",
                        "ip.dsfield": "0x00000000",
                        "ip.dsfield_tree": {
                            "ip.dsfield.dscp": "0",
                            "ip.dsfield.ecn": "0"
                        },
                        "ip.len": "48",
                        "ip.id": "0x00000f41",
                        "ip.flags": "0x00004000",
                        "ip.flags_tree": {
                            "ip.flags.rb": "0",
                            "ip.flags.df": "1",
                            "ip.flags.mf": "0"
                        },
                        "ip.frag_offset": "0",
                        "ip.ttl": "128",
                        "ip.proto": "6",
                        "ip.checksum": "0x000091eb",
                        "ip.checksum.status": "2",
                        "ip.src": "145.254.160.237",
                        "ip.src_host": "A",
                        "ip.dst": "65.208.228.223",
                        "ip.dst_host": "B",
                        }
                    }
                }
            }

    packet2 = copy.deepcopy(packet1)
    packet2['_source']['layers']['ip']['ip.dst'] = '65.208.228.224'
    packet3 = copy.deepcopy(packet1)
    packet3['_source']['layers']['ip']['ip.dst_host'] = 'C'
    packet3['_source']['layers']['ip']['ip.dst'] = '65.208.228.225'
    packet4 = copy.deepcopy(packet3)


    A = Node('A', {})
    B = Node('B', {})
    C = Node('C', {})
    A.addEdge('B', Direction.OUTGOING)
    B.addEdge('A', Direction.INCOMING)
    A.addEdge('C', Direction.OUTGOING)
    C.addEdge('A', Direction.INCOMING)

    commFactory = ConcreteCommunicationFactory()
    comm1 = commFactory.build(packet1)
    comm2 = commFactory.build(packet2)
    comm3 = commFactory.build(packet3)
    comm4 = commFactory.build(packet4)
    A.addCommunication('B', comm1)
    A.addCommunication('B', comm2)
    B.addCommunication('A', comm1)
    B.addCommunication('A', comm2)
    A.addCommunication('C', comm3)
    A.addCommunication('C', comm4)
    C.addCommunication('A', comm3)
    C.addCommunication('A', comm4)

    topology = {'A': A, 'B': B, 'C': C}

    DynamicDiscoveryRecognizer.recognize(topology, {})

    YMLExporter.export(topology, './tests/refiner/dynamicDiscoveryRecognizer/microTOSCA.yml')

if __name__ == '__main__':
    test()
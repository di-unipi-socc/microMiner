from .errors import NoInfoError
import ipaddress

class IP:
    
    def __init__(self, packet: dict):
        self.senderIP = ipaddress.ip_address(packet['ip.src'])
        self.receiverIP = ipaddress.ip_address(packet['ip.dst'])
        self.senderHost = packet['ip.src_host']
        self.receiverHost = packet['ip.dst_host']

    def getSenderIP(self) -> ipaddress:
        return self.senderIP
    
    def getReceiverIP(self) -> ipaddress:
        return self.receiverIP

    def getSenderHost(self) -> str:
        return self.senderHost
    
    def getReceiverHost(self) -> str:
        return self.receiverHost


class AMQP:
    
    def __init__(self, packet: dict):
        #AMQP 1.0
        if 'amqp.length' in packet and 'amqp.doff' in packet and 'amqp.type' in packet:
            if packet['amqp.type'] == '0' and packet['amqp.performative'] == '20':
                self.channel = packet['amqp.channel']
                self.more = bool(packet['amqp.method.arguments']['amqp.performative.arguments.more']) if 'amqp.performative.arguments.more' in packet['amqp.method.arguments'] else False
                self.handle = packet['amqp.method.arguments']['amqp.performative.arguments.handle']
                self.properties = packet['amqp.properties'] if 'amqp.properties' in packet else {}
                self.applicationProperties = packet['amqp.applicationProperties'] if 'amqp.applicationProperties' in packet else {}
                self.data = packet['amqp.data'] if 'amqp.data' in packet else ''
                self.version = '1.0.0'
            else:
                raise NoInfoError('')
        #AMQP 0.9.1
        elif 'amqp.type' in packet and 'amqp.channel' in packet and 'amqp.length' in packet:
            if packet['amqp.type'] == '1':
                self.version = '0.9.1'
                self.classID = packet['amqp.method.class']
                self.methodID = packet['amqp.method.method']
            else:
                raise NoInfoError('')
        else:
            raise NoInfoError('')
    
    def getVersion(self) ->  str:
        return self.version

    def getClassID(self) -> int:
        return int(self.classID)

    def getMethodID(self) -> int:
        return int(self.methodID)
    
    def getChannel(self) -> int:
        return int(self.channel)

    def getMore(self) -> bool:
        return self.more
    
    def getHandle(self) -> int:
        return int(self.handle)

    def getProperties(self) -> dict:
        return self.properties

    def getApplicationProperties(self) -> dict:
        return self.applicationProperties
    
    def getData(self) -> str:
        return self.data


class MQTT:
    
    def __init__(self, packet: dict):
        self.controlPacketType = int(packet['mqtt.hdrflags_tree']['mqtt.msgtype'])
    
    def getControlPacketType(self) -> int:
        return self.controlPacketType


class STOMP:
    
    def __init__(self, packet: dict):
        self.command = packet['stomp.command']

    def getCommand(self) -> str:
        return self.command


class HTTP:
    
    def __init__(self, packet: dict):
        pass

#    def getHeaders(self) -> dict:
#        return self.headers

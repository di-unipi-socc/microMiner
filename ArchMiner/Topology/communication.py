from typing import Optional
from abc import ABC, abstractmethod
import ipaddress

class Communication(ABC):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress):
        if senderIP is None or receiverIP is None:
            raise TypeError

        self.senderIP = senderIP
        self.receiverIP = receiverIP

    @abstractmethod
    def getSenderIP(self) -> ipaddress:
        return self.senderIP
    
    @abstractmethod
    def getReceiverIP(self) -> ipaddress:
        return self.receiverIP


class AMQP091Communication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, classID: int, methodID: int):
        super.__init__(senderIP, receiverIP)
        self.classID = classID
        self.methodID = methodID

    def getClassID(self) -> int:
        return self.classID

    def getMethodID(self) -> int:
        return self.methodID


class AMQP1Communication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, hashBareMessage: str):
        super.__init__(senderIP, receiverIP)
        self.hashBareMessage = hashBareMessage

    def getHashBareMessage(self) -> str:
        return self.hashBareMessage


class MQTTCommunication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, controlPacketType: int):
        super.__init__(senderIP, receiverIP)
        self.controlPacketType = controlPacketType
    
    def getControlPacketType(self) -> int:
        return self.controlPacketType


class STOMPCommunication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, command: str):
        super.__init__(senderIP, receiverIP)
        self.command = command

    def getCommand(self) -> str:
        return self.command


class HTTPCommunication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, headers: dict):
        super.__init__(senderIP, receiverIP)
        self.headers = headers

    def getHeaders(self) -> dict:
        return self.headers


class TCPCommunication(Communication):
    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, SYN: Optional[bool] = False):
        super.__init__(senderIP, receiverIP)
        self.SYN = SYN

    def getSYN(self) -> bool:
        return self.SYN

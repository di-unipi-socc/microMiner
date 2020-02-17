import ipaddress

class Communication:

    def __init__(self, senderIP: ipaddress, receiverIP: ipaddress, SYN: bool):
        self.senderIP = senderIP
        self.receiverIP = receiverIP
        self.SYN = SYN

    





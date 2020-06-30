from typing import Optional

class Communication:

    def __init__(self, networkLayer, transportLayer, applicationLayer):
        #Dizionario nome del protocollo a livello di rete -> informazioni estratte
        self.networkLayer = networkLayer
        #Dizionario nome del protocollo a livello di trasporto -> informazioni estratte
        self.transportLayer = transportLayer
        #Dizionario nome del protocollo a livello di applicazione -> informazioni estratte
        self.applicationLayer = applicationLayer

    def getNetworkLayer(self):
        return self.networkLayer
    
    def getTransportLayer(self):
        return self.transportLayer

    def getApplicationLayer(self):
        return self.applicationLayer

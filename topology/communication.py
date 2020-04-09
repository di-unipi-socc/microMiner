from typing import Optional

class Communication:

    def __init__(self, networkLayer, transportLayer, applicationLayer):
        self.networkLayer = networkLayer
        self.transportLayer = transportLayer
        self.applicationLayer = applicationLayer

    def getNetworkLayer(self):
        return self.networkLayer
    
    def getTransportLayer(self):
        return self.transportLayer

    def getApplicationLayer(self):
        return self.applicationLayer

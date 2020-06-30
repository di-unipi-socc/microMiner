from .communication import Communication
from ruamel.yaml import YAML
from pathlib import Path
from .errors import NoInfoError

class ConcreteCommunicationFactory:

    def __init__(self):
        #Carico i protocolli di comunicazione supportati
        loader = YAML(typ='safe')
        protocols = loader.load(Path('topology/protocols.yml'))
        self.networkLayerProtocols = protocols['networkLayer']
        self.transportLayerProtocols = protocols['transportLayer']
        self.applicationLayerProtocols = protocols['applicationLayer']

    def build(self, packet: dict) -> Communication:
        #Recupero il protocollo di rete, di trasporto, di applicazione
        networkProtocols = set(packet['_source']['layers'].keys()) & set(self.networkLayerProtocols.keys())
        transportProtocols = set(packet['_source']['layers'].keys()) & set(self.transportLayerProtocols.keys())
        applicationProtocols = set(packet['_source']['layers'].keys()) & set(self.applicationLayerProtocols.keys())
        
        #Per ogni protocollo, carico la classe e ne creo un'istanza
        netDict, transportDict, appDict = {}, {}, {}
        if len(networkProtocols) == 1:
            networkProtocolName = networkProtocols.pop()
            networkProtocolCls = self._get_class(self.networkLayerProtocols[networkProtocolName])
            networkProtocolInstance = networkProtocolCls(packet['_source']['layers'][networkProtocolName])
            netDict = {networkProtocolName: networkProtocolInstance}
        if len(transportProtocols) == 1:
            transportProtocolName = transportProtocols.pop()
            transportProtocolCls = self._get_class(self.transportLayerProtocols[transportProtocolName])
            transportProtocolInstance = transportProtocolCls(packet['_source']['layers'][transportProtocolName])
            transportDict = {transportProtocolName: transportProtocolInstance}
        if len(applicationProtocols) == 1:
            applicationProtocolName = applicationProtocols.pop()
            applicationProtocolCls = self._get_class(self.applicationLayerProtocols[applicationProtocolName])
            try:
                applicationProtocolInstance = applicationProtocolCls(packet['_source']['layers'][applicationProtocolName])
                appDict = {applicationProtocolName: applicationProtocolInstance}
            except(NoInfoError):
                pass

        return Communication(netDict, transportDict, appDict)

    
    def _get_class(self, fqnClass: str):
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

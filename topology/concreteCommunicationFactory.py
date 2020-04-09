from .communication import Communication
from ruamel.yaml import YAML
from pathlib import Path
from errors import NoInfoError

class ConcreteCommunicationFactory:

    def __init__(self):
        loader = YAML(typ='safe')
        protocols = loader.load(Path('topology/communications.yml'))
        self.networkLayerProtocols = protocols['networkLayer']
        self.transportLayerProtocols = protocols['transportLayer']
        self.applicationLayerProtocols = protocols['applicationLayer']

    def build(self, packet: dict) -> Communication:
        networkProtocol = set(packet['_source']['layers'].keys()) & set(self.networkLayerProtocols.keys())
        transportProtocol = set(packet['_source']['layers'].keys()) & set(self.transportLayerProtocols.keys())
        applicationProtocol = set(packet['_source']['layers'].keys()) & set(self.applicationLayerProtocols.keys())

        if len(networkProtocol) != 1 or len(transportProtocol) != 1 or len(applicationProtocol) != 1:
            raise TypeError

        networkProtocolCls = self._get_class(self.networkLayerProtocols[networkProtocol])
        transportProtocolCls = self._get_class(self.transportLayerProtocols[transportProtocol])
        applicationProtocolCls = self._get_class(self.applicationLayerProtocols[applicationProtocol])

        appProtInstance = None
        try:
            appProtInstance = applicationProtocolCls(packet['_source']['layers'][applicationProtocol])
        except(NoInfoError):
            pass

        return Communication({networkProtocol: networkProtocolCls(packet['_source']['layers'][networkProtocol])}, {transportProtocol: transportProtocolCls(packet['_source']['layers'][transportProtocol])}, {applicationProtocol: appProtInstance})

    
    def _get_class(self, fqnClass: str):
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

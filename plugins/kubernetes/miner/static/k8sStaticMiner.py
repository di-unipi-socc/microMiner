from .staticMiner import StaticMiner
from .k8sParserContext import K8sParserContext
from os import listdir
from os.path import Path, isdir, isfile, join, exists
from ...errors import StaticMinerError, WrongFolderError, UnsupportedTypeError, WrongFormatError
from ...topology.node import Node
from ...topology.types import NodeType, RelationshipProperty

class K8sStaticMiner(StaticMiner):

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, info: dict, nodes: dict):
        files = cls._listFiles(info['folderPath'])
        parser = K8sParserContext(info['parserVersions'])
        k8sObjects = []
        for k8sFile in files:
            try:
                k8sObjects.extend(parser.parse(k8sFile))
            except UnsupportedTypeError:
                print(k8sFile + 'is unsupported')
        
        for k8sObject in k8sObjects:
            if k8sObject:
                if k8sObject['type'] == 'pod':
                    node = Node(k8sObject['info'])
                    imageName = k8sObject['info']['image']
                    if cls._isDatabase(imageName):
                        node.setType(NodeType.MICROTOSCA_NODES_DATABASE)
                    elif cls._isIngressController(imageName):
                        pass
                    nodes[k8sObject['name']] = node
                elif k8sObject['type'] == 'endpoints':
                    endpoints = k8sObject['info']
                    for endpoint in endpoints:
                        name = endpoint.pop('name')
                        nodes[name] = Node(endpoint)
                elif k8sObject['type'] == 'service':
                    #vanno creati gli archi con i nodi corrispondenti
                    #se relativo ad un ingress non vanno inseriti nella topologia
                    #altrimenti va inserito come message router (nell'insieme edge se è di tipo NodePort o LoadBalancer)
                    pass
                elif k8sObject['type'] == 'ingress':
                    #cercare i service corrispondenti
                    #cercare l'ingress controller corrispondente tramite l'annotation ingress.class (nel db il nome dell'ingress e poi nel dict degli ingress controller)
                    #cercare i service corrispondenti
                    #creare un unico nodo messageRouter nell'edge
                    pass
    

    @classmethod
    def _listFiles(cls, folderPath: str) -> []:
        if not exists(folderPath) or not isdir(Path(folderPath)):
            raise WrongFolderError('')
        return [join(folderPath, f) for f in listdir(folderPath) if isfile(join(folderPath, f))]

    @classmethod
    def _isDatabase(cls, name: str) -> bool:
        isDatabase = False
        #TO-DO
        return isDatabase
        
    @classmethod
    def _isIngressController(cls, name: str) -> bool:
        isIngressController = False
        #TO-DO
        return isIngressController

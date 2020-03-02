from .....core.topology.node import Node, Direction
from .....core.topology.types import NodeType, RelationshipProperty
from .....core.miner.static.staticMiner import StaticMiner
from .errors import StaticMinerError, WrongFolderError, UnsupportedTypeError, WrongFormatError
from .parser.k8sParserContext import K8sParserContext
from os import listdir
from os.path import Path, isdir, isfile, join, exists

class K8sStaticMiner(StaticMiner):

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, info: dict, nodes: dict):
        files = cls._listFiles(info['folderPath'])
        parser = K8sParserContext(info['parserVersions'])
        parsedObjects = []

        #Effettuo il parsing dei file di Kubernetes
        for f in files:
            try:
                parsedObjects.extend(parser.parse(f))
            except UnsupportedTypeError:
                print(f + 'is unsupported')

        #Recupero i pods e gli endpoints
        for parsedObject in parsedObjects:
            if parsedObject:
                if parsedObject['type'] == 'pod':
                    node = Node(parsedObject)
                    imageName = parsedObject['info']['image']
                    if cls._isDatabase(imageName):
                        node.setType(NodeType.MICROTOSCA_NODES_DATABASE)
                    elif cls._isIngressController(imageName):
                        pass
                    nodes[parsedObject['name']] = node
                elif parsedObject['type'] == 'endpoints':
                    for endpoint in parsedObject['info']:
                        nodes[endpoint['name']] = Node(endpoint)

        #Recupero i service
        for parsedObject in parsedObjects:
            if parsedObject['type'] == 'service':
                serviceNode = Node(parsedObject)
                if parsedObject['info']['selector']:
                    #caso in cui il service abbia il selettore
                    for nodeName, node in nodes:
                        spec = node.getSpec()
                        if spec['type'] == 'pod' and 'labels' in spec['info']:
                            for key1, value1 in parsedObject['info']['selector']:
                                found = False
                                for key2, value2 in spec['info']['labels']:
                                    if key1 == key2 and value1 == value2:
                                        found = True
                                        break
                                if not found:
                                    break
                            if found:
                                node.addEdge(parsedObject['name'], Direction.INCOMING)  
                                serviceNode.addEdge(nodeName, Direction.OUTGOING)
                else:
                    #caso in cui il service sia senza selettore
                    for nodeName, node in nodes:
                        spec = node.getSpec()
                        if spec['type'] == 'endpoint':
                            found = False
                            for endpointPort in spec['ports']:
                                for servicePort in parsedObject['info']['ports']:
                                    if endpointPort['name'] == servicePort['name'] and endpointPort['number'] == servicePort['targetPort']:
                                        found = True
                                        break
                                if found:
                                    node.addEdge(parsedObject['name'], Direction.INCOMING)  
                                    serviceNode.addEdge(nodeName, Direction.OUTGOING)
                                    break

        #Recupero gli ingress
        for parsedObject in parsedObjects:                    
            if parsedObject['type'] == 'ingress':
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

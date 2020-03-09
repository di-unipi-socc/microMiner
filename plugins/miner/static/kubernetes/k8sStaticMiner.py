from .....core.topology.node import Node, Direction
from .....core.topology.types import NodeType, RelationshipProperty
from .....core.miner.static.staticMiner import StaticMiner
from .errors import StaticMinerError, WrongFolderError, UnsupportedTypeError, WrongFormatError
from .parser.k8sParserContext import K8sParserContext
from os import listdir
from os.path import Path, isdir, isfile, join, exists
from ruamel.yaml import YAML

class K8sStaticMiner(StaticMiner):

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, info: dict, nodes: dict):
        files = cls._listFiles(info['folderPath'])
        parser = K8sParserContext(info['parserVersions'])
        parsedObjects = []
        ingressControllers = {}

        #Effettuo il parsing dei file di Kubernetes
        for f in files:
            try:
                parsedObjects.extend(parser.parse(f))
            except UnsupportedTypeError:
                print(f + 'is unsupported')

        #Recupero i pods e gli endpoints
        for parsedObject in parsedObjects:
            if parsedObject and parsedObject['type'] == 'pod':
                node = Node(parsedObject)
                imageName = parsedObject['info']['image']
                if cls._isDatabase(imageName, info['dbImagesPath']):
                    node.setType(NodeType.MICROTOSCA_NODES_DATABASE)
                elif ingressClass := cls._isIngressController(imageName, info['controllerImagesPath']):
                    node.setType(NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER)
                    node.setIsEdge(True)
                    ingressControllers[ingressClass].append(node)
                nodes[parsedObject['name']] = node
                parsedObjects.remove(parsedObject)
            elif parsedObject and parsedObject['type'] == 'endpoints':
                for endpoint in parsedObject['info']:
                    nodes[endpoint['name']] = Node(endpoint)
                parsedObjects.remove(parsedObject)

        #Recupero i service
        for parsedObject in parsedObjects:
            if parsedObject and parsedObject['type'] == 'service':
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
                parsedObjects.remove(parsedObject)

        #Recupero gli ingress
        for parsedObject in parsedObjects:                    
            if parsedObject and parsedObject['type'] == 'ingress':
                #recupero i controllers
                if parsedObject['info']['controller'] != '':
                    controllerNodes = ingressControllers[parsedObject['info']['controller']]
                else:
                    controllerNodes = ingressControllers.values()
                #lego i controllers ai services corrispondenti
                for controller in controllerNodes:
                    for service in parsedObject['info']['services']:
                        serviceNode = nodes[service['name']]
                        controller.addEdge(service['name'], Direction.OUTGOING)
                        serviceNode.addEdge(controller.getSpec()['name'], Direction.INCOMING)
                parsedObjects.remove(parsedObject)
    

    @classmethod
    def _listFiles(cls, folderPath: str) -> []:
        if not exists(folderPath) or not isdir(Path(folderPath)):
            raise WrongFolderError('')
        return [join(folderPath, f) for f in listdir(folderPath) if isfile(join(folderPath, f))]

    @classmethod
    def _isDatabase(cls, imageName: str, filePath: str) -> bool:
        loader = YAML(typ='safe')
        databaseImages = loader.load(filePath)
        for databaseImage in databaseImages.values():
            if imageName == databaseImage['imageName']:
                return True
        return False
        
    @classmethod
    def _isIngressController(cls, imageName: str, filePath: str) -> str:
        loader = YAML(typ='safe')
        controllerImages = loader.load(filePath)
        for controllerImage, ingressClass in controllerImages:
            if imageName == controllerImage:
                return ingressClass
        return None

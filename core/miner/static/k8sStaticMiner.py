from .staticMiner import StaticMiner
from .k8sParserContext import K8sParserContext
from os import listdir
from os.path import Path, isdir, isfile, join, exists
from ...errors import StaticMinerError, WrongFolderError, UnsupportedTypeError, WrongFormatError

class K8sStaticMiner(StaticMiner):

    def __init__(self):
        pass

    @staticmethod
    def updateTopology(info: dict, nodes: dict):
        folderPath = info['folderPath']
        if not exists(folderPath) or not isdir(Path(folderPath)):
            raise WrongFolderError('')
        parser = K8sParserContext(info['parserVersions'])
        k8sFiles = [join(folderPath, f) for f in listdir(folderPath) if isfile(join(folderPath, f))]
        for k8sFile in k8sFiles:
            k8sObjects = []
            try:
                k8sObjects = parser.parse(k8sFile)
            except UnsupportedTypeError:
                print(k8sFile + 'is unsupported')
            for k8sObject in k8sObjects:
                if k8sObject:
                    if k8sObject['Type'] == 'pod':
                        pass
                    elif k8sObject['Type'] == 'service':
                        pass
                    elif k8sObject['Type'] == 'endpoints':
                        pass
                    elif k8sObject['Type'] == 'ingress':
                        pass
            
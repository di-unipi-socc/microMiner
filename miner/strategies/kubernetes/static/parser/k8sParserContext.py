import os.path
import re
import json
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional
from typing import Callable
from typing import Type
from .k8sParser import K8sParser
from .v1Parser import V1Parser
from .v1beta1Parser import V1beta1Parser
from .v1beta2Parser import V1beta2Parser
from ..errors import UnsupportedTypeError

class K8sParserContext:
    
    def __init__(self, versions: dict):
        self.versions = versions

    def addVersion(self, version: str, fqnParserClass: str):
        '''
        Installa una nuova versione del parser

        :param version: apiVersion di Kubernetes
        :param fqnParserClass: classe che implementa il parsing della versione dell'API
        '''
        self.versions[version] = fqnParserClass

    def parse(self, path: Path) -> []:
        if not(os.path.exists(path)):
            raise FileNotFoundError
        nodesInfo = []
        #Verifico se si tratta di JSON O YAML
        if path.endswith('.json'):
            contentStr = self._readFile(path)
            contentDict = json.loads(contentStr)
            try:
                #Estraggo la versione dell'API e tento di caricare la classe che implementa la strategia concreta
                apiVersion = contentDict['apiVersion'].split('/').pop()
                parser = self._getClass(self.versions[apiVersion])
            except:
                raise UnsupportedTypeError('Unsupported apiVersion')
            #Chiamo la funzione parse del parser
            nodesInfo.append(parser.parse(contentDict, contentStr))
        elif path.endswith('.yml') or path.endswith('.yaml'):
            yamlSplitted = re.split('^---\n', self._readFile(path), flags=re.MULTILINE)
            loader = YAML(typ='safe')
            for yaml in yamlSplitted:
                content = loader.load(yaml)
                if not content:
                    continue
                try:
                    #Estraggo la versione dell'API e tento di caricare la classe che implementa la strategia concreta
                    apiVersion = content['apiVersion'].split('/').pop()
                    parser = self._get_class(self.versions[apiVersion])
                except:
                    raise UnsupportedTypeError('Unsupported apiVersion')
                #Chiamo la funzione parse del parser
                nodesInfo.append(parser.parse(content, yaml))
        else:
            raise UnsupportedTypeError('Unsupported file type')
        return nodesInfo

    def _readFile(self, path: str) -> str:
        with open(path) as f:
            text = f.read()
        return text

    def _get_class(self, fqnClass: str) -> Type[K8sParser]:
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

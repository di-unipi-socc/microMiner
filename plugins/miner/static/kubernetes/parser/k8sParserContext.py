import os.path
import re
import json
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional
from typing import Callable
from .k8sParser import K8sParser
from .v1Parser import V1Parser
from .v1beta1Parser import V1beta1Parser
from .v1beta2Parser import V1beta2Parser
from ..errors import UnsupportedTypeError

class K8sParserContext:
    
    def __init__(self, versions: dict):
        self.versions = versions

    def addVersion(self, version: str, fqnParserClass: str):
        self.versions[version] = fqnParserClass

    def parse(self, path: Path) -> []:
        if not(os.path.exists(path)):
            raise FileNotFoundError
        nodesInfo = []
        if path.endswith('.json'):
            contentStr = self._readFile(path)
            contentDict = json.loads(contentStr)
            try:
                apiVersion = contentDict['apiVersion'].split('/').pop()
                parser = getClass(versions[apiVersion])
            except:
                raise UnsupportedTypeError('Unsupported apiVersion')
            nodesInfo.append(parser.parse(contentDict, contentStr))
        elif path.endswith('.yml'):
            yamlSplitted = self._readFile(path).split('---')
            loader = YAML(typ='safe')
            for yaml in yamlSplitted:
                content = loader.load(yaml)
                try:
                    apiVersion = content['apiVersion'].split('/').pop()
                    parser = getClass(versions[apiVersion])
                except:
                    raise UnsupportedTypeError('Unsupported apiVersion')
                nodesInfo.append(parser.parse(contentDict, yaml))
        else:
            raise UnsupportedTypeError('Unsupported file type')
        return nodesInfo

    def _readFile(self, path: str) -> str:
        with open(path) as f:
            text = f.read()
        return text

    def _get_class(self, fqnClass):
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

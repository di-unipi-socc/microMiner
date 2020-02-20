import os.path
import re
from os import path
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional
from typing import Callable
from .ymlv1Parser import Ymlv1Parser
from .ymlv1beta1Parser import Ymlv1beta1Parser
from .ymlv1beta2Parser import Ymlv1beta2Parser
from ...errors import UnsupportedTypeError

class K8SParserContext:
    
    def __init__(self, versions: Optional[dict] = {}):
        self.versions = versions

    def addVersion(self, version: tuple(str, str), function: Callable([[dict], dict])):
        self.versions[version] = function

    def parse(self, path: str) -> []:
        if not(os.path.exists(path)):
            raise FileNotFoundError
        nodesInfo = []
        if path.endswith('.json'):
            pass                           
        elif path.endswith('.yml'):
            yamlSplitted = self._splitFile(path)
            loader = YAML(typ='safe')
            for yaml in yamlSplitted:
                content = loader.load(yaml)
                try:
                    apiVersion = content['apiVersion'].split('/').pop()
                    nodesInfo.append(versions['yml', apiVersion](content))
                except:
                    raise UnsupportedTypeError('Unsupported file')
        else:
            raise UnsupportedTypeError('Unsupported type')
        return nodesInfo

    def _splitFile(self, path: str) -> []:
        #TO-DO: Rendere più efficiente leggendo in blocchi
        with open(path) as f:
            text = f.read()
        return text.split('---')

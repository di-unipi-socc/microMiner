import os.path
import re
import json
from os import path
from pathlib import Path
from ruamel.yaml import YAML
from typing import Optional
from typing import Callable
from .v1Parser import V1Parser
from .v1beta1Parser import V1beta1Parser
from .v1beta2Parser import V1beta2Parser
from ...errors import UnsupportedTypeError

class K8SParserContext:
    
    def __init__(self, versions: Optional[dict] = {}):
        self.versions = versions

    def addVersion(self, version: str, function: Callable([[dict, str], dict])):
        self.versions[version] = function

    def parse(self, path: str) -> []:
        if not(os.path.exists(path)):
            raise FileNotFoundError
        nodesInfo = []
        if path.endswith('.json'):
            contentStr = self._readFile(path)
            contentDict = json.loads(contentStr)
            try:
                apiVersion = contentDict['apiVersion'].split('/').pop()
                function = versions[apiVersion]
            except:
                raise UnsupportedTypeError('Unsupported apiVersion')
            nodesInfo.append(function(contentDict, contentStr))
        elif path.endswith('.yml'):
            yamlSplitted = self._readFile(path).split('---')
            loader = YAML(typ='safe')
            for yaml in yamlSplitted:
                content = loader.load(yaml)
                try:
                    apiVersion = content['apiVersion'].split('/').pop()
                    function = versions[apiVersion]
                except:
                    raise UnsupportedTypeError('Unsupported apiVersion')
                nodesInfo.append(function(content, yaml))
        else:
            raise UnsupportedTypeError('Unsupported file type')
        return nodesInfo

    def _readFile(self, path: str) -> str:
        with open(path) as f:
            text = f.read()
        return text

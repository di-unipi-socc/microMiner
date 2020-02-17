import os.path
from os import path
from pathlib import Path
from ruamel.yaml import YAML

class K8SParserContext:
    
    def __init__(self):
        pass

    def parse(self, path: str):
        if os.path.exists(path):
            if path.isFile(path):
                if path.endswith('.json'):
                    pass                           
                elif path.endswith('.yml'):
                    yaml = YAML(typ='safe')
                    content = yaml.load(Path(path))
                else:
                    raise TypeError('Unsupported file')
            if path.isDir(path):
                pass

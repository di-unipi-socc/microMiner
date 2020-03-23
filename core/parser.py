from typing import Type
from ruamel.yaml import YAML
from pathlib import Path
from .errors import WrongConfigFileError

class Parser:
    
    def __init__(self):
        pass

    @classmethod
    def searchMinerStrategy(cls, strategy: str) -> dict:
        loader = YAML(typ='safe')
        strategies = loader.load(Path('miner/strategies.yml'))
        
        return strategies[strategy]

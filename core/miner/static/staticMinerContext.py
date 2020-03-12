import os.path
from pathlib import Path
from typing import Type
from .staticMiner import StaticMiner

class StaticMinerContext:

    @classmethod
    def doStaticMining(cls, config: dict, nodes: dict):
        staticMinerStrategy = cls._get_class(config['strategy'])
        staticMinerStrategy.updateTopology(config['arguments'], nodes)
    
    @classmethod
    def _get_class(cls, fqnClass: str) -> Type[StaticMiner]:
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

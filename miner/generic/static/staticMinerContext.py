import os.path
from pathlib import Path
from typing import Type
from .staticMiner import StaticMiner

class StaticMinerContext:

    @classmethod
    def doStaticMining(cls, className: str, source: str, strategyArgs: dict, nodes: dict):
        staticMinerClass = cls._get_class(className)
        staticMinerClass.updateTopology(source, strategyArgs, nodes)
    
    @classmethod
    def _get_class(cls, fqnClass: str) -> Type[StaticMiner]:
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

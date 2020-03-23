import os.path
from pathlib import Path
from typing import Type
from .dynamicMiner import DynamicMiner

class DynamicMinerContext:

    @classmethod
    def doDynamicMining(cls, className: str, source: str, strategyArgs: dict, nodes: dict):
        dynamicMinerClass = cls._get_class(className)
        dynamicMinerClass.updateTopology(source, strategyArgs, nodes)
    
    @classmethod
    def _get_class(cls, fqnClass: str) -> Type[DynamicMiner]:
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

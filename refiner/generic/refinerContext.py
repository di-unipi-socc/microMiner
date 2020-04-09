from .refiner import Refiner
from typing import Type

class RefinerContext:

    def __init__(self):
        pass

    @classmethod
    def doRefinement(cls, strategies: dict, nodes: dict):
        for strategy in strategies.values():
            refinerCls = cls._get_class(strategy['class'])
            refinerCls.recognize(nodes, strategy['args'] if 'args' in strategy else {})
    
    @classmethod
    def _get_class(cls, fqnClass: str) -> Type[Refiner]:
        parts = fqnClass.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m

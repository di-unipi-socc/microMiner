from errors import ArchMinerError

class TopologyError(ArchMinerError):
    def __init__(self, message):
        self.message = message

class NoInfoError(TopologyError):
    def __init__(self, message):
        self.message = message

class EdgeExistsError(TopologyError):
    def __init__(self, message):
        self.message = message

class EdgeNotExistsError(TopologyError):
    def __init__(self, message):
        self.message = message
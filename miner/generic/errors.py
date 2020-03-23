from errors import ArchMinerError

class StaticMinerError(ArchMinerError):
    def __init__(self, message):
        self.message = message

class DynamicMinerError(ArchMinerError):
    def __init__(self, message):
        self.message = message

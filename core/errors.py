from errors import ArchMinerError

class CoreError(ArchMinerError):
    def __init__(self, message):
        self.message = message

class WrongConfigFileError(CoreError):
    def __init__(self, message):
        self.message = message
    
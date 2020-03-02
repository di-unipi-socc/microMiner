from ...core.errors import StaticMinerError, DynamicMinerError

class WrongFolderError(StaticMinerError):
    def __init__(self, message):
        self.message = message

class K8sParserError(StaticMinerError):
    def __init__(self, message):
        self.message = message

class UnsupportedTypeError(K8sParserError):
    def __init__(self, message):
        self.message = message

class WrongFormatError(K8sParserError):
    def __init__(self, message):
        self.message = message

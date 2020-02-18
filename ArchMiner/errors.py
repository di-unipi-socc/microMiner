class ArchMinerError(Exception):
    """
    A base class from which all other exceptions inherit.
    If you want to catch all errors that the ArchMiner might raise,
    catch this base exception.
    """

class K8sParserError(ArchMinerError):
    def __init__(self, message):
        self.message = message

class UnsupportedTypeError(K8sParserError):
    def __init__(self, message):
        self.message = message

class WrongFormatError(K8sParserError):
    def __init__(self, message):
        self.message = message

class ArchMinerError(Exception):
    """
    A base class from which all other exceptions inherit.
    If you want to catch all errors that the ArchMiner might raise,
    catch this base exception.
    """

class StaticMinerError(ArchMinerError):
    def __init__(self, message):
        self.message = message

class DynamicMinerError(ArchMinerError):
    def __init__(self, message):
        self.message = message

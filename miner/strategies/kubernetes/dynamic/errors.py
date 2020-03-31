from ....generic.errors import DynamicMinerError

class WrongFolderError(DynamicMinerError):
    def __init__(self, message):
        self.message = message

class DeploymentError(DynamicMinerError):
    def __init__(self, message):
        self.message = message

class MonitoringError(DynamicMinerError):
    def __init__(self, message):
        self.message = message

class TestError(DynamicMinerError):
    def __init__(self, message):
        self.message = message

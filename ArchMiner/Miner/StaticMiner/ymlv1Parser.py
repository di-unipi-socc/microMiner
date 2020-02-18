from .k8sparser import K8sParser
from ...errors import WrongFormatError

class Ymlv1Parser(K8sParser):

    def __init__(self):
        pass
    
    @staticmethod
    def parse(content: dict) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Pod']
        try:
            if content['kind'] in workloads:
                metadata, podSpec, labels = {}, {}, {}
                containers = []
                if content['kind'] == 'Pod':
                    metadata = content['metadata']
                    podSpec = content['spec']
                    containers = _parsePod(metadata, podSpec)
                elif 'template' in content['spec']:
                    metadata = content['spec']['template']['metadata']
                    podSpec = content['spec']['template']['spec']
                    containers = _parsePod(metadata, podSpec)
                if 'labels' in metadata:
                    labels = metadata['labels']
                return {'Type': 'workload', 'Labels': labels, 'Containers': containers}
            elif content['kind'] == 'Service':
                #TO-DO
                pass
        except:
            raise WrongFormatError('')

    def _parsePod(self, metadata: dict, spec: dict) -> []:
        containers = []
        namespace = 'default'
        podName = ''
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        if 'name' in metadata:
            podName = metadata['name']
        else:
            podName = metadata['generateName']
        for container in spec['containers']:
            name = namespace + '.' + podName + '.' + container['name']
            ports = container['ports']
            containers.append({'name': name, 'ports': ports})
        return containers

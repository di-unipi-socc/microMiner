from .k8sparser import K8sParser
from ...errors import WrongFormatError

#TO-DO: Rivedere la gestione dei nomi associati ai pods in accordo al dns di K8S

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
                return {'Type': 'workload', 'Info': {'Labels': labels, 'Containers': containers}}
            elif content['kind'] == 'Service':
                svcParsedInfo = _parseService(content['metadata'], content['spec'])
                return {'Type': 'service', 'Info': svcParsedInfo}
            elif content['kind'] == 'Endpoints':
                endpointsInfo = _parseEndpoint(content['metadata'], content['spec'])
                return {'Type': 'endpoints', 'Info': endpointsInfo}
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
            ports = []
            for containerPort in container['ports']:
                port = containerPort['containerPort']
                if 'name' in containerPort:
                    portName = containerPort['name']
                else:
                    portName = ''
                ports.append({'name': portName, 'number': port})
            name = namespace + '.' + podName + '.' + container['name']
            containers.append({'name': name, 'ports': ports})
        return containers

    def _parseService(self, metadata: dict, spec: dict) -> {}:
        namespace = 'default'
        name = ''
        svcInfo = {}
        svcPorts = []
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        if 'name' in metadata:
            name = metadata['name']
        else:
            name = metadata['generateName']
        svcInfo['name'] = namespace + '.' + name
        if 'selector' in spec:
            svcInfo['selector'] = spec['selector']
        else:
            svcInfo['selector'] = {}
        for svcPort in spec['ports']:
            portInfo = {}
            if 'name' in svcPort:
                portInfo['name'] = svcPort['name']
            else:
                portInfo['name'] = ''
            if 'nodePort' in svcPort:
                portInfo['nodePort'] = svcPort['nodePort']
            portInfo['port'] = svcPort['port']
            portInfo['targetPort'] = svcPort['targetPort']
            svcPorts.append(portInfo)
        svcInfo['ports'] = svcPorts
        if 'type' in spec:
            svcInfo['type'] = spec['type']
        else:
            svcInfo['type'] = 'ClusterIP'
        return svcInfo

    def _parseEndpoint(self, metadata: dict, spec: dict) -> []:
        namespace = 'default'
        name = ''
        endpoints = []
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        if 'name' in metadata:
            name = metadata['name']
        else:
            name = metadata['generateName']
        for subset in spec['subsets']:
            for address in subset['addresses']:
                ports = []
                for port in subset['ports']:
                    ports.append(port)
                endpoints.append({'name': namespace + '.' + name + '.' + address['hostname'], 'hostname': address['hostname'], 'ip': address['ip'], 'ports': ports})
        return endpoints

import hashlib
from .k8sparser import K8sParser
from ...errors import WrongFormatError

class V1Parser(K8sParser):

    def __init__(self):
        pass

    @staticmethod
    def parse(contentDict: dict, contentStr: str) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Pod']
        try:
            if content['kind'] in workloads:
                metadata, podSpec, labels = {}, {}, {}
                containers = []
                if content['kind'] == 'Pod':
                    metadata = content['metadata']
                    podSpec = content['spec']
                    containers = _parsePod(contentStr, podSpec)
                elif 'template' in content['spec']:
                    metadata = content['spec']['template']['metadata']
                    podSpec = content['spec']['template']['spec']
                    containers = _parsePod(contentStr, podSpec)
                if 'labels' in metadata:
                    labels = metadata['labels']
                return {'Type': 'workload', 'Info': {'Labels': labels, 'Containers': containers}}
            elif content['kind'] == 'Service':
                svcParsedInfo = _parseService(content['metadata'], content['spec'])
                return {'Type': 'service', 'Info': svcParsedInfo}
            elif content['kind'] == 'Endpoints':
                endpointsInfo = _parseEndpoints(content['metadata'], content['spec'])
                return {'Type': 'endpoints', 'Info': endpointsInfo}
        except:
            raise WrongFormatError('')

    def _parsePod(self, contentStr: str, spec: dict) -> []:
        containers = []
        hostname = ''
        if 'hostname' in spec:
            hostname = spec['hostname']
        else:
            hostname = hashlib.sha256(contentStr).hexdigest()
        for container in spec['containers']:
            ports = []
            name = hostname
            for containerPort in container['ports']:
                port = containerPort['containerPort']
                if 'name' in containerPort:
                    portName = containerPort['name']
                else:
                    portName = ''
                name = name + '.' + str(port)
                ports.append({'name': portName, 'number': port})
            containers.append({'name': name, 'ports': ports})
        return containers

    def _parseService(self, metadata: dict, spec: dict) -> {}:
        namespace = 'default'
        name = ''
        svcInfo = {}
        svcPorts = []
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        #if 'name' in metadata:
        name = metadata['name']
        #Suppose for now that is impossibile for services to use generateName . (Instead how it resolve the clusterIP?)
        #else:
        #    name = metadata['generateName']
        svcInfo['name'] = name + '.' + namespace + '.svc'
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

    #How a service without selector is bounded with Endpoints? (With ports?)
    def _parseEndpoints(self, metadata: dict, spec: dict) -> []:
        endpoints = []
        for subset in spec['subsets']:
            for address in subset['addresses']:
                ports = []
                for port in subset['ports']:
                    if 'name' in port:
                        portName = port['name']
                    else:
                        portName = ''
                    ports.append({'name': portName, 'number': port['port']})
                endpoints.append({'name': address['hostname'], 'ip': address['ip'], 'ports': ports})
        return endpoints

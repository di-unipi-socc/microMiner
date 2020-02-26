import hashlib
from .k8sparser import K8sParser
from ...errors import WrongFormatError

class V1Parser(K8sParser):

    def __init__(self):
        pass

    @staticmethod
    def parse(contentDict: dict, contentStr: str) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Job', 'Pod']
        info = {}
        try:
            if content['kind'] in workloads:
                podInfo = {}
                if content['kind'] == 'Pod':
                    podInfo = _parsePod(contentStr, content['metadata'], content['spec'])
                elif 'template' in content['spec']:
                    podInfo = _parsePod(contentStr, content['spec']['template']['metadata'], content['spec']['template']['spec'])
                if podInfo:
                    info = {'Type': 'pod', 'Info': podInfo}
            elif content['kind'] == 'Service':
                svcParsedInfo = _parseService(content['metadata'], content['spec'])
                info = {'Type': 'service', 'Info': svcParsedInfo}
            elif content['kind'] == 'Endpoints':
                endpointsInfo = _parseEndpoints(content['metadata'], content['spec'])
                info = {'Type': 'endpoints', 'Info': endpointsInfo}
        except:
            raise WrongFormatError('')
        return info

    def _parsePod(self, contentStr: str, metadata: dict, spec: dict) -> {}:
        if len(spec['containers']) != 1:
            raise WrongFormatError('')
        podInfo = {}
        ports = []
        if 'labels' in metadata:
            podInfo['labels'] = metadata['labels']
        else:
            podInfo['labels'] = {}
        if 'hostname' in spec:
            podInfo['hostname'] = spec['hostname']
        else:
            podInfo['hostname'] = hashlib.sha256(contentStr).hexdigest()
        podInfo['image'] = spec['containers'][0]['image']
        for port in spec['containers'][0]['ports']:
            if 'name' in port:
                portName = port['name']
            else:
                portName = ''
            ports.append({'name': portName, 'number': port['containerPort']})
        podInfo['ports'] = ports
        return podInfo

    def _parseService(self, metadata: dict, spec: dict) -> {}:
        namespace = 'default'
        name = ''
        svcInfo = {}
        svcPorts = []
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        #Suppose for now that is impossibile for services to use generateName
        name = metadata['name']
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
            if 'targetPort' in svcPort:
                portInfo['targetPort'] = svcPort['targetPort']
            else:
                portInfo['targetPort'] = portInfo['port']
            svcPorts.append(portInfo)
        svcInfo['ports'] = svcPorts
        if 'type' in spec:
            svcInfo['type'] = spec['type']
        else:
            svcInfo['type'] = 'ClusterIP'
        return svcInfo

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

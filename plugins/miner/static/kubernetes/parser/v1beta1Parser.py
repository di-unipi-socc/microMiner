import hashlib
from .k8sParser import K8sParser
from ..errors import WrongFormatError

class V1beta1Parser(K8sParser):

    def __init__(self):
        pass

    @staticmethod
    def parse(content: dict) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'StatefulSet']
        info = {}
        try:
            if content['kind'] in workloads and 'template' in content['spec']:
                info = _parsePod(contentStr, content['spec']['template']['metadata'], content['spec']['template']['spec']) 
            elif content['kind'] == 'CronJob' and 'template' in (jobSpec := content['spec']['jobTemplate']['spec']):
                info = _parsePod(contentStr, jobSpec['template']['metadata'], jobSpec['template']['spec'])
            elif content['kind'] == 'Ingress':
                info = _parseIngress(content['metadata'], content['spec'])
        except:
            raise WrongFormatError('')
        return info
        
    def _parsePod(self, contentStr: str, metadata: dict, spec: dict) -> {}:
        if len(spec['containers']) != 1:
            raise WrongFormatError('')
        podInfo = {}
        ports = []
        name = ''
        if 'hostname' in spec:
            name = spec['hostname']
        else:
            name = hashlib.sha256(contentStr).hexdigest()
        if 'labels' in metadata:
            podInfo['labels'] = metadata['labels']
        else:
            podInfo['labels'] = {}
        podInfo['image'] = spec['containers'][0]['image']
        for port in spec['containers'][0]['ports']:
            if 'name' in port:
                portName = port['name']
            else:
                portName = ''
            ports.append({'name': portName, 'number': port['containerPort']})
        podInfo['ports'] = ports
        return {'type': 'pod', 'name': name, 'info': podInfo}

    def _parseIngress(self, metadata: dict, spec: dict) -> {}:
        ingressInfo = {}
        services = []
        namespace = 'default'
        if 'namespace' in metadata:
            namespace = metadata['namespace']
        if 'annotations' in metadata and 'kubernetes.io/ingress.class' in metadata['annotations']:
            ingressInfo['controller'] = metadata['annotations']['kubernetes.io/ingress.class']
        else:
            ingressInfo['controller'] = ''
        if 'backend' in spec:
            services.append({'serviceName': spec['backend']['serviceName'] + '.' + namespace + '.svc', 'servicePort': spec['backend']['servicePort']})
        for rule in spec['rules']:
            for path in rule['http']['paths']:
                services.append({'serviceName': path['backend']['serviceName'] + '.' + namespace + '.svc', 'servicePort': path['backend']['servicePort']})
        ingressInfo['services'] = services
        return {'type': 'ingress', 'info': ingressInfo}

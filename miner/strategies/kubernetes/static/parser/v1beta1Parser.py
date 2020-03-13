import hashlib
from .k8sParser import K8sParser
from .v1Parser import V1Parser
from ..errors import WrongFormatError

class V1beta1Parser(K8sParser):

    def __init__(self):
        pass

    @classmethod
    def parse(cls, contentDict: dict, contentStr: str) -> dict:
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'StatefulSet']
        info = {}
        try:
            if contentDict['kind'] in workloads and 'template' in contentDict['spec']:
                info = V1Parser._parsePod(contentStr, contentDict['spec']['template']['metadata'], contentDict['spec']['template']['spec']) 
            elif contentDict['kind'] == 'CronJob' and 'template' in (jobSpec := contentDict['spec']['jobTemplate']['spec']):
                info = V1Parser._parsePod(contentStr, jobSpec['template']['metadata'], jobSpec['template']['spec'])
            elif contentDict['kind'] == 'Ingress':
                info = cls._parseIngress(contentDict['metadata'], contentDict['spec'])
        except:
            raise WrongFormatError('')
        return info

    @classmethod
    def _parseIngress(cls, metadata: dict, spec: dict) -> {}:
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
            services.append({'name': spec['backend']['serviceName'] + '.' + namespace + '.svc', 'port': spec['backend']['servicePort']})
        for rule in spec['rules']:
            for path in rule['http']['paths']:
                services.append({'name': path['backend']['serviceName'] + '.' + namespace + '.svc', 'port': path['backend']['servicePort']})
        ingressInfo['services'] = services
        return {'type': 'ingress', 'info': ingressInfo}

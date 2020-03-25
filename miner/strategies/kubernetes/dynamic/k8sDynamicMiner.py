from miner.generic.dynamic.dynamicMiner import DynamicMiner
from .errors import WrongFolderError, DeploymentError
from os.path import isdir, isfile, join, exists
from kubernetes import client, config, utils
from os import listdir
from ruamel import yaml
from ruamel.yaml import YAML
from pathlib import Path
import hashlib
import os

class K8sDynamicMiner(DynamicMiner):

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        config.load_kube_config()
        k8sClient = client.ApiClient()
        loader = YAML(typ='safe')
        files = cls._listFiles(source)
        for k8sFile in files:
            yamls = cls._readFile(k8sFile).split('---')
            for yaml in yamls:
                contentDict = loader.load(yaml)
                cls._prepareYaml(yaml, contentDict, info['monitoringContainer'], info['time'])
                try:
                    utils.create_from_dict(k8sClient, contentDict)
                except utils.FailToCreateError:
                    raise DeploymentError('Error deploying ' + 'k8sFile')
        
        '''
        Bisogna tenere in considerazione il tempo necessario a Kubernetes 
        perchè tutti i pod siano in esecuzione. Infatti il monitoring inizia
        nel momento in cui il pod viene eseguito. Momento in cui non necessariamente
        tutti i pod sono già in esecuzione e l'applicazione è pronta per eseguire i test
        e generare traffico. Una possibile soluzione è quella di verificare lo stato 
        dei pod tramite la client library e appena tutti i pod sono in esecuzione,
        far partire il monitoring, sempre tramite client library, per un certo periodo di tempo 
        ed infine eseguire i tests. Il problema di questo approccio è che tali richieste richiedono
        autenticazione.
        Un'altra soluzione è eseguire il monitoring per un tempo abbastanza lungo, che includa
        tutto il tempo necessario a Kubernetes per eseguire tutti i pods e affinchè possa essere generato
        abbastanza traffico. In tal caso, il test andrebbe eseguito dopo un pò, altrimenti il test 
        fallirebbe perchè l'app non sarebbe del tutto in esecuzione.
        '''


    @classmethod
    def _readFile(cls, path: str) -> str:
        with open(path) as f:
            text = f.read()
        return text

    @classmethod
    def _listFiles(cls, folderPath: str) -> []:
        if not exists(Path(folderPath)) or not isdir(Path(folderPath)):
            raise WrongFolderError('')
        return [join(folderPath, f) for f in listdir(folderPath) if isfile(join(folderPath, f))]

    @classmethod
    def _prepareYaml(cls, contentStr: str, contentDict: dict, imageName: str, time: int):
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Job']

        if contentDict['kind'] in workloads and 'template' in contentDict['spec']:
            podSpec = contentDict['spec']['template']['spec']
        elif contentDict['kind'] == 'CronJob' and 'template' in (jobSpec := contentDict['spec']['jobTemplate']['spec']):
            podSpec = jobSpec['template']['spec']
        elif contentDict['kind'] == 'Pod':
            podSpec = contentDict['spec']

        if not 'hostname' in podSpec:
            podSpec['hostname'] = hashlib.sha256(contentStr.encode('utf-8')).hexdigest()

        filePath = join('/home/path', imageName)
        podSpec['containers'].append({'image': imageName, 'command': ['timeout', str(time), 'tcpdump', '-w', filePath]})

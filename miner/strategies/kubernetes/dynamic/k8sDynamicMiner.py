from miner.generic.dynamic.dynamicMiner import DynamicMiner
from .errors import WrongFolderError, DeploymentError, MonitoringError, TestError
from os.path import isdir, isfile, join, exists
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from os import listdir
from ruamel import yaml
from ruamel.yaml import YAML
from pathlib import Path
import importlib
import hashlib
import time
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
                cls._prepareYaml(yaml, contentDict, info['monitoringContainer'])
                try:
                    utils.create_from_dict(k8sClient, contentDict)
                except utils.FailToCreateError:
                    raise DeploymentError('Error deploying ' + 'k8sFile')
        
        v1 = client.CoreV1Api()
        deploymentCompleted = False

        while not deploymentCompleted:
            pods = v1.list_pod_for_all_namespaces(watch = False)
            deploymentCompleted = True
            for pod in pods.items:
                if pod.status.phase != 'Running' or pod.status.phase != 'Succeeded':
                    deploymentCompleted = False
                    break
            if not deploymentCompleted:
                time.sleep(10)
            
        pods = v1.list_pod_for_all_namespaces(watch = False)
        containerName = ''.join(c for c in info['monitoringContainer'] if c.isalnum())

        for pod in pods.items:
            filePath = join('/home/path', pod.metadata.name + '-' + containerName + '.json')
            command = [
                        '/bin/sh',
                        '-c',
                        'tshark -a duration:' + str(info['time']) + ' -N nNdt -T json > ' + filePath]
            try:
                v1.connect_get_namespaced_pod_exec(
                                                    pod.metadata.name, 
                                                    pod.metadata.namespace, 
                                                    command = command, 
                                                    container = containerName,
                                                    stderr=True, stdin=False,
                                                    stdout=True, tty=False)
            except ApiException as e:
                raise MonitoringError(pod.metadata.name)

        try:
            testModule = importlib.import_module(info['test'])
            testModule.runTest()
        except:
            raise TestError('')

        time.sleep(info['time'])

        pods = v1.list_pod_for_all_namespaces(watch = False)
        for pod in pods.items:
            filePath = join('/home/path', pod.metadata.name + '-' + containerName + '.json')
            os.system('kubectl cp ' + pod.metadata.namespace + '/' + pod.metadata.name + ':' +  filePath + ' ' + info['monitoringFiles'])


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
    def _prepareYaml(cls, contentStr: str, contentDict: dict, imageName: str):
        workloads = ['Deployment', 'ReplicaSet', 'DaemonSet', 'ReplicationController', 'StatefulSet', 'Job']

        if contentDict['kind'] in workloads and 'template' in contentDict['spec']:
            podSpec = contentDict['spec']['template']['spec']
        elif contentDict['kind'] == 'CronJob' and 'template' in (jobSpec := contentDict['spec']['jobTemplate']['spec']):
            podSpec = jobSpec['template']['spec']
        elif contentDict['kind'] == 'Pod':
            podSpec = contentDict['spec']

        if not 'hostname' in podSpec:
            podSpec['hostname'] = hashlib.sha256(contentStr.encode('utf-8')).hexdigest()

        podSpec['containers'].append({'name': ''.join(c for c in imageName if c.isalnum()), 'image': imageName})

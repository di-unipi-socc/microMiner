from miner.generic.dynamic.dynamicMiner import DynamicMiner
from topology.node import Node, Direction
from topology.communication import Communication
from topology.concreteCommunicationFactory import ConcreteCommunicationFactory
from .errors import WrongFolderError, DeploymentError, MonitoringError, TestError
from os.path import isdir, isfile, join, exists
from kubernetes import client, config, utils
from kubernetes.client.rest import ApiException
from os import listdir
from ruamel import yaml
from ruamel.yaml import YAML
from pathlib import Path
import importlib
import json
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
        newDeploymentPath = join(source, 'deploymentNew')
        os.makedirs(newDeploymentPath)
        
        #Deployment of the application
        for k8sFile in files:
            yamls = cls._readFile(k8sFile).split('---')
            i = 0
            for contentStr in yamls:
                contentDict = loader.load(contentStr)
                cls._prepareYaml(contentStr, contentDict, info['monitoringContainer'])
                try:
                    utils.create_from_dict(k8sClient, contentDict)
                except utils.FailToCreateError:
                    raise DeploymentError('Error deploying ' + k8sFile)
                with open(join(newDeploymentPath, str(i) + '.yml'), 'w') as f:
                    yamlContent = yaml.dump(contentDict)
                    f.write(yamlContent)
                i = i + 1
        
        #Wait until the deployment is completed
        v1 = client.CoreV1Api()
        deploymentCompleted = False

        while not deploymentCompleted:
            pods = v1.list_pod_for_all_namespaces(watch = False)
            deploymentCompleted = True
            for pod in pods.items:
                if pod.spec.hostname in nodes:
                    if pod.status.phase != 'Running' and pod.status.phase != 'Succeeded':
                        deploymentCompleted = False
                        break
            if not deploymentCompleted:
                time.sleep(3)

        #Start monitoring   
        pods = v1.list_pod_for_all_namespaces(watch = False)
        containerName = ''.join(c for c in info['monitoringContainer'] if c.isalnum())

        for pod in pods.items:
            if pod.spec.hostname in nodes:
                filePath = join('/home/path', pod.metadata.name + '-' + containerName + '.json')
                command = [
                            './bin/sh',
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
        
        #Start tests
        if info['test']:
            try:
                testModule = importlib.import_module(info['test'])
                testModule.runTest()
            except:
                raise TestError('')
        
        #Wait until monitoring is finished
        time.sleep(info['time'])

        #Save on local host the packets
        pods = v1.list_pod_for_all_namespaces(watch = False)
        for pod in pods.items:
            if pod.spec.hostname in nodes:
                remoteFilePath = join('/home/path', pod.metadata.name + '-' + containerName + '.json')
                localFilePath = join(info['monitoringFiles'], pod.metadata.name + '-' + containerName + '.json')
                os.system('kubectl cp -c ' + containerName + ' ' + pod.metadata.namespace + '/' + pod.metadata.name + ':' + remoteFilePath + ' ' + localFilePath)

        #Clean the environment
        files = cls._listFiles(newDeploymentPath)
        for yamlFile in files:
            os.system('kubectl delete -f ' + yamlFile)

        #Analyze the packet
        commFactory = ConcreteCommunicationFactory()
        files = cls._listFiles(info['monitoringFiles'])
        for monitoringFile in files:
            packetList = json.loads(cls._readFile(monitoringFile))
            for packet in packetList:
                cls._analyzePacket(packet, nodes, commFactory)
                

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
        
        podSpec = {}
        if contentDict['kind'] in workloads and 'template' in contentDict['spec']:
            podSpec = contentDict['spec']['template']['spec']
        elif contentDict['kind'] == 'CronJob' and 'template' in (jobSpec := contentDict['spec']['jobTemplate']['spec']):
            podSpec = jobSpec['template']['spec']
        elif contentDict['kind'] == 'Pod':
            podSpec = contentDict['spec']
        
        if podSpec:
            if not 'hostname' in podSpec:
                podSpec['hostname'] = hashlib.sha1(contentStr.encode('utf-8')).hexdigest()
            podSpec['containers'].append({'name': ''.join(c for c in imageName if c.isalnum()), 'image': imageName})

    @classmethod
    def _analyzePacket(cls, packet: dict, nodes: dict, commFactory):
        packetLayers = packet['_source']['layers']
        srcNode, dstNode = None, None
        srcNodeName = packetLayers['ip']['ip.src_host']
        if 'svc' in srcNodeName.split('.'):
            srcNodeName = srcNodeName.split('svc')[0] + 'svc'
        srcNode = nodes[srcNodeName]
        dstNodeName = packetLayers['ip']['ip.dst_host']
        if 'svc' in dstNodeName.split('.'):
            dstNodeName = dstNodeName.split('svc')[0] + 'svc' 
        dstNode = nodes[dstNodeName]
        if 'tcp' in packetLayers and packetLayers['tcp']['tcp.flags_tree']['tcp.flags.syn'] == '1':
            srcNode.addEdge(dstNodeName, Direction.OUTGOING)
            dstNode.addEdge(srcNodeName, Direction.INCOMING)

        communication = commFactory.build(packet)
        if communication:
            srcNode.addCommunication(dstNodeName, communication, Direction.OUTGOING)
            dstNode.addCommunication(srcNodeName, communication, Direction.INCOMING)

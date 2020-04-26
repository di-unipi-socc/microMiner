from miner.generic.dynamic.dynamicMiner import DynamicMiner
from topology.node import Node, Direction
from topology.communication import Communication
from topology.communicationFactory import CommunicationFactory
from topology.concreteCommunicationFactory import ConcreteCommunicationFactory
from topology.microToscaTypes import NodeType
from topology.errors import EdgeExistsError, EdgeNotExistsError
from .errors import WrongFolderError, DeploymentError, MonitoringError, TestError
from os.path import isdir, isfile, join, exists
from kubernetes import client, config, utils
from kubernetes.client import configuration
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from os import listdir
from ruamel import yaml
from ruamel.yaml import YAML
from pathlib import Path
from typing import Type
import logging
import copy
import shutil
import importlib
import ijson.backends.yajl2_c as ijson
import hashlib
import time
import os

class K8sDynamicMiner(DynamicMiner):

    log = logging.getLogger(__name__)
    packetToPodHosts = {}

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        config.load_kube_config()
        configuration.assert_hostname = False
        k8sClient = client.ApiClient()
        loader = YAML(typ='safe')
        files = cls._listFiles(source)
        
        try:
            #Deployment of the application
            print('   Deploying the application...')
            for k8sFile in files:
                yamls = cls._readFile(k8sFile).split('---')
                i = 0
                for contentStr in yamls:
                    contentDict = loader.load(contentStr)
                    cls._prepareYaml(contentStr, contentDict, info['monitoringContainer'])
                    with open(join(info['modDeploymentFiles'], str(i) + '.yml'), 'w') as f:
                        try: 
                            f.write(yaml.dump(contentDict))
                            utils.create_from_dict(k8sClient, contentDict)
                        except utils.FailToCreateError:
                            cls._cleanEnvironment(info['modDeploymentFiles'], info['monitoringFiles'])
                            raise DeploymentError('Error deploying ' + k8sFile)
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
            time.sleep(10)
            print('   Deployment completed')        

            #Start monitoring
            print('   Monitoring in progress...')   
            pods = v1.list_pod_for_all_namespaces(watch = False)
            containerName = ''.join(c for c in info['monitoringContainer'] if c.isalnum())
            for pod in pods.items:
                if pod.spec.hostname in nodes:
                    filePath = join('/home/dump', pod.spec.hostname + '.json')
                    command = [
                                './bin/sh',
                                '-c',
                                'tshark -i eth0 -a duration:' + str(info['time'] + 3) + ' -N nNdt -T json > ' + filePath + ' 2>/dev/null &']
                    try:
                        resp = stream(v1.connect_get_namespaced_pod_exec,
                                                            pod.metadata.name, 
                                                            pod.metadata.namespace, 
                                                            command = command, 
                                                            container = containerName,
                                                            stderr=False, stdin=False,
                                                            stdout=True, tty=False)
                    except ApiException as e:
                        cls._cleanEnvironment(info['modDeploymentFiles'], info['monitoringFiles'])
                        raise MonitoringError(pod.metadata.name)
            
            #Start tests
            time.sleep(3)
            if info['test']:
                try:
                    testModule = importlib.import_module(info['test'])
                    testModule.runTest()
                except:
                    cls._cleanEnvironment(info['modDeploymentFiles'], info['monitoringFiles'])
                    raise TestError('')
            
            #Wait until monitoring is finished
            time.sleep(info['time'])
            print('   Monitoring completed')

            #Save on local host the packets
            pods = v1.list_pod_for_all_namespaces(watch = False)
            for pod in pods.items:
                if pod.spec.hostname in nodes:
                    remoteFilePath = join('home/dump', pod.spec.hostname + '.json')
                    localFilePath = join(info['monitoringFiles'], pod.spec.hostname + '.json')
                    os.system('kubectl cp -c ' + containerName + ' ' + pod.metadata.namespace + '/' + pod.metadata.name + ':' + remoteFilePath + ' ' + localFilePath)
            
            #Create edges
            print('   Analyzing packets...')
            try:
                files = cls._listFiles(info['monitoringFiles'])
            except WrongFolderError:
                cls._cleanEnvironment(info['modDeploymentFiles'], info['monitoringFiles'])
                raise
            for monitoringFilePath in files:
                srcNodeName = monitoringFilePath.split('/')[-1].replace('.json', '')
                with open(monitoringFilePath, 'rb') as monitoringFile:
                    for packet in ijson.items(monitoringFile, 'item'):
                        if cls._isOutgoingPacket(packet, nodes, srcNodeName):
                            cls._createEdge(packet, nodes, srcNodeName)
            
            #Create communications
            commFactory = ConcreteCommunicationFactory()
            for monitoringFilePath in files:
                srcNodeName = monitoringFilePath.split('/')[-1].replace('.json', '')
                with open(monitoringFilePath, 'rb') as monitoringFile:
                    for packet in ijson.items(monitoringFile, 'item'):
                        if cls._isOutgoingPacket(packet, nodes, srcNodeName):
                            cls._createCommunication(packet, nodes, commFactory, srcNodeName)
        finally:
            cls._cleanEnvironment(info['modDeploymentFiles'], info['monitoringFiles'])
        

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
            cls.log.info(contentDict['metadata']['name'] + ':' + podSpec['hostname'])
            podSpec['containers'].append({'name': ''.join(c for c in imageName if c.isalnum()), 'image': imageName})

    @classmethod
    def _isOutgoingPacket(cls, packet: dict, nodes: dict, srcNodeName: str) -> bool:
        packetLayers = packet['_source']['layers']
        if not 'ip' in packetLayers:
            return False
        packetSrc = packetLayers['ip']['ip.src_host']
        if 'svc' in packetSrc.split('.'):
            return False
        if packetSrc != srcNodeName:
            return False
        
        return True

    @classmethod
    def _getPodHostname(cls, ip: str, host: str) -> str:
        if host in cls.packetToPodHosts:
            return cls.packetToPodHosts[host]
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch = False)
        for pod in pods.items:
            if pod.status.pod_ip == ip:
                cls.packetToPodHosts[host] = pod.spec.hostname
                return pod.spec.hostname
        return ''

    @classmethod
    def _getDstNode(cls, packet: dict, nodes: dict) -> (str, Node):
        packetLayers = packet['_source']['layers']
        if not 'ip' in packetLayers:
            return ('', None)
        dstNodeName = packetLayers['ip']['ip.dst_host']
        if 'svc' in dstNodeName.split('.'):
            dstNodeName = dstNodeName.split('.svc.')[0] + '.svc'
        if not dstNodeName in nodes:
            dstNodeName = cls._getPodHostname(packetLayers['ip']['ip.dst'], dstNodeName)
        if not dstNodeName in nodes:
            return ('', None)

        return (dstNodeName, nodes[dstNodeName])

    @classmethod
    def _createEdge(cls, packet: dict, nodes: dict, srcNodeName: str):
        packetLayers = packet['_source']['layers']
        srcNode = nodes[srcNodeName]
        dst = cls._getDstNode(packet, nodes)
        dstNodeName = dst[0]
        dstNode = dst[1]
        if not dstNodeName:
            return
        dstIsService = dstNode.getType() == NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER
        if ('tcp' in packetLayers and packetLayers['tcp']['tcp.flags_tree']['tcp.flags.syn'] == '1' and packetLayers['tcp']['tcp.flags_tree']['tcp.flags.ack'] == '0') or (dstIsService):
            try:
                srcNode.addEdge(dstNodeName, Direction.OUTGOING)
                dstNode.addEdge(srcNodeName, Direction.INCOMING)
            except EdgeExistsError:
                srcNode.setIsMicroToscaEdge(dstNodeName, True)
        if dstIsService:
            edges = dstNode.getEdges(Direction.OUTGOING)
            for adjacentName in edges.keys():
                if nodes[adjacentName].getType() == NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER:
                    continue
                try:
                    nodes[adjacentName].addEdge(srcNodeName, Direction.OUTGOING, isMicroToscaEdge = False)
                    srcNode.addEdge(adjacentName, Direction.INCOMING)
                except EdgeExistsError:
                    pass

    @classmethod
    def _createCommunication(cls, packet: dict, nodes: dict, commFactory: Type[CommunicationFactory], srcNodeName: str):
        srcNode = nodes[srcNodeName]
        dst = cls._getDstNode(packet, nodes)
        dstNodeName = dst[0]
        dstNode = dst[1]
        if not dstNodeName:
            return
        packet['_source']['layers']['ip']['ip.dst_host'] = dstNodeName
        dstIsService = dstNode.getType() == NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER
        communication = commFactory.build(copy.deepcopy(packet))
        if communication:
            try:
                srcNode.addCommunication(dstNodeName, communication)
                dstNode.addCommunication(srcNodeName, communication)
            except EdgeNotExistsError:
                cls.log.warn('Edge (' + srcNodeName + ', ' + dstNodeName + ') not exists')
                pass
        
        if dstIsService:
            packet['_source']['layers']['ip']['ip.src_host'] = dstNodeName
            edges = dstNode.getEdges(Direction.OUTGOING)
            for adjacentName in edges.keys():
                packet['_source']['layers']['ip']['ip.dst_host'] = adjacentName
                communication = commFactory.build(copy.deepcopy(packet))
                if communication:
                    dstNode.addCommunication(adjacentName, communication)
                    nodes[adjacentName].addCommunication(dstNodeName, communication)
    
    @classmethod
    def _cleanEnvironment(cls, modDeploymentFiles: str, monitoringFiles: str):
        files = cls._listFiles(modDeploymentFiles)
        for yamlFile in files:
            os.system('kubectl delete -f ' + yamlFile + ' 1>/dev/null 2>/dev/null')
            os.remove(yamlFile)
        files = cls._listFiles(monitoringFiles)
        for monitoringFile in files:
            os.remove(monitoringFile)

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
import json
import time
import os
import re

class K8sDynamicMiner(DynamicMiner):

    log = logging.getLogger(__name__)
    config = {}
    packetToPodHosts = {}
    controllers = []

    def __init__(self):
        pass

    @classmethod
    def updateTopology(cls, source: str, info: dict, nodes: dict):
        cls.config = info
        config.load_kube_config()
        configuration.assert_hostname = False
        k8sClient = client.ApiClient()
        loader = YAML(typ='safe')
        files = cls._listFiles(source)
        newNodes = []
        try:
            #Search ingress controller already deployed
            cls.controllers = cls._searchIngressControllers()
            for controller in cls.controllers:
                newNode = cls._addControllerToTopology(controller, nodes)
                if newNode:
                    newNodes.append(newNode)
                else:
                    cls.controllers.remove(controller)
            #Deployment of the application
            print('   Deploying the application...')
            i = 0
            for k8sFile in files:
                yamls = re.split('^---\n', cls._readFile(k8sFile), flags=re.MULTILINE)
                for contentStr in yamls:
                    contentDict = loader.load(contentStr)
                    if not contentDict:
                        continue
                    cls._prepareYaml(contentStr, contentDict)
                    with open(join(cls.config['modDeploymentFiles'], str(i) + '.yml'), 'w') as f:
                        try:
                            f.write(yaml.dump(contentDict))
                            utils.create_from_dict(k8sClient, contentDict)
                        except utils.FailToCreateError:
                            cls._cleanEnvironment()
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
                        for containerStatus in pod.status.container_statuses:
                            if not containerStatus.ready:
                                deploymentCompleted = False
                                break
                    if not deploymentCompleted:
                        break
                if not deploymentCompleted:
                    time.sleep(3)
            print('   Deployment completed')

            #Start monitoring
            print('   Monitoring in progress...')   
            pods = v1.list_pod_for_all_namespaces(watch = False)
            containerName = ''.join(c for c in cls.config['monitoringContainer'] if c.isalnum())
            for pod in pods.items:
                if pod.spec.hostname in nodes or pod.status.pod_ip in nodes:
                    fileName = pod.spec.hostname if pod.spec.hostname else pod.status.pod_ip
                    filePath = join('/home/dump', fileName + '.json')
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
                        cls._cleanEnvironment()
                        raise MonitoringError(pod.metadata.name)
            
            #Start tests
            time.sleep(3)
            if info['test']:
                try:
                    testModule = importlib.import_module(info['test'])
                    testModule.runTest()
                except:
                    cls._cleanEnvironment()
                    raise TestError('')
            
            #Wait until monitoring is finished
            time.sleep(info['time'])
            print('   Monitoring completed')

            #Save on local host the packets
            pods = v1.list_pod_for_all_namespaces(watch = False)
            for pod in pods.items:
                if pod.spec.hostname in nodes or pod.status.pod_ip in nodes:
                    fileName = pod.spec.hostname if pod.spec.hostname else pod.status.pod_ip
                    remoteFilePath = join('home/dump', fileName + '.json')
                    localFilePath = join(cls.config['monitoringFiles'], fileName + '.json')
                    os.system('kubectl cp -c ' + containerName + ' ' + pod.metadata.namespace + '/' + pod.metadata.name + ':' + remoteFilePath + ' ' + localFilePath)
            
            #Create edges
            print('   Analyzing packets...')
            try:
                files = cls._listFiles(cls.config['monitoringFiles'])
            except WrongFolderError:
                cls._cleanEnvironment()
                raise
            for monitoringFilePath in files:
                if os.path.getsize(monitoringFilePath) == 0:
                    continue
                srcNodeName = monitoringFilePath.split('/')[-1].replace('.json', '')
                with open(monitoringFilePath, 'rb') as monitoringFile:
                    for packet in ijson.items(monitoringFile, 'item'):
                        if cls._isOutgoingPacket(packet, nodes, srcNodeName):
                            cls._createEdge(packet, nodes, srcNodeName)
            
            #Create communications
            commFactory = ConcreteCommunicationFactory()
            for monitoringFilePath in files:
                if os.path.getsize(monitoringFilePath) == 0:
                    continue
                srcNodeName = monitoringFilePath.split('/')[-1].replace('.json', '')
                with open(monitoringFilePath, 'rb') as monitoringFile:
                    for packet in ijson.items(monitoringFile, 'item'):
                        if cls._isOutgoingPacket(packet, nodes, srcNodeName):
                            cls._createCommunication(packet, nodes, commFactory, srcNodeName)
            
            for newNode in newNodes:
                edges = nodes[newNode['controller']].getEdges(Direction.OUTGOING)
                if not edges:
                    nodes.pop(newNode['controller'], None)
                    for service in newNode['services']:
                        nodes.pop(service, None)

        finally:
            cls._cleanEnvironment()
        

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
    def _prepareYaml(cls, contentStr: str, contentDict: dict):
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
            podSpec['containers'].append({'name': ''.join(c for c in cls.config['monitoringContainer'] if c.isalnum()), 'image': cls.config['monitoringContainer']})

    @classmethod
    def _isOutgoingPacket(cls, packet: dict, nodes: dict, srcNodeName: str) -> bool:
        packetLayers = packet['_source']['layers']
        if not 'ip' in packetLayers:
            return False
        packetSrc = packetLayers['ip']['ip.src_host']
        if 'svc' in packetSrc.split('.'):
            return False
        if packetSrc != srcNodeName:
            packetSrc = packetLayers['ip']['ip.src']
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
            dstNodeName = packetLayers['ip']['ip.dst']
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
        dstIsService = '.svc.' in dstNodeName
        if ('tcp' in packetLayers and packetLayers['tcp']['tcp.flags_tree']['tcp.flags.syn'] == '1' and packetLayers['tcp']['tcp.flags_tree']['tcp.flags.ack'] == '0') or (dstIsService):
            try:
                srcNode.addEdge(dstNodeName, Direction.OUTGOING)
                dstNode.addEdge(srcNodeName, Direction.INCOMING)
            except EdgeExistsError:
                srcNode.setIsMicroToscaEdge(dstNodeName, True)
        if dstIsService:
            edges = dstNode.getEdges(Direction.OUTGOING)
            for adjacentName in edges.keys():
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
        dstIsService = '.svc.' in dstNodeName
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
    def _cleanEnvironment(cls):
        files = cls._listFiles(cls.config['modDeploymentFiles'])
        for yamlFile in files:
            os.system('kubectl delete -f ' + yamlFile + ' 1>/dev/null 2>/dev/null')
            os.remove(yamlFile)
        files = cls._listFiles(cls.config['monitoringFiles'])
        for monitoringFile in files:
            os.remove(monitoringFile)
        for controller in cls.controllers:
            os.system('kubectl delete pod -n ' + controller.metadata.namespace + ' ' + controller.metadata.name + ' 1>/dev/null 2>/dev/null')
    
    @classmethod
    def _searchIngressControllers(cls):
        loader = YAML(typ='safe')
        controllerImages = loader.load(Path(cls.config['controllerImages']))['INGRESS-CONTROLLERS']
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch = False)
        controllers = []
        for pod in pods.items:
            if pod.status.phase != 'Running':
                continue
            for container in pod.spec.containers:
                containerImage = re.sub(':.*', '', container.image)
                found = False
                for controllerImage in controllerImages:
                    if controllerImage == containerImage:
                        found = True
                        controllers.append(pod)
                        break
                if found:
                    break
        
        return controllers

    @classmethod
    def _addControllerToTopology(cls, controller, nodes: dict) -> []:
        isController = False
        serviceNodes = []
        if controller.spec.host_network:
            isController = True
        
        if not isController:
            labels = controller.metadata.labels
            v1 = client.CoreV1Api()
            services = v1.list_service_for_all_namespaces()
            for service in services.items:
                if service.spec.type == 'NodePort' or service.spec.type == 'LoadBalancer':
                    for key1, value1 in service.spec.selector.items():
                        found = False
                        for key2, value2 in labels.items():
                            if key1 == key2 and value1 == value2:
                                found = True
                                break
                        if not found:
                            break
                    if found:
                        serviceNodes.append(service)
                        isController = True

        newNodes = {}
        if isController:
            hostname = cls._prepareController(controller)
            namespace = controller.metadata.namespace if controller.metadata.namespace else 'default'
            controllerNode = Node(controller.metadata.name + '.' + namespace, {})
            nodes[hostname] = controllerNode
            controllerNode.setType(NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER)
            controllerNode.setIsEdge(True)
            newNodes['services'] = []
            for serviceNode in serviceNodes:
                namespace = serviceNode.metadata.namespace if serviceNode.metadata.namespace else 'default'
                serviceName = serviceNode.metadata.name + '.' + serviceNode.metadata.namespace + '.svc'
                service = Node(serviceName, {})
                nodes[serviceName] = service
                service.setType(NodeType.MICROTOSCA_NODES_MESSAGE_ROUTER)
                service.setIsEdge(True)
                controllerNode.addEdge(serviceName, Direction.INCOMING)
                nodes[serviceName].addEdge(hostname, Direction.OUTGOING)
                newNodes['services'].append(serviceName)
            newNodes['controller'] = hostname
        
        return newNodes
            

    @classmethod
    def _prepareController(cls, controller):
        if controller.spec.hostname:
            controllerName = controller.spec.hostname
        else:
            controllerName = controller.status.pod_ip
        namespace = 'default'
        if controller.metadata.namespace:
            namespace = controller.metadata.namespace
        ephemeralContainer = {
            'apiVersion': 'v1',
            'kind': 'EphemeralContainers',
            'metadata':
            {
                'name': controller.metadata.name,
                'namespace': controller.metadata.namespace if controller.metadata.namespace else 'default'
            },
            'ephemeralContainers':
                [
                    {
                        'name': ''.join(c for c in cls.config['monitoringContainer'] if c.isalnum()),
                        'image': cls.config['monitoringContainer'],
                        'imagePullPolicy': 'IfNotPresent',
                        'terminationMessagePolicy': 'File'
                    }
                ]
        }
        with open(join(cls.config['modDeploymentFiles'], 'ec.json'), 'w') as f:
            jsonContent = json.dumps(ephemeralContainer)
            f.write(jsonContent)
        os.system('kubectl replace --raw /api/v1/namespaces/' + namespace + '/pods/' + controller.metadata.name + '/ephemeralcontainers -f ' + cls.config['modDeploymentFiles'] + '/ec.json 1>/dev/null 2>/dev/null')
        os.remove(join(cls.config['modDeploymentFiles'], 'ec.json'))
        return controllerName

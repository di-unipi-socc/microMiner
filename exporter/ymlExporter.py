from .exporter import Exporter
from topology.node import Node, Direction
from topology.microToscaTypes import NodeType, RelationshipProperty
from ruamel import yaml
from typing import List, Optional

class YMLExporter(Exporter):

    def __init__(self):
        pass

    @classmethod
    def export(cls, topology: dict, path: str, modelName: Optional[str] = 'Generic application'):
        with open(path, 'w') as f:
            yamlContent = yaml.dump(cls._toDict(topology, modelName))
            f.write(yamlContent)

    @classmethod
    def _toDict(cls, topology: dict, modelName: str) -> dict:

        ymlDict = cls._getMetadata(modelName)
        topologyTemplate = {}

        nodeTemplates = {}
        edgeNodes = []
        for node in topology.values():
            nodeName = node.getFrontendName()
            microToscaNode = {}
            microToscaNode['type'] = node.getType().value
            microToscaNode['requirements'] = []
            requirements = node.getEdges(Direction.OUTGOING)
            for requirementName, requirement in requirements.items():
                requirementNodeName = topology[requirementName].getFrontendName()
                if not requirement['properties']:
                    microToscaNode['requirements'].append({'interaction': requirementNodeName})
                else:
                    microToscaNode['requirements'].append({'interaction': {'node': requirementNodeName, 'relationship': cls._buildYmlRelationshipProperty(requirement['properties'])}})
            if node.getIsEdge():
                edgeNodes.append(nodeName)
            nodeTemplates[nodeName] = microToscaNode 
        topologyTemplate['node_templates'] = nodeTemplates

        edgeTemplate = {}
        if edgeNodes:
            edgeTemplate['edge'] = {'type': 'micro.groups.Edge', 'members': edgeNodes}
        topologyTemplate['groups'] = edgeTemplate

        topologyTemplate['relationship_templates'] = cls._buildRelationshipTemplates()

        ymlDict['topology_template'] = topologyTemplate

        return ymlDict

    @classmethod
    def _getMetadata(cls, modelName, version="1.1"):
        metadata = dict(tosca_definitions_version=f"micro_tosca_yaml_{version}", 
                          description=modelName,
                          imports=[{"micro": f"https://di-unipi-socc.github.io/microTOSCA/{version}/microTOSCA.yaml"}])
        return metadata
    
    @classmethod
    def _buildYmlRelationshipProperty(cls, relationshipProperties) -> str:
        isTimeout, isCircuitBreaker, isDynamicDiscovery = False, False, False
        for relationshipProperty in relationshipProperties:
            if relationshipProperty == RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY:
                isTimeout = True
            elif relationshipProperty == RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY:
                isCircuitBreaker = True
            elif relationshipProperty == RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY:
                isDynamicDiscovery = True
        
        ymlRelationship = ''
        if isTimeout and not isCircuitBreaker and not isDynamicDiscovery:
            ymlRelationship = 't'
        elif not isTimeout and isCircuitBreaker and not isDynamicDiscovery:
            ymlRelationship = 'c'
        elif not isTimeout and not isCircuitBreaker and isDynamicDiscovery:
            ymlRelationship = 'd'
        elif isTimeout and isCircuitBreaker and not isDynamicDiscovery:
            ymlRelationship = 'tc'
        elif isTimeout and not isCircuitBreaker and isDynamicDiscovery:
            ymlRelationship = 'td'
        elif not isTimeout and isCircuitBreaker and isDynamicDiscovery:
            ymlRelationship = 'cd'
        elif isTimeout and isCircuitBreaker and isDynamicDiscovery:
            ymlRelationship = 'tcd'

        return ymlRelationship

    @classmethod
    def _buildRelationshipTemplates(cls):
        relTempl = {}
        relTempl['t'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY.value: True}}
        relTempl['c'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY.value: True}}
        relTempl['d'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY.value: True}}
        relTempl['tc'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY.value: True, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY.value: True}}
        relTempl['td'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY.value: True, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY.value: True}}
        relTempl['cd'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY.value: True, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY.value: True}}
        relTempl['tcd'] = {"type": RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH.value, "properties": {RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY.value: True, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY.value: True, RelationshipProperty.MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY.value: True}}
        return relTempl

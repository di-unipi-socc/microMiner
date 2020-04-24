from enum import Enum

class NodeType(Enum):
    
    MICROTOSCA_NODES_SERVICE = 'micro.nodes.Service'
    MICROTOSCA_NODES_DATABASE = 'micro.nodes.Datastore'

    MICROTOSCA_NODES_MESSAGE_BROKER = 'micro.nodes.MessageBroker'
    MICROTOSCA_NODES_MESSAGE_ROUTER = 'micro.nodes.MessageRouter'

class RelationshipProperty(Enum):

    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH = 'micro.relationships.InteractsWith'
    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY = "timeout"
    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY = "circuit_breaker"
    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY = "dynamic_discovery"

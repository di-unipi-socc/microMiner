from enum import Enum

class NodeType(Enum):
    
    MICROTOSCA_NODES_SERVICE = 'micro.nodes.Service'
    MICROTOSCA_NODES_DATABASE = 'micro.nodes.Datastore'

    MICROTOSCA_NODES_MESSAGE_BROKER = 'micro.nodes.MessageBroker'
    MICROTOSCA_NODES_MESSAGE_ROUTER = 'micro.nodes.MessageRouter'

    MICROTOSCA_NODES_MESSAGE_ROUTER_KINGRESS = 'micro.nodes.MessageRouter.KIngress'
    MICROTOSCA_NODES_MESSAGE_ROUTER_KSERVICE = 'micro.nodes.MessageRouter.KService'
    MICROTOSCA_NODES_MESSAGE_ROUTER_KPROXY = 'micro.nodes.MessageRouter.KProxy'

class RelationshipProperty(Enum):

    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_TIMEOUT_PROPERTY = "timeout"
    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_CIRCUIT_BREAKER_PROPERTY = "circuit_breaker"
    MICROTOSCA_RELATIONSHIPS_INTERACT_WITH_DYNAMIC_DISCOVERY_PROPERTY = "dynamic_discovery"

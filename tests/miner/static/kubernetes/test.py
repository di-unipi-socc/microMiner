from ruamel import yaml
from .....core.miner.static.staticMinerContext import StaticMinerContext
from .....core.topology.node import Node

if __name__ == '__main__':
    config = {  
                'strategy': 'plugins.miner.static.kubernetes.k8sStaticMiner.K8sStaticMiner',
                'arguments':
                    {
                        'folderPath': './sock-shop',
	                    'parserVersions':
		                {
                            'v1': 'plugins.miner.static.kubernetes.parser.v1Parser.V1Parser', 
		                    'v1beta1': 'plugins.miner.static.kubernetes.parser.v1beta1Parser.V1beta1Parser'
                        },
	                    'dbImagesPath': './dbImages.yml',
	                    'controllerImagesPath': './controllerImages.txt'
                    }
            }
    
    fileContent = ''
    nodes = {}
    StaticMinerContext.doStaticMining(config, nodes)
    
    for nodeName, node in nodes:
        fileContent += yaml.dump({'name': nodeName, 'spec': node.dump()})
        fileContent += '\n---\n'
    
    with open('./result.txt', 'w') as f:
        f.write(fileContent)

from ruamel import yaml
from core.topology.node import Node
from core.miner.static.staticMinerContext import StaticMinerContext
from ruamel.yaml import YAML
from pathlib import Path

print('Inizio test')

loader = YAML(typ='safe')
config = loader.load(Path('./tests/miner/static/kubernetes/config.yml'))
    
fileContent = ''
nodes = {}
StaticMinerContext.doStaticMining(config, nodes)

print('Nodi generati')
    
for nodeName, node in nodes.items():
    fileContent += yaml.dump({'name': nodeName, 'spec': node.dump()})
    fileContent += '\n---\n'

with open('./tests/miner/static/kubernetes/result.yml', 'w') as f:
    f.write(fileContent)

print('File creato')

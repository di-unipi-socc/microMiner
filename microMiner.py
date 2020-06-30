import click
import logging
from core.parser import Parser
from miner.generic.static.staticMinerContext import StaticMinerContext
from miner.generic.dynamic.dynamicMinerContext import DynamicMinerContext
from refiner.generic.refinerContext import RefinerContext
from exporter.ymlExporter import YMLExporter

@click.group()
def cli():
    """
    MicroMiner generate an architectural model of a microservices application
    """

@cli.command()
@click.argument('strategy')
@click.argument('source')
@click.argument('target')
@click.option('--time', default = 60, help = 'Seconds of monitoring')
@click.option('--test', default = '', help = 'FQN module of test')
@click.option('--name', default = 'Generic application', help = 'Name of the microTOSCA model')
def generate(strategy, source, target, time, test, name):
    nodes = {}
    #Cerco la strategia di mining richiesta
    strategyConfig = Parser.searchMinerStrategy(strategy)
    #Eseguo quella statica se presente
    if 'static' in strategyConfig:
        print('Executing static mining...')
        StaticMinerContext.doStaticMining(strategyConfig['static']['class'], source, strategyConfig['static']['args'] if 'args' in strategyConfig['static'] else {}, nodes)
    #Eseguo quella dinamica se presente
    if 'dynamic' in strategyConfig:
        print('Executing dynamic mining...')
        if 'args' in strategyConfig['dynamic']:
            strategyConfig['dynamic']['args']['time'] = time
            strategyConfig['dynamic']['args']['test'] = test
            DynamicMinerContext.doDynamicMining(strategyConfig['dynamic']['class'], source, strategyConfig['dynamic']['args'], nodes)
        else:
            strategyConfig['dynamic']['args'] = {'time': time}
            strategyConfig['dynamic']['args'] = {'test': test}
            DynamicMinerContext.doDynamicMining(strategyConfig['dynamic']['class'], source, strategyConfig['dynamic']['args'], nodes)
    
    #Carico ed eseguo tutte le strategie di refinement
    refinerStrategies = Parser.getRefinerStrategies()
    if refinerStrategies:
        print('Executing Refinement...')
        RefinerContext.doRefinement(refinerStrategies, nodes)

    #Esporto il microTOSCA
    print('Exporting microTOSCA...')
    YMLExporter.export(nodes, target, name)

if __name__ == "__main__":
    logging.basicConfig(filename = 'archMiner.log', filemode = 'w', level = logging.DEBUG)
    cli()

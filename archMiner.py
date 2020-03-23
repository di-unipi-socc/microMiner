import click
from core.parser import Parser
from miner.generic.static.staticMinerContext import StaticMinerContext
from miner.generic.dynamic.dynamicMinerContext import DynamicMinerContext
from exporter.ymlExporter import YMLExporter

@click.group()
def cli():
    """
    Archminer generate an architectural model of a microservices application
    """

@cli.command()
@click.argument('strategy')
@click.argument('name')
@click.argument('source')
@click.argument('target')
def generate(strategy, name, source, target):
    nodes = {}
    strategyConfig = Parser.searchMinerStrategy(strategy)
    if 'static' in strategyConfig:
        print('Executing static mining...')
        StaticMinerContext.doStaticMining(strategyConfig['static']['class'], source, strategyConfig['static']['args'], nodes)
    if 'dynamic' in strategyConfig:
        print('Executing dynamic mining...')
        DynamicMinerContext.doDynamicMining(strategyConfig['dynamic']['class'], source, strategyConfig['dynamic']['args'], nodes)
    
    #REFINER

    print('Exporting microTOSCA...')
    YMLExporter.export(nodes, name, target)

if __name__ == "__main__":
    cli()
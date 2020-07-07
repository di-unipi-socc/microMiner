# microMiner
A tool for automatically generate a microTosca specification of a microservice-based architecture

# Installation
Clone this repository
Run "python setup.py install"
Run "pip install -r requirements.txt"
Execute microMiner with this command: "sudo python microMiner generate strategy sorce target [test] [time]" where strategy indicates the mining strategy (actually available only "Kubernetes"), source indicates the path of the folder containing the manifest files, target is the path of the microTOSCA file. Test is optional and specify the fqn of the module of test. Time is also optional (default 60 seconds) and specify how long the application should be monitored.

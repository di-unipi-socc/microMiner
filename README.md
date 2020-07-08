# MicroMiner
MicroMiner is a tool for automatically determining the architecture of a microservice-based application, in the microTOSCA specification, i.e., by a topology graph, whose nodes model the services, integration components (e.g., API gateways, message queues, or load balancers), and databases forming the application, and whose arcs indicate the runtime interactions occurring among them.  
MicroMiner determines the architecture with a black-box approach, i.e., without knowing the source code of the application but only the deployment files.  
It presents a plug-in architecture to support multiple deployment specification (e.g., Kubernetes, Docker compose, Chef) and to support multiple strategies to recognize integration components.  
Actually, we support only the Kubernetes manifest files and we are able to recognize message routers, message brokers, client-side discovery pattern and databases.  
The execution of MicroMiner is divided into three steps, as shown in this figure:  

![solution](https://user-images.githubusercontent.com/44097586/86887448-d66b4c80-c0f8-11ea-9575-0a3c4f2314e4.png)

The figure below illustrates the modular architecture of MicroMiner: the main module offers a command-line interface enabling application administrators to provide the manifest files specifying the application deployment in Kubernetes. Given such files, the main module starts orchestrating the other modules to enact the architecture mining, i.e., (i) it first invokes the miner to enact the static and dynamic mining steps in our approach, (ii) it then invokes the refiner to refine the mined topology as described in the refinement step in our approach, and (iii) it finally invokes the exporter to obtain the specification in microTOSCA of the mined architecture. Step (i) and (ii) incrementally build and refine the architecture of the analysed microservice-based application by relying on the topology module, which enables instantiating and updating topology graphs. Step (iii) then picks the mined topology graph from the topology module and streamlines it to microTOSCA.

![microminer-architecture](https://user-images.githubusercontent.com/44097586/86887621-1f230580-c0f9-11ea-9b42-9ce864346c1d.png)

## Requirements
MicroMiner must be executed in a Kubernetes cluster on a UNIX environment.    
It's requested Python 3.8 and the sudo privileges.  
To support all MicroMiner features you need to enable ephemeralContainers on your Kubernetes cluster (https://www.shogan.co.uk/kubernetes/enabling-and-using-ephemeral-containers-on-kubernetes-1-16/).

## Installation
Clone this repository.  
Run:  
```
python setup.py install  
sudo pip install -r requirements.txt  
```

## Usage
Run:  
```
sudo python -m microMiner generate strategy source target [test] [time] [name]
```
where "strategy" indicates the mining strategy (actually only "Kubernetes"), "source" indicates the path of the folder containing the manifest files, "target" is the path of the microTOSCA file. "Test" is optional and specify the fqn of the module of test. "Time" is also optional (default 60 seconds) and specify how long the application should be monitored. "Name" is the name of the application.

## Demo
You can try MicroMiner with MiniKube (https://kubernetes.io/docs/tasks/tools/install-minikube/) and with the demo application Online-boutique (https://github.com/GoogleCloudPlatform/microservices-demo):
```
sudo python -m microMiner generate kubernetes tests/kubernetes/online-boutique/deployment microMiner-DEMO.yaml --time=10
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

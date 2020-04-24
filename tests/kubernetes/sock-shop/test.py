import docker

def runTest():
    client = docker.from_env()
    client.containers.run('weaveworksdemos/load-test', network_mode = 'host', command = '-h 192.168.56.20:30001 -c 10 -r 50')

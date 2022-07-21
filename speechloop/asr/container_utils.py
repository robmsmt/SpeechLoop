import time
import warnings


try:
    import docker

    DOCKER_CLIENT = docker.from_env()
except Exception as e:
    warnings.warn("Either docker is not installed OR the docker client cannot be connected to. " "This might be ok if using just APIs")


def launch_container(dockerhub_url, ports_dict, verbose=True, delay=5):
    container_running = False
    for container in DOCKER_CLIENT.containers.list():
        if len(container.image.tags) > 0 and container.image.tags[-1] == dockerhub_url:
            if verbose:
                print(f"Docker container: {dockerhub_url} found running")
            container_running = True

    if not container_running:
        if verbose:
            print(f"Docker container: {dockerhub_url} NOT found... downloading and/or running...")
        DOCKER_CLIENT.containers.run(
            dockerhub_url,
            detach=True,
            ports=ports_dict,
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
        )
        if verbose:
            print(f"{dockerhub_url} Downloaded. Starting container...")
        time.sleep(delay)


def kill_container(dockerhub_url, verbose=True):
    for container in DOCKER_CLIENT.containers.list():
        if len(container.image.tags) > 0 and container.image.tags[-1] == dockerhub_url:
            if verbose:
                print(f"Docker container: {dockerhub_url} found. Killing...")
            container.stop()

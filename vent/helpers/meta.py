import datetime
import docker
import multiprocessing
import os
import pkg_resources
import platform
import subprocess

from vent.api.plugin_helpers import PluginHelper
from vent.api.templates import Template
from vent.helpers.paths import PathDirs


def Version():
    """ Get Vent version """
    version = ''
    try:
        version = pkg_resources.require("vent")[0].version
        if not version.startswith('v'):
            version = 'v' + version
    except Exception as e:  # pragma: no cover
        pass
    return version


def System():
    """ Get system operating system """
    return platform.system()


def Docker():
    """ Get Docker setup information """
    docker_info = {'server': {}, 'env': '', 'type': '', 'os': ''}

    # get docker server version
    try:
        d_client = docker.from_env()
        docker_info['server'] = d_client.version()
    except Exception as e:  # pragma: no cover
        pass

    # get operating system
    system = System()
    docker_info['os'] = system

    # check if native or using docker-machine
    if 'DOCKER_MACHINE_NAME' in os.environ:
        # using docker-machine
        docker_info['env'] = os.environ['DOCKER_MACHINE_NAME']
        docker_info['type'] = 'docker-machine'
    elif 'DOCKER_HOST' in os.environ:
        # not native
        docker_info['env'] = os.environ['DOCKER_HOST']
        docker_info['type'] = 'remote'
    else:
        # using "local" server
        docker_info['type'] = 'native'
    return docker_info


def Containers(vent=True, running=True):
    """
    Get containers that are created, by default limit to vent containers that
    are running
    """
    containers = []

    try:
        d_client = docker.from_env()
        if vent:
            c = d_client.containers.list(all=not running,
                                         filters={'label': 'vent'})
        else:
            c = d_client.containers.list(all=not running)
        for container in c:
            containers.append((container.name, container.status))
    except Exception as e:  # pragma: no cover
        pass

    return containers


def Cpu():
    cpu = "Unknown"
    try:
        cpu = str(multiprocessing.cpu_count())
    except Exception as e:  # pragma: no cover
        pass
    return cpu


def Gpu(pull=False):
    gpu = ""
    try:
        image = 'nvidia/cuda:8.0-runtime'
        image_name, tag = image.split(":")
        d_client = docker.from_env()
        nvidia_image = d_client.images.list(name=image)

        if pull and len(nvidia_image) == 0:
            try:
                d_client.images.pull(image_name, tag=tag)
                nvidia_image = d_client.images.list(name=image)
            except Exception as e:  # pragma: no cover
                pass

        if len(nvidia_image) > 0:
            cmd = 'nvidia-docker run --rm ' + image + ' nvidia-smi -L'
            proc = subprocess.Popen([cmd],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True,
                                    close_fds=True)
            gpus = proc.stdout.read()
            if gpus:
                for line in gpus.strip().split("\n"):
                    gpu += line.split(" (UUID: ")[0] + ", "
                gpu = gpu[:-2]
            else:
                gpu = "None"
        else:
            gpu = "None"
    except Exception as e:  # pragma: no cover
        gpu = "Unknown"
    return gpu


def Images(vent=True):
    """ Get images that are build, by default limit to vent images """
    images = []

    # TODO needs to also check images in the manifest that couldn't have the
    #      label added
    try:
        d_client = docker.from_env()
        if vent:
            i = d_client.images.list(filters={'label': 'vent'})
        else:
            i = d_client.images.list()
        for image in i:
            images.append((image.tags[0], image.short_id))
    except Exception as e:  # pragma: no cover
        pass

    return images


def Jobs():
    """
    Get the number of jobs that are running and finished, and the number of
    total tools running and finished for those jobs
    """
    jobs = [0, 0, 0, 0]

    # get running jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=False,
                                     filters={'label': 'vent-plugin'})
        files = []
        for container in c:
            jobs[1] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[0] = len(files)
    except Exception as e:  # pragma: no cover
        pass

    # get finished jobs
    try:
        d_client = docker.from_env()
        c = d_client.containers.list(all=True,
                                     filters={'label': 'vent-plugin'})
        files = []
        for container in c:
            jobs[3] += 1
            if 'file' in container.attrs['Config']['Labels']:
                if container.attrs['Config']['Labels']['file'] not in files:
                    files.append(container.attrs['Config']['Labels']['file'])
        jobs[2] = len(files) - jobs[0]
        jobs[3] = jobs[3] - jobs[1]
    except Exception as e:  # pragma: no cover
        pass

    return tuple(jobs)


def Tools(**kargs):
    """ Get tools that exist in the manifest """
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()
    return tools[1]


def Services(vent=True):
    """
    Get services that have exposed ports, by default limit to vent containers
    """
    services = []
    try:
        d_client = docker.from_env()
        if vent:
            containers = d_client.containers.list(filters={'label': 'vent'})
        else:
            containers = d_client.containers.list()
        for container in containers:
            if vent:
                name = container.attrs['Config']['Labels']['vent.name']
            else:
                name = container.name
            ports = container.attrs['NetworkSettings']['Ports']
            p = []
            for port in ports:
                if ports[port]:
                    p.append(ports[port][0]['HostIp'] +
                             ":" +
                             ports[port][0]['HostPort'])
            if p:
                services.append((name, p))
    except Exception as e:  # pragma: no cover
        pass
    return services


def Tools_Status(core, branch="master", version="HEAD", **kargs):
    """
    Get tools that are currently installed/built/running and also the number of
    repos that those tools come from; can toggle whether looking for core tools
    or plugin tools
    """
    # !! TODO this might need to store namespaces/branches/versions
    all_tools = {'built': [], 'running': [], 'installed': [], 'normal': []}
    core_repo = 'https://github.com/cyberreboot/vent'
    repos = set()
    tools = Tools(**kargs)
    p_helper = PluginHelper(plugins_dir='.internals/plugins/')

    # get manifest file
    path_dirs = PathDirs(**kargs)
    manifest = os.path.join(path_dirs.meta_dir, "plugin_manifest.cfg")
    template = Template(template=manifest)
    tools = template.sections()

    # get repos
    if core:
        repos.add(core_repo)
    else:
        for tool in tools[1]:
            repo = template.option(tool, 'repo')
            if repo[0] and repo[1] != core_repo:
                repos.add(repo[1])

    # get normal tools
    for repo in repos:
        status, _ = p_helper.clone(repo)
        if status:
            p_helper.apply_path(repo)
            p_helper.checkout(branch=branch, version=version)
            path, _, _ = p_helper.get_path(repo)
            matches = None
            if core:
                matches = p_helper.available_tools(path, version=version,
                                                   groups='core')
            else:
                matches = p_helper.available_tools(path, version=version)
            for match in matches:
                all_tools['normal'].append(match[0].split('/')[-1])
        else:
            all_tools['normal'] = 'failed'

    # get tools that have been installed
    for tool in tools[1]:
        repo = template.option(tool, "repo")
        if repo[0] and repo[1] in repos:
            name = template.option(tool, "name")
            if name[0]:
                all_tools['installed'].append(name[1])

    # get core tools that have been built and/or are running
    try:
        d_client = docker.from_env()
        images = d_client.images.list(filters={'label': 'vent'})
        for image in images:
            try:
                core_check = ("vent.groups" in image.attrs['Labels'] and
                              'core' in image.attrs['Labels']['vent.groups'])
                image_check = None
                if core:
                    image_check = core_check
                else:
                    image_check = not core_check
                if image_check:
                    if 'vent.name' in image.attrs['Labels']:
                        all_tools['built'].append(image.attrs['Labels']['vent.name'])
            except Exception as err:  # pragma: no cover
                pass
        containers = d_client.containers.list(filters={'label': 'vent'})
        for container in containers:
            try:
                core_check = ("vent.groups" in container.attrs['Config']['Labels'] and
                              'core' in container.attrs['Config']['Labels']['vent.groups'])
                container_check = None
                if core:
                    container_check = core_check
                else:
                    container_check = not core_check
                if container_check:
                    if 'vent.name' in container.attrs['Config']['Labels']:
                        all_tools['running'].append(container.attrs['Config']['Labels']['vent.name'])
            except Exception as err:  # pragma: no cover
                pass
    except Exception as e:  # pragma: no cover
        pass
    return (len(repos), all_tools)


def Timestamp():
    """ Get the current datetime in UTC """
    timestamp = ""
    try:
        timestamp = str(datetime.datetime.now())+" UTC"
    except Exception as e:  # pragma: no cover
        pass
    return timestamp


def Uptime():
    """ Get the current uptime information """
    uptime = ""
    try:
        uptime = str(subprocess.check_output(["uptime"], close_fds=True))[1:]
    except Exception as e:  # pragma: no cover
        pass
    return uptime

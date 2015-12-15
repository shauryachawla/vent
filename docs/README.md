Vent Documentation
====

Summary of stuff.

Install instructions
====

For a pre-compiled ISO, skip down to the next [section](#install-instructions-download-the-release).

#### Build dependencies:
```
make
docker
```
#### Step 1 - Clone:
```
git clone https://github.com/CyberReboot/vent.git
cd vent
```
#### Step 2 - Make:

There are [several options](#install-instructions-makefile-options) of how to build `vent` from the Makefile.  
The easiest way to get started quickly is to just execute:
```
make
```
which will build the Vent ISO that can be deployed as a VM or on a bare metal server.
#### Step 3 - Deploy:

This is just a standard ISO that can be deployed like any other ISO, but here is a simple way using [docker-machine](https://docs.docker.com/machine/) with a local virtualbox (`docker-machine` can also be used to deploy `vent` on cloud providers and data centers):
```
# from a terminal that is in the `vent` directory
# start a simple webserver to serve up the ISO file
python -m SimpleHTTPServer

# from another terminal run `docker-machine`
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent
# other options to customize the size of the vm are available as well:
# --virtualbox-cpu-count "1"
# --virtualbox-disk-size "20000"
# --virtualbox-memory "1024"

# once it's done provisioning, the webserver from the first terminal can be stopped
# SSH into the vent CLI
docker-machine ssh vent
```
Now you're ready to [get started](#getting-started) using `vent`.

Download the release
----

Summary of stuff.

Makefile options
----

Summary of stuff.

Getting Started
====

Summary of stuff.

Demo
----

Summary of stuff.

Tutorial
----

Summary of stuff.

Usage
----

Summary of stuff.

Use cases
----

Summary of stuff.

Advanced Usage
====

Vent is based off of [boot2docker](https://github.com/boot2docker/boot2docker).  There are a few notable differences in the way this VM runs than a typical one might.  Vent will automatically install and provision the disk on boot and then restart when done.  Vent runs in RAM, so changes need to be made under `/var/lib/docker` or `/var/lib/boot2docker` as those are persistent (see boot2docker [documentation](https://github.com/boot2docker/boot2docker/blob/master/README.md) for more information).  it's possible that the `vent-management` container won't automatically get added and run, in order to remedy you can go to the shell from the vent CLI and run `docker ps` and if it's not running execute `sudo /data/custom`.

Commands
----

Summary of stuff.

Developers
====

Summary of stuff.

API
----

Summary of stuff.

Customizing
----

Summary of stuff.

Contributing
----

Summary of stuff.

Ecosystem
====

Summary of stuff.


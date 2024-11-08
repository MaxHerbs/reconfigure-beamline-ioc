# Reconfigure IOC
Script to convert between new container-style kubernetes IOC and old malcolm format and vice versa.

# Repository Structure
```
├── ClusterHandler.py - Provides an interface with kubernetes
├── IocController.py  - Configures IOC to restore malcolm compatibility
├── main.py - The main script
├── configurations - Store malcom-configure yaml files
├── internals - Internal store of previous kubernetes configurations
├── README.md - Repository readme
├── requirements.txt - Pip requirements
└── run.sh - Main run script
```

`run.sh` is executable to start the script. This then verifies paths and includes the files necessary for `main.py` to run. Both `IocController.py` and `ClusterHandler.py` provide classes to with their own functionality, relating to configuring legacy IOC's and managing the kubernetes IOC's.

# Running the Script

### First Time Setup:
Running the following should fetch all the pre-requesits, and spit out the correct bash command to run the script

```bash
$ bash first-time-setup.sh
```
You will still need to create your own config file for restoring malcolm scans, but this repository will provide a template to base your own on. The script will output something like the following, so change config path (the first param) as necessary.

```bash
RUN:
bash run.sh configurations/master.yaml venv/bin/activate p99-services/environment.sh
```


The script has three pre-requisits;

1. A config file describing each malcolm-style IOC name and executable path. See `configurations/master.yaml` for reference on structure. 
2. A path to a virtual enviroment. A valid venv is needed to for `run.sh`, which then provides the script with the correct tools for kubernetes etc.
3. A path to a beamline-repo's `environment.sh`. This describes the full namespace and kubernetes config to allow the script to interact with the cluster.[The p99 service is available here](https://github.com/MaxHerbs/p99-services).

To start the script;

```bash 
# bash run.sh {path to config yaml} {path to venv} {path to beamline environment}
$ bash run.sh configurations/master.yaml venv/bin/activate /scratch/$USER/p99-services/environment.sh
```

# Options
When running the script, you will be presented with several options:

```
Would you like to:
1. Reconfigure all IOC a specific config
2. Restore Kubernetes IOC configuration
3. Exit the script
```

1. This will stop all kuberenetes IOC, and then run configure-ioc to set the paths for each IOC boot script as described in the chosen config yaml file.

> **NOTE**: If you choose this, you will be asked whether you would like to make a new restore file for the current Kubernetes IOC states. **Usually you will not want to do this**. If you choose to do this, a new restore file will be created, recording the states that the Kubernetes IOC are in, and this will become the the first-choice restore file for returning to the kubernetes IOC. Choosing option 1 will continue the script without adding a new restore point, so the previous restore point will be used when restoring the kubernetes IOC. You may want to do this if recent, permanant, changes have been made manually to the cluster IOC that you want to keep.


2. This option will restore the Kubernetes IOCs. Every time you create a new restore point, the states of the kubernetes IOC are logged and dated into a restore file in `internals/...`. When restoring kubernetes, the script will restore as described in the most recent restore file.

3. Exit. This will stop the script. No changes have been made at this point.
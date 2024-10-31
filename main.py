from IocController import IocController
from ClusterHandler import ClusterHandler
import os
import yaml
import sys

def main(configPath):
    clusterHandler = ClusterHandler()

    chosen = False
    while not chosen:
        print("\n\n\n")
        print("Would you like to:")
        print("1. Reconfigure all IOC a specific config")
        print("2. Restore Kubernetes IOC configuration")
        print("3. Exit the script")
     
        choice = input("Enter your choice (1,2,3): ") 
        
        try:
            choice = int(choice)
        except:
            pass

        if choice == 1: 
            chosen = True
        if choice == 2: 
            chosen = True
        if choice == 3: 
            exit()
        else: 
            print("Invalid choice. Please enter 1, 2, or 3.")




    if choice == 2:
        status = clusterHandler.restoreKubernetes()
        if status:
            print("Kubernetes has been restored.")
        else:
            print("An error occured while restoring Kubernetes")
        exit()
  

    clusterHandler.begin()
    clusterHandler.takeDownKubernetes()

    print(configPath)
    path = configPath
    errorsList = dict()
    if not os.path.exists(path):
        print("Config file could not be found")
        errorsList["Missing Config"] = f"Config file could not be found at {path}"
        return errorsList
    configFile = open(path, "r")
    try:
        configYaml = yaml.safe_load(configFile)
    except Exception as err:
        errorsList["Broken Config"] = f"Something went wrong while parsing the configuration file\n{err}"
        print("Something went wrong opening the config file")
        return errorsList
    for ioc in configYaml["iocs"]:
        myIoc = IocController(ioc)
        status = myIoc.redirectIoc()
        if status:
            errorsList[myIoc.iocName + " Redirect Error"] = "ERROR: " + status[0] + "Message: " + status[1] 
        
        status = myIoc.restartIoc()
        if status:
            print(f"An error occured while restarting {myIoc.iocName}({myIoc.nickname})\n{status}\nErrors will be listed at the end of run time.")
            errorsList[myIoc.iocName + " Reboot Error"] = status 
        
    print("\n")
    if not errorsList:
        print("Success")
    else:
        print("#############################################")
        print("########The following errors occured:########")
        print("#############################################")
        for ioc, error in errorsList.items():
            print("---------------------------------------------")
            print(f"{ioc}: {error}")
            print("")


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Please enter the path to the configuration file as an argument")
        exit()
    if not os.path.exists(args[1]):
        print(f"The config file could not be found at {args[1]}") 
        exit()
    
    main(args[1])
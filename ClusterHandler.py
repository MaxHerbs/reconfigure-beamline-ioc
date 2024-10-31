import os
import subprocess
import sys
from datetime import datetime

KUBE_CONF_PATH = "internals/"
class ClusterHandler:
    initialStatus = dict()
    def __init__(self):
        pass

    def begin(self):
        cmd = ["kubectl", "get", "statefulsets"]
        response = subprocess.run(cmd, capture_output=True)
        if response.returncode != 0:
            print("Error: Issur while getting statefulsets")
            print(response.stderr.decode("utf-8"))
            return
        clusterTable = response.stdout.decode("utf-8").split("\n")[1::]
        print(clusterTable)

        statefulSetInfo = []
        for row in clusterTable:
            row = row.split(" ")
            rowInfo = [element for element in row if element != ""]
            if len(rowInfo) > 0:
                statefulSetInfo.append(rowInfo)
        try:
            validSets = [(statefulSet[0], statefulSet[1].split("/")[1]) for statefulSet in statefulSetInfo if "bl99p" in statefulSet[0]]
        except Exception as e:
            print("Error: Issue while parsing statefulsets")
            print(e)
            print("Are the slashes missing in table output or is the table malformed?")

        self.initialStatus = dict(validSets)
        print(self.initialStatus)
        self.storeKubernetesConfig()


    def storeKubernetesConfig(self):
        if os.path.exists(KUBE_CONF_PATH) and os.listdir(KUBE_CONF_PATH):
            print("\n\n\n")
            print("There is currently a restore point of the IOC states in the kubernetes cluster, but this may be out of date")
            chosen = False
            while not chosen:
                print("Would you like to:")
                print("1. Continue (Most likely option)")
                print("2. Add a new restore post based on the current kubernetes IOC states and continue with the script")
                print("3. Exit the script")
             
                choice = input("Enter your choice (1,2,3): ") 
                
                try:
                    choice = int(choice)
                except:
                    pass

                if choice == 1: 
                    return True
                if choice == 2: 
                    chosen = True
                if choice == 3: 
                    exit()
                else: 
                    print("Invalid choice. Please enter 1, 2, or 3.")

        status = self.writeKubernetesConfig()
        return status


    def writeKubernetesConfig(self):
        fileName = KUBE_CONF_PATH + f"kubernetesConfig.{datetime.now().strftime('%m%d%Y-%H%M%S')}.dict"
        with open(fileName, "w+") as f:
            f.write(str(self.initialStatus))
        return True


    def takeDownKubernetes(self):
        if not os.path.exists(KUBE_CONF_PATH) and not os.listdir(KUBE_CONF_PATH):
            print("No kubernetes config file exists. You will have to manually restart all of the kubernetes IOC.")
            choice = input("Would you like to continue? (y/n): ")
            while choice.lower() not in "yn":
                print("Invalid choice. Please enter y or n.")

            if choice.lower() == "n":
                exit()
        
        if not self.initialStatus:
            self.begin()


        return self.runKubernetesScale(0)


    def restoreKubernetes(self):
        if not os.path.exists(KUBE_CONF_PATH):
            print("Kubeconfig directory does not exist. Please run the script again.")
            return False
        availableConfigs = os.listdir(KUBE_CONF_PATH)
        if len(availableConfigs) == 0:
            print("No available configs found to restore from")
            return False
        print(availableConfigs)

        filesDates = [datetime.strptime(file.split(".")[1], '%m%d%Y-%H%M%S') for file in availableConfigs if "kubernetesConfig" in file]
        filePath = KUBE_CONF_PATH + "kubernetesConfig." + sorted(filesDates)[0].strftime('%m%d%Y-%H%M%S') + ".dict"

        with open(filePath, "r") as f:
            self.initialStatus = eval(f.read())
            
        return self.runKubernetesScale()


    def runKubernetesScale(self, replicas = None):
        success = True
        for ioc, number in self.initialStatus.items():
            cmd = ["kubectl", "scale", f"--replicas={number if replicas == None else replicas}", "statefulset", ioc]
            print("Running ", " ".join(cmd))
            response = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            print(response.stdout.decode("utf-8"))
                  
            if response.returncode != 0:
                print(f"Error: Issue while restoring {ioc} kubernetes config")
                print(response.stderr)
                success = False
        
        return success
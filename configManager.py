import os
import shutil

configFile = "configuration/config.json"
defaultConfigFile = "defaultConfiguration/defaultConfig.json"

# Copies the default configuration file into the configuration volume if no config.json is found
def initConfigJSON():
    if not os.path.exists(configFile):
            shutil.copy(defaultConfigFile, configFile)
    else:
        print("config.json already exists in configuration volume")

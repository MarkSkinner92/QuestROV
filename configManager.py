import os
import shutil

# Copies the default configuration file into the configuration volume if no config.json is found
def initConfigJSON():
    if not os.path.exists("configuration/config.json"):
            shutil.copy("defaultConfiguration/defaultConfig.json", "configuration/config.json")
    else:
        print(" config.json already exists in configuration volume")
from time import time
from json import loads, dumps
from sys import argv, exit

print(""" __      ___    _____                     _____ _          __  __ 
 \ \    / / |  |  __ \                   / ____| |        / _|/ _|
  \ \  / /| | _| |__) |_ _ _ __ ___  ___| (___ | |_ _   _| |_| |_ 
   \ \/ / | |/ /  ___/ _` | '__/ __|/ _ \\___ \| __| | | |  _|  _|
    \  /  |   <| |  | (_| | |  \__ \  __/____) | |_| |_| | | | |  
     \/   |_|\_\_|   \__,_|_|  |___/\___|_____/ \__|\__,_|_| |_|  
             https://github.com/execeval/vkparsestuff                                                            
                                                                  """)
print("""Usage:\nvkparse.py set (login/password)\nvkparse.py active <findIn> <findFor>  ## shows findFor's active in 
        findIn's page\n""")

global settings
with open("settings.json") as file:
    settings = loads(file.read())


def dumpSettings(whatToSet, data, settings=settings):
    settings[whatToSet] = data
    settings = dumps(settings)
    with open("settings.json", "w") as file:
        file.write(settings)


if len(argv) - 1:
    if argv[1].startswith("set"):
        if len(argv) != 4:
            print("Wrong usage! Example to set: set password {your password}")
        else:
            if argv[2].startswith("password"):
                dumpSettings("password", argv[3])
                print("Password was changed to " + argv[3])
                exit()
            elif argv[2].startswith("login"):
                dumpSettings("login", argv[3])
                print("Login was changed to " + argv[3])
        exit()
else:
    exit()

from kernel import *

if argv[1].startswith("active"):
    if len(argv) != 4:
        print("Wrong usage! Example: active <findIn> <findFor>")
    else:
        print(findActiveBy(argv[3], argv[2]))

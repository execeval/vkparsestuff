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
print("""Usage:\nvkpasrse.py set (login/password/output)  ##output can be py and js""")

global settings
with open("settings.json") as file:
    settings = loads(file.read())


def setsets(whatToSet, data, settings=settings):
    settings[whatToSet] = data
    settings = dumps(settings)
    with open("settings.json", "w") as file:
        file.write(settings)


if len(argv) - 1:
    if argv[1].startswith("set"):
        if len(argv) < 4:
            print("Wrong usage! Example to set: set password {your password}")
        else:
            if argv[2].startswith("password"):
                setsets("password", argv[3])
                print("Password was changed to " + argv[3])
                exit()
            elif argv[2].startswith("login"):
                setsets("login", argv[3])
                print("Login was changed to " + argv[3])
        exit()

from kernel import *



'''

start_time = time()
shot, yandere = "237921652", " "

# list_shot=[163993326,145419056,135208164,132879947]

shot_info = vk.users.get(user_ids=shot)
print(shot_info)

yandere_friend = vk.friends.get(user_id=yandere)['items']
shot_friend = vk.friends.get(user_id=shot)['items']
common_friends = set(yandere_friend) & set(shot_friend)  # Общие друзья

print('Друзья цели')

findCommon(shot, yandere)
shot_counter = deepFriNet(shot)
deepFriNet_t(shot_counter)

# findActiveBy(shot,yandere)
# shot_info= vk.users.get(user_ids=shot)
# print(shot_info)
# yandere_friend = vk.friends.get(user_id=yandere)['items']
# shot_friend = vk.friends.get(user_id=shot)['items']
# common_friends = set(yandere_friend) & set(shot_friend) #Общие друзья
# print('Друзья цели')
# findCommon(shot, yandere)
# shot_counter = deepFriNet(shot)
# deepFriNet_translate(shot_counter)


print("--- %s seconds ---" % (time() - start_time))
'''

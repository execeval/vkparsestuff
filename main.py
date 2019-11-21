from time import time
from kernel import *

# print(vk.likes.isLiked(user_id=yandere,ttype='photo' ,owner_id=shot,item_id =photo['id'])['liked'])


start_time = time()
shot, yandere = " ", " "

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

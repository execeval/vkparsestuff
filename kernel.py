from collections import Counter
from json import dumps, loads
from sys import exit
from vk_api import *
from vk_api.exceptions import *

with open("settings.json") as settings:
    settings = loads(settings.read())

vk_session = VkApi(settings['login'], settings['password'])

try:
    vk_session.auth()
except Captcha and BadPassword:
    print("Error with auth! Please use main.py set password <pass> and main.py set login <login>")
    exit()
vk = vk_session.get_api()

userFriends = lambda user, offset=0, whl=24: '''
        var i = 0 ;  
        var members = [];
        var user_friends = API.friends.get({"user_id": %d})["items"];
        while(i < %d){
        members.push(API.friends.get({"user_id": user_friends[i +%d]})["items"]);
        i = i + 1;
        }
        return members;
        ''' % (user, offset, whl)

countLikes = lambda user_id, ttype, owner_id, item_ids, whl=25: '''
        var i = 0 ;  
        var count = 0;
        var item_ids = %d;
        while(i < %d){
        count = count + API.likes.isLiked({"user_id": %d, "type": \"%d\", "owner_id": %d, "item_id": item_ids[i]})["liked"];
        i = i + 1;
        }
        return count;
        ''' % (user_id, ttype, owner_id, item_ids, whl)


def findActiveBy(shot, yandere):  # собираем активность на странице shot пользователя yandere
    res = 0
    shot_info = vk.users.get(user_ids=shot, name_case='gen')[0]

    # print("На странице",shot_info['first_name'],shot_info['last_name'])

    yandere_info = vk.users.get(user_ids=yandere, name_case='gen')[0]

    print(">Считаем лайки", yandere_info['first_name'], yandere_info['last_name'] + '<')

    if shot_info['is_closed'] and not (shot_info['can_access_closed']):
        print("Нет доступа к аккаунту")
        return "full_close"

    wall, photos, saves = False, False, False
    # shot_friend = vk.friends.get(user_id=shot)['items']

    try:
        wall = vk.wall.get(owner_id=shot, count='100')
    except ApiError:
        print("стена закрыта")

    try:
        photos = vk.photos.get(owner_id=shot, album_id="profile", rev="1", count="100")
    except ApiError:
        print("профильные фотки закрыты")

    try:
        saves = vk.photos.get(owner_id=shot, album_id="saved", rev="1", count="100")
    except ApiError:
        print("сохры закрыты")
    # print(wall) #["count"]

    if saves:
        saved_likes = 0
        photo_ids = []

        for photo in saves['items']:
            photo_ids.append(photo['id'])
        # print(Code.countLikes(ttype="photo ",item_ids=photo_ids,owner_id=shot,user_id=yandere))

        lenc = len(photo_ids)
        ind = 0

        while lenc > 25:
            saved_likes += int(vk.execute(
                code=countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere)))
            ind += 25
            lenc -= 25

        saved_likes += int(vk.execute(
            code=countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere,
                            whl=lenc)))
        res += saved_likes
        print("Лайкнуто сохров:", saved_likes)

        # for likes in vk.likes.getList(ttype="photo", owner_id=shot, item_id=photo["id"])['items']:  #print(
        # vk.likes.isLiked(user_id=yandere,ttype='photo' ,owner_id=shot,item_id =photo['id'])['liked'])
        # like_shot_saved_photos[likes] += 1

    if photos:
        prof_likes = 0
        photo_ids = []
        # print(photos['items'])

        for photo in photos['items']:
            # print(vk.likes.isLiked(user_id=yandere, ttype='photo', owner_id=shot, item_id=photo['id'])['liked'])
            # print(photo)
            photo_ids.append(photo['id'])

        # print(Code.countLikes(ttype="photo ",item_ids=photo_ids,owner_id=shot,user_id=yandere))
        lenc = len(photo_ids)
        ind = 0

        while lenc > 25:
            # print(Code.countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere))
            prof_likes += int(vk.execute(
                code=countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere)))
            ind += 25
            lenc -= 25

        prof_likes += int(vk.execute(
            code=countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere,
                            whl=lenc)))
        res += prof_likes
        print("Лайкнуто профильных фоток:", prof_likes)

    if wall and photos:

        wall_likes = 0
        wall_ids = []
        for post in wall["items"]: wall_ids.append(post['id'])
        lenc = len(wall_ids)
        ind = 0

        while lenc > 25:
            # print(Code.countLikes(ttype="photo", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere))
            wall_likes += int(vk.execute(
                code=countLikes(ttype="post", item_ids=wall_ids[ind:ind + 25], owner_id=shot,
                                user_id=yandere)))
            ind += 25
            lenc -= 25

        wall_likes += int(vk.execute(
            code=countLikes(ttype="post", item_ids=photo_ids[ind:ind + 25], owner_id=shot, user_id=yandere,
                            whl=lenc)))
        res += wall_likes
        print("Лайкнуто записей на стене:", wall_likes)
    return res


def deepFriNet(shot):
    print(shot)
    info = vk.users.get(user_ids=shot)[0]
    print(info)

    if info['is_closed'] and info['can_access_closed']:
        return "full_close"

    wall, photos, saves = False, False, False
    like_shot_wall = Counter()
    like_shot_photos = Counter()
    like_shot_saved_photos = Counter()

    try:
        wall = vk.wall.get(owner_id=shot, count='100')
    except ApiError:
        return ">стена закрыта"

    try:
        photos = vk.photos.get(owner_id=shot, album_id="profile", rev="1")
    except ApiError:
        return ">профильные фотки закрыты"

    try:
        saves = vk.photos.get(owner_id=shot, album_id="saved", rev="1")
    except ApiError:
        return ">сохры закрыты"

    # print(wall) #["count"]
    if saves:
        for photo in saves['items']:
            # print(photo)
            for likes in vk.likes.getList(ttype="photo", owner_id=shot, item_id=photo["id"])['items']:
                like_shot_saved_photos[likes] += 1

    if photos:
        for photo in photos['items']:
            # print(photo)
            for likes in vk.likes.getList(ttype="photo", owner_id=shot, item_id=photo["id"])['items']:
                like_shot_photos[likes] += 1

    if wall:
        for post in wall["items"]:
            for likes in vk.likes.getList(ttype="post", owner_id=shot, item_id=post["id"])['items']:
                like_shot_wall[likes] += 1

    d = 0
    return [like_shot_wall.most_common(), like_shot_photos.most_common(), like_shot_saved_photos.most_common()]


def deepFriNet_t(res):
    f = 0
    tittle = ["лайки стены", "лайки профильных фоток", "лайки сохр"]

    for list_user in res:  # [0]-лайки стены [1]-лайки профильных фоток [2]- лайки сохр

        print(tittle[f])
        all_id = []

        for z in list_user: all_id.append(z[0])

        # print(str(all_id)[1:-1])
        info_list = vk.users.get(user_ids=all_id, fields="domain")

        for i in range(len(list_user)):
            print("❤" + str(list_user[i][1]), info_list[i]['first_name'], info_list[i]['last_name'],
                  "vk.com/" + info_list[i]['domain'], )

        f += 1


def findCommon(shot, yandere):
    yandere_friend = vk.friends.get(user_id=yandere)['items']
    shot_friends = vk.friends.get(user_id=shot)['items']
    # print("Shot Friends ---", shot_friends)
    count = len(shot_friends)
    offset = 0

    while count > 24:
        # print(code(user=shot ,offset=offset))
        res = vk.execute(code=userFriends(user=shot, offset=offset))
        for i in range(24):
            try:
                shot_friend = shot_friends[offset + i]
                if str(shot_friend) == str(yandere):
                    continue
                shot_friend_friends = res[i]
                shot_friend_info = vk.users.get(user_ids=shot_friend, fields="domain")[0]
                common_shot = (set(shot_friend_friends) & set(shot_friends))
                common_yandere = (set(shot_friend_friends) & set(yandere_friend))
                if len(common_shot) > 1 or len(common_yandere) > 1:
                    print('##########################################')
                    print('######', shot_friend_info['first_name'], shot_friend_info['last_name'],
                          "vk.com/" + shot_friend_info["domain"], '######')
                    print('##########################################')
                    findActiveBy(shot=shot_friend, yandere=shot)  # возвращает сумму лайков на аккаунте
                    # print(common_shot)
                    if len(common_shot) > 0:
                        print("Общие друзья shot")
                        for dd in common_shot:
                            inf = vk.users.get(user_ids=dd, fields="domain")[0]
                            print(inf['first_name'], inf['last_name'], "vk.com/" + inf["domain"])
                    if len(common_yandere) > 1:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!0000000"
                              "-------------------------------------------")
                        print("Общие друзья c yandere !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        for dd in common_yandere:
                            inf = vk.users.get(user_ids=dd, fields="domain")[0]
                            print(inf['first_name'], inf['last_name'], "vk.com/" + inf["domain"])
            except ApiError as shit:
                print("ошибка = ", shit)
                continue

        offset += 24
        count -= 24

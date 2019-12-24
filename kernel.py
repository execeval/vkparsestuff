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

countLikes = lambda user_id, js_type, owner_id, item_ids, whl=25: '''
        var i = 0 ;  
        var count = 0;
        var item_ids = %r;
        while(i < %r){
        count = count + API.likes.isLiked({"user_id": %r, "type": \"%r\", "owner_id": %r, "item_id": item_ids[i]})["liked"];
        i = i + 1;
        }
        return count;
        ''' % (str(item_ids), str(whl), str(user_id), str(js_type), str(owner_id))


def findActiveBy(owner, user):
    owner = findId(owner)
    user = findId(user)
    res = 0
    owner_info = vk.users.get(user_ids=owner, name_case='gen')[0]

    user_info = vk.users.get(user_ids=user, name_case='gen')[0]

    print(">Считаем лайки", user_info['first_name'], user_info['last_name'] + '<')

    if owner_info['is_closed'] and not (owner_info['can_access_closed']):
        print("Нет доступа к аккаунту")
        return "full_close"

    wall, photos, saves = False, False, False

    try:
        wall = vk.wall.get(owner_id=owner, count='100')
    except ApiError:
        print("стена закрыта")

    try:
        photos = vk.photos.get(owner_id=owner, album_id="profile", rev="1", count="100")
    except ApiError:
        print("профильные фотки закрыты")

    try:
        saves = vk.photos.get(owner_id=owner, album_id="saved", rev="1", count="100")
    except ApiError:
        print("сохры закрыты")

    if saves:
        saved_likes = 0
        photo_ids = []

        for photo in saves['items']:
            photo_ids.append(photo['id'])

        lenc = len(photo_ids)
        ind = 0

        while lenc > 25:
            saved_likes += int(vk.execute(
                code=countLikes(js_type="photo", item_ids=photo_ids[ind:ind + 25], owner_id=owner, user_id=user)))
            ind += 25
            lenc -= 25

        saved_likes += int(vk.execute(
            code=countLikes(js_type="photo", item_ids=photo_ids[ind:ind + 25], owner_id=owner, user_id=user,
                            whl=lenc)))
        res += saved_likes
        print("Лайкнуто сохров:", saved_likes)

    if photos:
        prof_likes = 0
        photo_ids = []
        for photo in photos['items']:
            photo_ids.append(photo['id'])

        lenc = len(photo_ids)
        ind = 0

        while lenc > 25:
            prof_likes += int(vk.execute(
                code=countLikes(js_type="photo", item_ids=photo_ids[ind:ind + 25], owner_id=owner, user_id=user)))
            ind += 25
            lenc -= 25
        prof_likes += int(vk.execute(
            code=countLikes(js_type="photo", item_ids=photo_ids[ind:ind + 25], owner_id=owner, user_id=user,
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
            wall_likes += int(vk.execute(
                code=countLikes(js_type="post", item_ids=wall_ids[ind:ind + 25], owner_id=owner,
                                user_id=user)))
            ind += 25
            lenc -= 25

        wall_likes += int(vk.execute(
            code=countLikes(js_type="post", item_ids=photo_ids[ind:ind + 25], owner_id=owner, user_id=user,
                            whl=lenc)))
        res += wall_likes
        print("Лайкнуто записей на стене:", wall_likes)
    return res


def deepFriNet(owner):
    owner = findId(owner)
    print(owner)
    info = vk.users.get(user_ids=owner)[0]
    print(info)

    if info['is_closed'] and info['can_access_closed']:
        return "full_close"

    wall, photos, saves = False, False, False
    like_owner_wall = Counter()
    like_owner_photos = Counter()
    like_owner_saved_photos = Counter()

    try:
        wall = vk.wall.get(owner_id=owner, count='100')
    except ApiError:
        return ">стена закрыта"

    try:
        photos = vk.photos.get(owner_id=owner, album_id="profile", rev="1")
    except ApiError:
        return ">профильные фотки закрыты"

    try:
        saves = vk.photos.get(owner_id=owner, album_id="saved", rev="1")
    except ApiError:
        return ">сохры закрыты"

    if saves:
        for photo in saves['items']:
            for likes in vk.likes.getList(ttype="photo", owner_id=owner, item_id=photo["id"])['items']:
                like_owner_saved_photos[likes] += 1

    if photos:
        for photo in photos['items']:
            for likes in vk.likes.getList(ttype="photo", owner_id=owner, item_id=photo["id"])['items']:
                like_owner_photos[likes] += 1

    if wall:
        for post in wall["items"]:
            for likes in vk.likes.getList(ttype="post", owner_id=owner, item_id=post["id"])['items']:
                like_owner_wall[likes] += 1

    d = 0
    return [like_owner_wall.most_common(), like_owner_photos.most_common(), like_owner_saved_photos.most_common()]


def deepFriNet_t(res):
    f = 0
    tittle = ["лайки стены", "лайки профильных фоток", "лайки сохр"]

    for list_user in res:  # [0]-лайки стены [1]-лайки профильных фоток [2]- лайки сохр

        print(tittle[f])
        all_id = []

        for z in list_user: all_id.append(z[0])

        info_list = vk.users.get(user_ids=all_id, fields="domain")

        for i in range(len(list_user)):
            print("❤" + str(list_user[i][1]), info_list[i]['first_name'], info_list[i]['last_name'],
                  "vk.com/" + info_list[i]['domain'], )

        f += 1


def findCommon(owner, user):
    owner = findId(owner)
    user = findId(user)
    user_friend = vk.friends.get(user_id=user)['items']
    owner_friends = vk.friends.get(user_id=owner)['items']
    count = len(owner_friends)
    offset = 0

    while count > 24:
        res = vk.execute(code=userFriends(user=owner, offset=offset))
        for i in range(24):
            try:
                owner_friend = owner_friends[offset + i]
                if str(owner_friend) == str(user):
                    continue
                owner_friend_friends = res[i]
                owner_friend_info = vk.users.get(user_ids=owner_friend, fields="domain")[0]
                common_owner = (set(owner_friend_friends) & set(owner_friends))
                common_user = (set(owner_friend_friends) & set(user_friend))
                if len(common_owner) > 1 or len(common_user) > 1:
                    print('##########################################')
                    print('######', owner_friend_info['first_name'], owner_friend_info['last_name'],
                          "vk.com/" + owner_friend_info["domain"], '######')
                    print('##########################################')
                    findActiveBy(owner=owner_friend, user=owner)  # возвращает сумму лайков на аккаунте
                    if len(common_owner) > 0:
                        print("Общие друзья owner")
                        for dd in common_owner:
                            inf = vk.users.get(user_ids=dd, fields="domain")[0]
                            print(inf['first_name'], inf['last_name'], "vk.com/" + inf["domain"])
                    if len(common_user) > 1:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!0000000"
                              "-------------------------------------------")
                        print("Общие друзья c user !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        for dd in common_user:
                            inf = vk.users.get(user_ids=dd, fields="domain")[0]
                            print(inf['first_name'], inf['last_name'], "vk.com/" + inf["domain"])
            except ApiError as shit:
                print("ошибка = ", shit)
                continue

        offset += 24
        count -= 24


def findId(link):
    link = link.replace("https://", "")
    link = link.replace("http://", "")
    link = link.replace("/", "")
    link = link.replace("vk.com", "")
    if link.isdigit():
        return int(link)
    else:
        return vk.users.get(user_ids=link)[0]['id']

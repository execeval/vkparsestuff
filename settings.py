from vk_api import *
from vk_api.exceptions import *

vk_session = VkApi('login', 'pass')
vk_session.auth()
vk = vk_session.get_api()

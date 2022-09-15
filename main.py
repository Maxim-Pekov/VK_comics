import os
import random
from pprint import pprint
import pathlib

import requests
from pathlib import Path
from urllib.parse import urlparse
from os.path import splitext
from environs import Env


env = Env()
env.read_env()
VK_CLIENT_ID = env.int('VK_CLIENT_ID')
access_token = env.str('access_token')
user_id = env.int('user_id')


def get_extension(img_url):
    parse_result = urlparse(img_url)
    url_path = parse_result.path
    only_path, extension = splitext(url_path)
    return extension


def get_last_comic_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    return response.json().get('num')


def get_random_comic_number():
    x = random.randint(1, get_last_comic_number())
    return x


comic_number = get_random_comic_number()
print(get_random_comic_number())
url = f"https://xkcd.com/{comic_number}/info.0.json"
name_photo = 'commics'
response = requests.get(url)
response.raise_for_status()
img_url = response.json().get('img')
comment = response.json().get('alt')
num = response.json().get('num')
extension = get_extension(img_url)
directory_path = 'files'
pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
x = Path()
outpath = Path() / directory_path / f'{name_photo}{extension}'

pprint(response.json())
response_img = requests.get(img_url)
img_content = response_img.content
print(comment)
with open(outpath, 'wb') as file:
    file.write(img_content)


# vk_url = 'https://api.vk.com/method/groups.get?PARAMS&access_token=TOKEN&v=V'
# params = {
#     'access_token': access_token,
#     'v': 5.131
# }
# response = requests.get(vk_url, params)
# pprint(response.json())
# # pprint(photos.getWallUploadServer)

vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
vk_url_ = 'https://pu.vk.com/c521232/ss2215/upload.php?act=do_add&mid=11096823&aid=-14&gid=0&hash=be410b83cf82f998ce9ed20a17de251a&rhash=eb6d761db23268db167c1529a52a639f&swfupload=1&api=1&wallphoto=1'
params = {
    'album_id': -14,
    'access_token': access_token,
    'v': 5.131
}
response = requests.get(vk_url, params)
pprint(response.json())
# pprint(response.photos.getUploadServer)

with open(outpath, 'rb') as file:
    url = '...'
    files = {
        'photo': file,  # Вместо ключа "media" скорее всего нужно подставить другое название ключа. Какое конкретно см. в доке API ВК.
    }
    response = requests.post(vk_url_, files=files)
    response.raise_for_status()
    resp = response.json()
    pprint(resp)
    print()
    # pprint(response.json().photos.saveWallPhoto)
hash = resp.get('hash')
photo = resp.get('photo')
server = resp.get('server')
print(resp.get('hash'))
print()

paramss = {
    'hash': hash,
    'photo': photo,
    'server': server,
    'album_id': -14,
    'access_token': access_token,
    'v': 5.131
}
vk_url_upload = 'https://api.vk.com/method/photos.saveWallPhoto'
response_upload = requests.post(vk_url_upload, params=paramss)
response_upload.raise_for_status()
x = response_upload.json()
pprint(response_upload.json())
print()

url_post = 'https://api.vk.com/method/wall.post'
owner_id = -215958081
photo_id = x.get('response')[0].get('id')
owner_id_ = x.get('response')[0].get('owner_id')
print('owner_id', owner_id)
print('id', photo_id)
p = {
    'attachments': f'photo{owner_id_}_{photo_id}',
    'album_id': -14,
    'access_token': access_token,
    'v': 5.131,
    'from_group': 215958081,
    'message': comment,
    'owner_id': owner_id

}
response_upload = requests.post(url_post, params=p)
response_upload.raise_for_status()
print()
print('wall.post')
pprint(response_upload.json())
print()
os.remove(outpath)
os.rmdir(directory_path)
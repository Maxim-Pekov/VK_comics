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
directory_path = 'files'
path_photo = ''
comment = ''


def get_extension(img_url):
    parse_result = urlparse(img_url)
    url_path = parse_result.path
    only_path, extension = splitext(url_path)
    return extension


def get_random_comic_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    last_comic_number = response.json().get('num')
    random_comic_number = random.randint(1, last_comic_number)
    return random_comic_number


def fetch_img_url(comic_number):
    url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    img_url = response.json().get('img')
    comment = response.json().get('alt')
    comic_number = response.json().get('num')
    img_info = {}
    img_info['img_url'] = img_url
    img_info['comment'] = comment
    img_info['commic_number'] = comic_number
    return img_info


def safe_image(img_info):
    response_img = requests.get(img_info.get('img_url'))
    extension = get_extension(img_info.get('img_url'))
    comic_number = img_info.get('comic_number')
    name_photo = 'commics'
    pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
    path_photo = Path() / directory_path / f'{name_photo}{comic_number}{extension}'
    img_content = response_img.content
    with open(path_photo, 'wb') as file:
        file.write(img_content)
    return path_photo


def get_upload_server():
    vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'album_id': -14,
        'access_token': access_token,
        'v': 5.131
    }
    response = requests.get(vk_url, params)
    pprint(response.json())
    vk_server_url = response.json().get('response').get('upload_url')
    return vk_server_url

# vk_server_url = 'https://pu.vk.com/c521232/ss2215/upload.php?act=do_add&mid=11096823&aid=-14&gid=0&hash=be410b83cf82f998ce9ed20a17de251a&rhash=eb6d761db23268db167c1529a52a639f&swfupload=1&api=1&wallphoto=1'
def upload_photos_to_server(vk_server_url, path_photo):
    with open(path_photo, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(vk_server_url, files=files)
        response.raise_for_status()
        server_response = response.json()
        pprint(server_response)
        print()
    return server_response


def save_photo_to_album(server_response):
    hash = server_response.get('hash')
    photo = server_response.get('photo')
    server = server_response.get('server')
    params = {
        'hash': hash,
        'photo': photo,
        'server': server,
        'album_id': -14,
        'access_token': access_token,
        'v': 5.131
    }
    vk_url_upload = 'https://api.vk.com/method/photos.saveWallPhoto'
    response_upload = requests.post(vk_url_upload, params=params)
    response_upload.raise_for_status()
    x = response_upload.json()
    pprint(response_upload.json())
    print()
    return x

def post_img(x):
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


def main():
    comic_number = get_random_comic_number()
    img_info = fetch_img_url(comic_number)
    path_photo = safe_image(img_info)
    vk_server_url = get_upload_server()
    server_response = upload_photos_to_server(vk_server_url, path_photo)
    x = save_photo_to_album(server_response)
    post_img(x)
    os.remove(path_photo)
    os.rmdir(directory_path)


if __name__ == '__main__':
    main()
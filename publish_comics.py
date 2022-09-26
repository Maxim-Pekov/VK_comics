import os, random, requests

from pathlib import Path
from environs import Env


def get_random_comic_number():
    url = "https://xkcd.com/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    last_comic_number = response.json().get('num')
    random_comic_number = random.randint(1, last_comic_number)
    return random_comic_number


def fetch_img_info(comic_number):
    url = f"https://xkcd.com/{comic_number}/info.0.json"
    response = requests.get(url)
    response.raise_for_status()
    json_response = response.json()
    img_url = json_response.get('img')
    comment = json_response.get('alt')
    return img_url, comment


def save_image(img_url):
    response_img = requests.get(img_url)
    comic_name = os.path.basename(img_url)
    photo_path = Path() / comic_name
    img_content = response_img.content
    with open(photo_path, 'wb') as file:
        file.write(img_content)
    return photo_path


def get_upload_server(album_id, access_token, v):
    vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    params = {
        'album_id': album_id,
        'access_token': access_token,
        'v': v
    }
    response = requests.get(vk_url, params)
    vk_server_url = response.json().get('response').get('upload_url')
    return vk_server_url


def upload_comic_to_server(vk_server_url, path_photo):
    with open(path_photo, 'rb') as file:
        files = {'photo': file}
        response = requests.post(vk_server_url, files=files)
    response.raise_for_status()
    server_response = response.json()
    hash_number = server_response.get('hash')
    photo = server_response.get('photo')
    server = server_response.get('server')
    return hash_number, photo, server


def save_comic_to_album(hash_number, photo, server, album_id, access_token, v):
    server_params = {
        'hash': hash_number,
        'photo': photo,
        'server': server,
        'album_id': album_id,
        'access_token': access_token,
        'v': v
    }
    vk_url_upload = 'https://api.vk.com/method/photos.saveWallPhoto'
    upload_response = requests.post(vk_url_upload, params=server_params)
    upload_response.raise_for_status()
    server_photo = upload_response.json()
    photo_id = server_photo.get('response')[0].get('id')
    owner_id = server_photo.get('response')[0].get('owner_id')
    return photo_id, owner_id


def post_comic(photo_id, owner_id, comment, album_id, access_token, v, group_id):
    url_post = 'https://api.vk.com/method/wall.post'
    photo_params = {
        'attachments': f'photo{owner_id}_{photo_id}',
        'from_group': group_id,
        'message': comment,
        'owner_id': group_id,
        'album_id': album_id,
        'access_token': access_token,
        'v': v
    }
    upload_response = requests.post(url_post, params=photo_params)
    upload_response.raise_for_status()


def main():
    env = Env()
    env.read_env()
    access_token = env.str('VK_ACCESS_TOKEN')
    group_id = -env.int('GROUP_ID')
    album_id = -14
    v = 5.131
    comic_number = get_random_comic_number()
    img_info = fetch_img_info(comic_number)
    img_url, comment = img_info
    try:
        photo_path = save_image(img_url)
        vk_server_url = get_upload_server(album_id, access_token, v)
        server_response = upload_comic_to_server(vk_server_url, photo_path)
        hash_number, photo, server = server_response
        server_photo = save_comic_to_album(hash_number, photo, server, album_id, access_token, v)
        photo_id, owner_id = server_photo
        post_comic(photo_id, owner_id, comment, album_id, access_token, v, group_id)
    finally:
        os.remove(photo_path)


if __name__ == '__main__':
    main()
import os, random, pathlib, requests

from pathlib import Path
from environs import Env


COMIC_DIRECTORY_PATH = 'files'


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
    comic_number = json_response.get('num')
    img_info = {}
    img_info['img_url'] = img_url
    img_info['comment'] = comment
    img_info['commic_number'] = comic_number
    return img_info


def save_image(img_info):
    response_img = requests.get(img_info.get('img_url'))
    img_url = img_info.get('img_url')
    comic_name = os.path.basename(img_url)
    pathlib.Path(COMIC_DIRECTORY_PATH).mkdir(parents=True, exist_ok=True)
    photo_path = Path() / COMIC_DIRECTORY_PATH / comic_name
    img_content = response_img.content
    with open(photo_path, 'wb') as file:
        file.write(img_content)
    return photo_path


def get_upload_server(params):
    vk_url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(vk_url, params)
    vk_server_url = response.json().get('response').get('upload_url')
    return vk_server_url


def upload_comic_to_server(vk_server_url, path_photo):
    with open(path_photo, 'rb') as file:
        files = {'photo': file}
        response = requests.post(vk_server_url, files=files)
    response.raise_for_status()
    server_response = response.json()
    return server_response


def save_comic_to_album(server_response, params):
    hash_number = server_response.get('hash')
    photo = server_response.get('photo')
    server = server_response.get('server')
    server_params = {
        'hash': hash_number,
        'photo': photo,
        'server': server,
    }
    params.update(server_params)
    vk_url_upload = 'https://api.vk.com/method/photos.saveWallPhoto'
    upload_response = requests.post(vk_url_upload, params=params)
    upload_response.raise_for_status()
    server_photo = upload_response.json()
    return server_photo


def post_comic(server_photo, comment, params, group_id):
    url_post = 'https://api.vk.com/method/wall.post'
    photo_id = server_photo.get('response')[0].get('id')
    owner_id = server_photo.get('response')[0].get('owner_id')
    photo_params = {
        'attachments': f'photo{owner_id}_{photo_id}',
        'from_group': group_id,
        'message': comment,
        'owner_id': group_id
    }
    photo_params.update(params)
    upload_response = requests.post(url_post, params=photo_params)
    upload_response.raise_for_status()


def main():
    env = Env()
    env.read_env()
    access_token = env.str('VK_ACCESS_TOKEN')
    group_id = -env.int('GROUP_ID')
    params = {
        'album_id': -14,
        'access_token': access_token,
        'v': 5.131
    }
    comic_number = get_random_comic_number()
    img_info = fetch_img_info(comic_number)
    photo_path = save_image(img_info)
    vk_server_url = get_upload_server(params)
    server_response = upload_comic_to_server(vk_server_url, photo_path)
    server_photo = save_comic_to_album(server_response, params)
    comment = img_info.get('comment')
    post_comic(server_photo, comment, params, group_id)
    os.remove(photo_path)
    os.rmdir(COMIC_DIRECTORY_PATH)


if __name__ == '__main__':
    main()
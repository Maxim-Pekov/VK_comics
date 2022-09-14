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


url = "https://xkcd.com/info.0.json"
name_photo = 'commics'
response = requests.get(url)
response.raise_for_status()
img_url = response.json().get('img')
comment = response.json().get('alt')
extension = get_extension(img_url)
directory_path = 'files'
pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
x = Path()
outpath = Path() / directory_path / f'{name_photo}{extension}'

# pprint(response.json())
response_img = requests.get(img_url)
img_content = response_img.content
print(comment)
with open(outpath, 'wb') as file:
    file.write(img_content)


vk_url = 'https://api.vk.com/method/groups.get?PARAMS&access_token=TOKEN&v=V'
params = {
    'access_token': access_token,
    'v': 5.131
}
response = requests.get(vk_url, params)
pprint(response.json())
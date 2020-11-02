import requests
from urllib.parse import urljoin
from pprint import pprint
import time
import json
import os
import tqdm

# TOKEN_VK = '----TOKEN_VK----'
# TOKEN_YADISK = '----TOKEN_YADISK----'
API_BASE_URL = 'https://api.vk.com/method/'
V = '5.21'
FOLDER_NAME = 'vk_profile_photo/'
print('Backup app')
token_vk = (input('Введите токен пользователя vk: '))
token_yadisk = input('Введите токен с Полигона Яндекс.Диска: ')


class VKAPIClient:

    def __init__(self, token=token_vk, version=V):
        self.token = token
        self.version = version

    def photos_get_id(self):
        photos_get_id = urljoin(API_BASE_URL, 'photos.get')
        response = requests.get(photos_get_id, params={
            'access_token': self.token,
            'v': self.version,
            'album_id': 'profile',
            'rev': 1,  # порядок сортировки фотографий антихронологический
            'extended': 1,  # дополнительные поля
            'photo_sizes': 1,
            'count': 1000,  # количество записей, которое будет получено
            # 'owner_id': 1111111  # скачать фото у другого пользователя
        })
        return response.json()['response']['items']


class YaUploader:

    def __init__(self, token):
        self.token = token

    def create_folder(self, folder_name):
        HEADERS = {"Authorization": f'OAuth {self.token}'}
        requests.put(
            "https://cloud-api.yandex.net/v1/disk/resources",
            params={"path": folder_name},
            headers=HEADERS
        )
        return folder_name

    def upload(self, file_name, file_url):
        """Указываем путь и даем имя файлу, по url

        файла загружаем его на яндекс диск

        """
        HEADERS = {"Authorization": f'OAuth {self.token}'}
        FILE = file_name
        URL = file_url

        requests.post(
            "https://cloud-api.yandex.net/v1/disk/resources/upload",
            params={"path": FILE, "url": URL},
            headers=HEADERS,
        )
        return file_url, file_name

    def publish(self):
        folder = uploader.create_folder(FOLDER_NAME)
        photos = user.photos_get_id()
        json_list = []
        for photo_info in tqdm.tqdm(photos):
            photo_url = photo_info['sizes'][-1]['src']
            photo_size = photo_info['sizes'][-1]['type']
            likes = photo_info['likes']['count']
            photo_data = photo_info['date']
            upload_time = time.ctime(photo_data).replace(':', ';')
            photo_name = f'{str(likes)}, {upload_time}'

            # print(photo_name)
            # print(photo_url)
            # print(photo_size)
            # print(likes)

            info = {"file_name": photo_name, "size": photo_size}
            json_list.append(info)
            uploader.upload((folder + photo_name + 'jpg'), photo_url)

        with open("info.json", 'w', encoding='utf-8') as f:
            json.dump(json_list, f, indent=1)
        with open('info.json', 'r') as f:
            data = json.load(f)
            print('Информация по файлу:')
            pprint(data)

        print('Измененный Я.диск, куда добавились фотографии:')
        print('https://disk.yandex.ru/client/disk/' + folder)

if __name__ == "__main__":
    user = VKAPIClient()
    # pprint(user.photos_get_id())
    uploader = YaUploader(token_yadisk)
    uploader.publish()
import os, json
import requests
import logging
from tqdm import tqdm

current_file = os.path.basename(__file__)
logger2 = logging.getLogger(current_file)
logger2.setLevel(logging.INFO)

# настройка обработчика и форматировщика для logger2
handler2 = logging.FileHandler(f"{current_file}.log", mode='w')
formatter2 = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
handler2.setFormatter(formatter2)
# добавление обработчика к логгеру
logger2.addHandler(handler2)

logger2.info(f"Testing the custom logger for module {current_file}...")

breed = input('Введите породу собаки')
token = input('token ?')

url = 'https://cloud-api.yandex.net/v1/disk/resources'
params = {'path': f'{breed}/'}
headers = {'Authorization': token}
requests.put(url, params=params, headers=headers)
response = requests.get(f'https://dog.ceo/api/breeds/list/all')

sub_breeds = response.json()['message'][breed]
images_list = []
if len(sub_breeds):
    for sub_breed in sub_breeds:
        try:
            response = requests.get(f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random/1')
            images_list.append(response.json()['message'][0])
        except ConnectionError:
            print("Проверьте подключение к сети.")

else:
    try:
        response = requests.get(f'https://dog.ceo/api/breed/{breed}/images/')
        images_list = response.json()['message']
    except ConnectionError:
        print("Проверьте подключение к сети.")

def upload_file(binary_data, path_destination, replace=False):
    """
    path_destination: Путь к файлу на принимающем Диске
    binary_data: Данные загружаемого контента в бинарном виде
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'https://cloud-api.yandex.net/v1/disk/resources/upload?'
                       f'path={path_destination}&overwrite={replace}', headers=headers).json()
    try:
        requests.put(res['href'], files={'file':binary_data})
        logger2.info(f"upload with result: {response.status_code}")
    except KeyError:
        print(res)

data_list = []
for image_url in tqdm(images_list):
    filename = (breed + '_' + image_url.split('/')[-1])
    data_list.append({'file_name': image_url.split('/')[-1]})
    img_data = requests.get(image_url).content
    upload_file(img_data, f'{breed}/{filename}')

with open("data_list.json", "w") as write_file:
    json.dump(data_list, write_file, indent=4)
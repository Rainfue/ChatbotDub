# --------------------------------------------------
# импортирование библиотек
# для работы с запросами
import requests
# для работы с json
import json
# ключ для запроса на API
from config import API_KEY, API_SECRET, API_URL
# для работы со временем
import time
# для работы с форматом base64
import base64
# для работы с байтовой информацией
from io import BytesIO
# для работы с изображениями
from PIL import Image

# --------------------------------------------------
# реализация класса
# создаем класс для работы с API Kandinsky
class KandinskyAPI:
    # конструктор класса
    def __init__(self):
        # инициализируем ссылку к API
        self.URL = API_URL
        # инициализируем ключи для запроса
        self.AUTH_HEADERS = {
            'X-Key': F'Key {API_KEY}',
            'X-Secret': F'Secret {API_SECRET}',
        }
        
    # метод для проверки доступности API
    def is_available(self) -> bool:
        '''Проверяет, доступна ли API'''
        # пробуем получить ответ
        try:
            # отправляем запрос
            response = requests.get(self.URL + 'key/api/v1/models', 
                                    headers=self.AUTH_HEADERS,
                                    timeout=5)
            # возвращаем True
            return response.status_code == 200
        # если не получилось
        except:
            # возвращаем False
            return False

    # метод для получения ID модели
    def get_model_id(self):
        # получаем информацию про модель
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        # возвращаем id модели
        return response.json()[0]['id']
    
    # метод для генерации изображения
    def generate(self, 
                 prompt: str, 
                 model_id: int, 
                 images: int = 1, 
                 width: int = 512, 
                 heigth: int = 512):

        # создаем словарь для запроса
        params = {
            'type': 'GENERATE',             # тип задачи (нельзя поменять)
            'numImages': images,            # количество изображений (нельзя поменять) 
            'width': width,                 # ширина изображения
            'style': 'UHD',                 # стиль генерации
            'height': heigth,               # высота изображения
            'generateParams': {             # параметры запроса
                'query': f'{prompt}'        # запрос для модели
            }
        }

        # запрос
        data = {
            'model_id': (None, model_id),                               # id модели
            'params': (None, json.dumps(params), 'application/json')    # параметры запроса
        }

        # получаем ответ
        response = requests.post(self.URL + 'key/api/v1/text2image/run',
                                 headers=self.AUTH_HEADERS,
                                 files=data)
        # получаем данные о генерации
        data = response.json()
        # возвращаем UUID запроса
        return data['uuid']

    # метод для проверки готовности сгенерированного изображения
    def check_generation(self,
                         request_id: str,
                         attempts: int = 10, 
                         delay: int = 10):
        # пока не закончатся попытки
        while attempts > 0:
            # обращаемся к генерации по UUID
            response = requests.get(
                self.URL + 'key/api/v1/text2image/status/' + request_id,
                headers = self.AUTH_HEADERS
            )
            # получаем информацию о генерации
            data = response.json()
            # если изображение готово
            if data['status'] == 'DONE':
                # возвращаем изображение в формате base64
                return data['images'][0]
            # если нет, тратим попытку
            attempts -= 1
            # задержка
            time.sleep(delay)
        # если не получилось
        return None


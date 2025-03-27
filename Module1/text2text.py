# --------------------------------------------------
# импортирование библиотек
# API Gigachat
from gigachat import GigaChat
# импортируем API ключи
from config import GIGA_AUTH_KEY, CA_FILE_PATH


# Создаем класс объекта gigachat модели
class GigachatAPI:
    # Конструктор класса
    def __init__(self,
                token: str = GIGA_AUTH_KEY,
                ca_file_path: str = CA_FILE_PATH
                ):
        
        # Создаем объект класса GigaChat
        self.gigachat = GigaChat(
            credentials = token,
            # ca_bundle_file = ca_file_path
            )

    # функция для получения кода доступа
    def get_access_code(self):
        # получаем код доступа
        return self.gigachat.get_token().access_token

    # метод для генерации ответа
    def generate(
            self,
            prompt: str
    ):
        # используем объект класса GigaChat для генерации ответа
        response = self.gigachat.chat(prompt)
        return response.choices[0].message.content


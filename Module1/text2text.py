# --------------------------------------------------
# импортирование библиотек
# API Gigachat
from gigachat import GigaChat
# импортируем API ключи
from config import GIGA_AUTH_KEY


# Создаем класс объекта gigachat модели
class GigachatAPI:
    # Конструктор класса
    def __init__(self,
                token: str = GIGA_AUTH_KEY,
                ):
        
        # Создаем объект класса GigaChat
        self.gigachat = GigaChat(
            credentials = token,
            )

    # метод для получения доступности API
    def is_available(self) -> bool:
        '''Проверяет доступность API'''
        # пробуем получить токен
        try:
            self.gigachat.get_token()
            # если получилось, возвращем True
            return True
        # если не получилось, возвращаем False
        except:
            return False

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
        # возвращаем ответ
        return response.choices[0].message.content

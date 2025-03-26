# --------------------------------------------------
# импортирование библиотек
# фреймворк для инерфейса
import streamlit as st
# импортируем объект с text2imageAPI
from text2image import KandinskyAPI
# модуль для обработки формата изображения
import base64
# для обработки битовой информацией
from io import  BytesIO
# модуль для вывода изображения
from PIL import Image

# --------------------------------------------------
# создание класса с интерфейсом
class MyGUI:
    # конструктор класса
    def __init__(self):
        # класс с text2image моделью
        self.kandinsky = KandinskyAPI()
        # получаем ID модели
        self.model_id = self.kandinsky.get_model_id()
        # заголовок
        self.title = st.title('Интерфейс для взаимодействия с Kandinsky и GigaChat')
        # форма для текстовых запросов
        self.text_area = None
        # кнопка для генерации ответа
        self.generate_bt = None
        # для вывода результатов запроса
        self.see_results = None

    # метод для запуска приложения
    def run(self):
        # создаем поле для ввода текста
        self.text_area = st.text_area('Введите запрос: ')
        # создаем кнопку для генерации
        self.generate_bt = st.button('Отправить')
        
        # если кнопка нажата:
        if self.generate_bt:
            # проверка на введенный текст
            if self.text_area:
                # получаем UUID генерации
                generation_uuid = self.kandinsky.generate(self.text_area, self.model_id)
                # проверяем наличие генерации
                generation_check = self.kandinsky.check_generation(generation_uuid)
                # если генерация готова:
                if generation_check:
                    # раскодируем изображение:
                    image_data = base64.b64decode(generation_check)
                    # получаем фотографию
                    image = Image.open(BytesIO(image_data))
                    # выводим результат генерации   
                    self.see_results = st.image(image)
                # если генерация не готова
                else:
                    # выводим сообщение
                    st.write('Не получилось сгенерировать изображение, попробуйте позже')


if __name__ == '__main__':
    mygui = MyGUI()
    mygui.run()
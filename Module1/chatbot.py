# --------------------------------------------------
# импортирование библиотек
# фреймворк для инерфейса
import streamlit as st

# объекты с моделями:
# объект с text2imageAPI
from text2image import KandinskyAPI
# объект с GigaChatAPI
from text2text import GigachatAPI
# объект с моделью классификации
from mean_classifier import TextClassifier
# объект с резервной моделью
from backup import BackupAssistant

# модуль для обработки формата изображения
import base64
# для обработки битовой информацией
from io import  BytesIO
# модуль для работы с временем
import time
from time import sleep

# --------------------------------------------------
# создание класса с интерфейсом
class MyGUI:
    # конструктор класса
    def __init__(self):
        # инициализируем объекты моделей
        # класс с text2image моделью
        self.kandinsky = KandinskyAPI()
        # класс с text2text моделью
        self.gigachat = GigachatAPI()
        # класс с моделью классификации
        self.classifier = TextClassifier()
        # резервная модель
        self.backup = BackupAssistant()

        # получаем ID модели для text2image
        # если API доступна
        if self.kandinsky.is_available():
            self.model_id = self.kandinsky.get_model_id()
        # интерфейс
        # история чата
        if 'messages' not in st.session_state:
            # создаем пустую историю сообщений
            st.session_state.messages = []
        # сохраняем как аргумент класса
        self.history = st.session_state.messages

    # метод для создания потокового текста
    @staticmethod
    def stream_data(text: str):
        '''Функция для создания потокового текста'''
        for word in text.split():
            yield word + ' '
            sleep(0.02)

    # метод для конвертации изображения в base64
    @staticmethod
    def pil2base64(image):
        # инициализируем класс BytesIO
        buffer = BytesIO()
        # сохраняем изображение в байтовую информацию
        image.save(buffer, format='PNG')
        # возвращаем изображение в формате base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    # метод для проверки доступности API
    def api_is_available(self) -> bool:
        # возвращаем проверку GigaChat и Kandinsky
        return (
            self.kandinsky.is_available() and       # проверка кандинского
            self.gigachat.is_available()            # проверка гигачата
            )
    
    # метод для сохранения сообщения
    def add_message(self, 
                    role: str = 'user', 
                    content: str = None,
                    message_type: str = 'text',
                    label: str = 'text'):
        '''Процедура для сохранения сообщения в историю сообщений'''
        # добавляем сообщение в историю
        self.history.append({
            'role': role,               # роль
            'content': content,         # содержимое
            'type': message_type,        # тип сообщения
            'label': label
        })

    # метод для отображения сообщения
    def display_message(self, message: dict, new_message: bool = False):
        '''Процедура для отображения сообщения в интерфейсе'''
        # получаем роль отправителя
        with st.chat_message(message['role']):
            # проверяем тип сообщения
            if message['type'] =='text':
                # выводим текст
                # если новое сообщение, то используем генератор
                if new_message:
                    st.write_stream(self.stream_data(message['content']))
                # если нет, то просто выводим
                else:
                    st.markdown(message['content'])
                    
            # если это изображение
            elif message['type'] == 'image':
                # пробуем вывести изображение
                try:
                    # выводим изображение
                    st.image(base64.b64decode(message['content']),
                             width=400)
                # если ошибка
                except Exception as e:
                    # выводим ошибку
                    st.error(f'ОШИБКА: {e}')
            # иначе
            else:
                # выводим предупреждение
                st.warning(f'Неизвестный тип сообщения: {message["type"]}')

    # метод для отображения всей истории чата
    def display_history(self):
        '''Процедура для отображения всей истории чата'''
        # проходимся по каждому сообщению в истории
        for message in self.history:
            # выводим сообщение
            self.display_message(message)

    # метод для получения контекста
    def get_context(self, prompt):
        # получаем контекст
        context = [message['content'] for message in self.history if message['type'] == 'text' and message['label'] == 'text']
        # сначала создаем строку с переносами
        context = '\n'.join(context)+f'\n\n{prompt}'

        # возвращаем полный контекст
        return context
    
    # метод для запуска приложения
    def run(self):
        '''Основной метод для работы web-приложения'''
        # кнопка для очистки истории сообщений
        clear_history = st.sidebar.button('🧹 Очистить историю')
        # отображаем всю историю чата
        self.display_history()
        # обработка ввода
        if prompt := st.chat_input('Введите текст для обработки'):
            if not prompt.strip():
                st.warning("Запрос не может быть пустым")
            else:
                # проверяем доступность API
                if self.api_is_available():
                    # получаем метку промпта
                    print(f'prompt: {prompt}')
                    prompt_label = self.classifier.classify(prompt)
                    # добавляем сообщение пользователя в историю
                    self.add_message(role='user', content=prompt, label=prompt_label)
                    # выводим сообщения пользователя (последнее в истории)
                    self.display_message(self.history[-1])

                    # в зависимости от метки подключаем нужную модель
                    if prompt_label == 'image generation':
                        # создаем статус генерации изображения
                        with st.status("🖌️ Генерирую изображение...", expanded=True) as status:
                            # запоминаем время генерации
                            start_time = time.time()
                            # получаем код сгенерированого пример
                            generation_uuid = self.kandinsky.generate(prompt, self.model_id)
                            # ждем пока он сгенерируется
                            generation_check = self.kandinsky.check_generation(generation_uuid)
                            # обновляем статус
                            status.update(label="Готово!", state="complete")

                        # если изображение готово
                        if generation_check:
                            # пробуем сохранить изображение
                            self.add_message(role='AI', 
                                            content=generation_check, 
                                            message_type='image')
                            # выводим ответ
                            self.display_message(self.history[-1])
                            # выводим время генерации
                            st.markdown(f'Время генерации: {(time.time() - start_time):.2f}s')

                    # если метка text answer
                    elif prompt_label == 'text':
                        # получаем контекст чата
                        context = self.get_context(prompt)
                        # получаем ответ
                        response = self.gigachat.generate(context)
                        # добавляем ответ в историю
                        self.add_message(role='AI', content=response)
                        # выводим новое сообщение, используя генератор
                        self.display_message(self.history[-1], new_message=True)

                # если API недоступны
                else:
                    # выводим сообщение об ошибке
                    st.error('API недоступен')
                    st.markdown(
                        self.backup.generate_response(prompt)
                        )




        # если пользователь очистил историю
        if clear_history:
            # очищаем session_state
            st.session_state.messages = []
            # синхронизируем
            self.history = st.session_state.messages
            # обновляем страницу
            st.rerun()


if __name__ == '__main__':
    mygui = MyGUI()
    mygui.run()
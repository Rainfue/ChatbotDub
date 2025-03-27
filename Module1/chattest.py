import streamlit as st
from text2image import KandinskyAPI
#
from text2text import GigachatAPI
#
from mean_classifier import TextClassifier


import base64
from io import BytesIO
from PIL import Image
# для работы со временем
import time

classifier = TextClassifier()
gigachat = GigachatAPI()
kandinsky = KandinskyAPI()
model_id = kandinsky.get_model_id()

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Функция для конвертации изображения в base64
def pil_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Функция для отображения истории
def display_message(message):
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            st.markdown(message["content"])
        elif message["type"] == "image":
            img_bytes = base64.b64decode(message["content"])
            st.image(img_bytes, width=400)

# Отображаем всю историю
for message in st.session_state.messages:
    display_message(message)

# Обработка ввода
if prompt := st.chat_input("Ваш вопрос..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "type": "text"
    })
    with st.chat_message('user'):
        st.markdown(prompt)

    prompt_label = classifier.classify(prompt)
    print(prompt_label)
    if prompt_label == "text answer":
        context = [message['content'] for message in st.session_state.messages if message["type"] == "text"]
        context.append(prompt)
        response = gigachat.generate('\n'.join(context))
        # Добавляем текстовый ответ
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "type": "text"
        })

    elif prompt_label == "image generation":
        with st.status("🖌️ Генерирую изображение...", expanded=True) as status:
            # запоминаем время
            start_time = time.time()
            # Генерация изображения
            generation_uuid = kandinsky.generate(prompt, model_id)
            generation_check = kandinsky.check_generation(generation_uuid)
            status.update(label="Готово!", state="complete")
            
        if generation_check:
            try:
                # Конвертируем в base64 и сохраняем
                # image_data = base64.b64decode(generation_check)
                # image = Image.open(BytesIO(image_data))
                # image_base64 = pil_to_base64(image)
                
                # Сохраняем изображение в историю
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": generation_check,
                    "type": "image"
                })
                
                # Добавляем текстовый ответ
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Сгенерировано по запросу: {prompt} ({time.time() - start_time:.2f}s)",
                    "type": "text"
                })
                
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")
        else:
            st.error("Ошибка генерации изображения")
    
    # Принудительно обновляем интерфейс
    st.rerun()

if st.sidebar.button("🧹 Очистить историю"):
    st.session_state.messages = []
    st.rerun()
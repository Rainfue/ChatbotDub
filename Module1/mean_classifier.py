# --------------------------------------------------
# импорт библиотек
# функция для использования модели классификации
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
# модуль для работы с массивами
import numpy as np

# --------------------------------------------------
# реализуем модель zero-hot encoding
class TextClassifier():
    # конструктор класса
    def __init__(self):
        # имя модели классификации (zero-hot classifier)
        self.model_name = 'symanto/xlm-roberta-base-snli-mnli-anli-xnli'
        # модель классификации
        self.classifier = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        # токенизатор
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        # метки
        self.labels = ['image', 'text']
        
    # модуль для классификации текста
    def classify(self,
                 text: str) -> str:
        # Токенизация с явным указанием меток
        inputs = self.tokenizer(
            [text] * len(self.labels),  # Текст повторяется
            text_pair=self.labels,       # Список меток
            return_tensors='pt',
            padding=True,
            truncation=True
        )
        
        # Получаем логиты для entailment (подтверждение)
        with torch.no_grad():
            outputs = self.classifier(**inputs)
        logits = outputs.logits[:, 0]  # Берем только entailment
        
        # Нормализуем для двух меток
        probs = torch.softmax(logits, dim=0)

        pred_idx = torch.argmax(probs).item()

        return self.labels[pred_idx]

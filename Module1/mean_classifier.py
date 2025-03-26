# --------------------------------------------------
# импорт библиотек
# функция для использования модели классификации
from transformers import pipeline


# --------------------------------------------------
# реализуем модель zero-hot encoding
class TextClassifier():
    # конструктор класса
    def __init__(self):
        # инициализируем модель классификации
        self.classifier = pipeline('zero-shot-classification', 
                                   model='symanto/xlm-roberta-base-snli-mnli-anli-xnli')
        
    # модуль для классификации текста
    def classify(self,
                 text: str) -> str:
        
        # получаем словарь с результатами классификации
        result = self.classifier(text, candidate_labels=['image generation', 'text answer'])
        # преобразуем в нужный нам словарь
        scores = {label: scores for label, scores in zip(result['labels'], result['scores'])}
        # находим максимальую уверенность
        max_score = max(scores.values())
        # возвращаем соответсвующую метку
        return next((label for label, score in scores.items() if score == max_score), None)

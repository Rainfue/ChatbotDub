# backup_model.py
import random

class BackupAssistant:
    '''Локальный помощник для диагностики сети'''
    
    def __init__(self):
        self.troubleshooting_steps = [
            '- Проверьте подключение кабеля к роутеру',
            '- Перезагрузите роутер',
            '- Убедитесь, что авиарежим выключен',
            '- Проверьте настройки DNS'
        ]
        
        self.keyword_triggers = {
            'интернет': 'network',
            'сеть': 'network',
            'роутер': 'network',
            'wi-fi': 'network',
            'подключение': 'network'
        }

    def is_network_issue(self, text: str) -> bool:
        '''Определяет, относится ли запрос к проблемам сети'''
        text_lower = text.lower()
        return any(keyword in text_lower 
                  for keyword in self.keyword_triggers.keys())
                  
    def generate_response(self, text: str) -> str:
        '''Генерирует ответ для проблем с сетью'''
        if self.is_network_issue(text):
            steps = '\n'.join(random.sample(self.troubleshooting_steps, 3))
            return (
                '🔧 Кажется, у вас проблемы с интернетом. '
                f'Попробуйте:\n{steps}\n'
                'Если это не поможет, обратитесь к провайдеру.'
            )
        return '⚠️ Основные сервисы недоступны. Повторите запрос позже.'
    
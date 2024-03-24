import requests
from transformers import AutoTokenizer
import logging
from config import URl, MAX_TOKENS, temperature, MAX_SESSIONS_TOKENS, SYSTEM_PROMPT, modes, HEADERS, FOLDER_ID

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class GPT:
    def __init__(self):
        self.URL = URl
        self.MAX_TOKENS = MAX_TOKENS
        self.assistant_content = "Сценарий:\n"

    @staticmethod
    def count_tokens(prompt):
        data = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
            "maxTokens": MAX_SESSIONS_TOKENS,
            "text": prompt
        }
        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=HEADERS
            ).json()['tokens']
    )
    def process_resp(self, response) -> [bool, str]:
        # Проверка статус кода
        if response.status_code < 200 or response.status_code >= 300:
            self.clear_history()
            logging.error(response.text)
            return False, f"Ошибка: {response.status_code}"

        # Проверка json
        try:
            full_response = response.json()
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        # Проверка сообщения об ошибке
        try:
            if "error" in full_response or 'choices' not in full_response:
                self.clear_history()
                logging.error(full_response)
                return False, f"Ошибка: {full_response}"
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        result = full_response["result"]["alternatives"][0]["message"]["text"]

        # Пустой результат == объяснение закончено
        if result == "" or result is None:
            logging.info("Закончено")
            self.clear_history()
            return True, "Объяснение закончено"

        # Сохраняем сообщение в историю
        self.save_history(result)
        return True, self.assistant_content

    def make_prompt(self, data, mode, used_tokens=0):
        json = {
            "modelUri": self.URL,
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": MAX_SESSIONS_TOKENS - used_tokens,
            },
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": modes[mode] + f"Главный герой - {data['person']} в жанре {data['genre']}. Место событий - {data['location']}"},
                {"role": "assistant", "content": self.assistant_content}
            ]
        }
        logging.info("Промпт создан")
        tokens = self.count_tokens(json['messages'][0]['content'] + json['messages'][1]['content'] + json['messages'][2]['content'])
        return json, tokens

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=self.URL, headers=self.HEADERS, json=json)
        logging.info("Запрос отправлен")
        return resp

    # Сохраняем историю общения
    def save_history(self, content_response):
        self.assistant_content += content_response
        logging.info("История сохранена")

    # Очистка истории общения
    def clear_history(self):
        self.assistant_content = "Сценарий:\n"
        logging.info("История очищена")
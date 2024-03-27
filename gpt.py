import requests
import logging
from config import URL, MAX_TOKENS, TEMPERATURE, MAX_SESSIONS_TOKENS, SYSTEM_PROMPT, MODES, HEADERS, FOLDER_ID, YAURL
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class GPT:
    def __init__(self):
        self.url = URL
        self.MAX_TOKENS = MAX_TOKENS
        self.assistant_content = "Сценарий:\n"

    @staticmethod
    def count_tokens(prompt):
        data = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
            "text": prompt
        }
        return len(
            requests.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
                json=data,
                headers=HEADERS
            ).json()['tokens']
    )
    def process_resp(self, response, data=None) -> [bool, str]:
        if data != None:
            logging.info(f"Запрос: {response}")
            logging.info(f"Статус запроса: {response.status_code}")

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
            if "error" in full_response or "result" not in full_response or "alternatives" not in full_response['result']:
                self.clear_history()
                logging.error(full_response)
                if data != None:
                    return False, f"Ошибка: {full_response}", f"Cтатус запроса: {response.status_code}"
                else:
                    return False, f"Ошибка: {full_response}"
        except:
            self.clear_history()
            return False, "Ошибка получения JSON"

        result = full_response["result"]["alternatives"][0]["message"]["text"]

        # Пустой результат == объяснение закончено
        if result is None or result == "":
            logging.info("Закончено")
            self.clear_history()
            if data!=None:
                return True, "Объяснение закончено", f"Cтатус запроса: {response.status_code}"
            else:
                return True, "Объяснение закончено"

        # Сохраняем сообщение в историю
        self.save_history(result)
        if data != None:
            return True, self.assistant_content, f"Cтатус запроса: {response.status_code}"
        else:
            return True, self.assistant_content

    def make_prompt(self, data, mode, used_tokens=0):
        json = {
            "modelUri": URL,
            "completionOptions": {
                "stream": False,
                "temperature": TEMPERATURE,
                "maxTokens": MAX_SESSIONS_TOKENS - used_tokens,
            },
            "messages": [
                {"role": "system", "text": SYSTEM_PROMPT}, 
                {"role": "user", "text": MODES[mode] + f"Главный герой - {data['person']} в жанре {data['genre']}. Место событий - {data['location']}"},
                {"role": "assistant", "text": self.assistant_content}
            ]
        }
        print(json)
        logging.info("Промпт создан")
        tokens = self.count_tokens(json['messages'][0]['text'] + json['messages'][1]['text'] + json['messages'][2]['text'])
        return json, tokens

    # Отправка запроса
    def send_request(self, json):
        resp = requests.post(url=YAURL, headers=HEADERS, json=json)
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

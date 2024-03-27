TOKEN = ""

APITOKEN = ""

ABOUTS = "Я бот сценарист, который напишет самый лучший сценарий"

FOLDER_ID = ""

DB_NAME = 'data.db'

TABLE_NAME = 'users'
TABLE_HISTORY = 'history'

YAURL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

URL = f'gpt://{FOLDER_ID}/yandexgpt-lite'

MAX_TOKENS = 30

TEMPERATURE = 0.6

MAX_SESSIONS = 2
MAX_SESSIONS_TOKENS = 20

CONTINUE_STORY = "Продолжи сюжет и оставь интригу. Ничего не поясняй"

END_STORY = 'Напиши завершение истории c неожиданной развязкой. Ничего не поясняй'

MODES = {
    "continue": "Продолжи сюжет и оставь интригу. Ничего не поясняй",
    "end": "Напиши завершение истории c неожиданной развязкой. Ничего не поясняй",
    "begin": "Начинаем с нуля. Ничего не поясняй"
}

SYSTEM_PROMPT = ("Ты пишешь историю вместе с человеком. Пишете историю по очереди."
                 "Начинает человек, а ты продолжаешь. При необходимости, "
                 "ты можешь дополнять текст диалогами, но добавляй их с новой строки и отделяй"
                 "знаком тире. Ничего не поясняй.")

HEADERS = {
    'Authorization': f'Bearer {APITOKEN}',
    'Content-Type': 'application/json'
}
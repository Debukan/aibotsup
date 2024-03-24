TOKEN = ""

APITOKEN = ""

ABOUTS = "Я бот сценарист, который напишет самый лучший сценарий"

FOLDER_ID = ""

db_name = 'data.db'

table_name = 'users'
table_history = 'history'

URl = f'gpt://{FOLDER_ID}/yandexgpt-lite'

MAX_TOKENS = 500

temperature = 0.6

MAX_SESSIONS = 2
MAX_SESSIONS_TOKENS = 100

CONTINUE_STORY = "Продолжи сюжет и оставь интригу. Ничего не поясняй"

END_STORY = 'Напиши завершение истории c неожиданной развязкой. Ничего не поясняй'

modes = {
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
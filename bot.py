import telebot
import logging
import config
from gpt import GPT
from data_base import DataBase

gpt = GPT()
db = DataBase()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

bot = telebot.TeleBot(token=config.TOKEN)

logging.info("Бот начал работу")

# все команды бота
bot.set_my_commands([
    telebot.types.BotCommand('start', 'Начать'),
    telebot.types.BotCommand('help', 'Помощь'),
    telebot.types.BotCommand('about', 'Расскажу о себе'),
    telebot.types.BotCommand('continue', 'Продолжить сценарий'),
    telebot.types.BotCommand('begin', 'Начать генерацию сценария'),
    telebot.types.BotCommand('change_person', 'Сменить персонажа'),
    telebot.types.BotCommand('change_genre', 'Сменить жанр'),
    telebot.types.BotCommand('change_location', 'Сменить локацию'),
    telebot.types.BotCommand('end', 'Закончить сценарий'),
])

db.create_table()
db.create_table_history()
db.create_table_token_usage()
db.insert_token_usage_data(0)

logging.info("Бот подготовился")
print("Бот подготовлен")

# список команд для команды help
commands = {
    '/start': 'Начать общение с ботом',
    '/help': 'Показать все команды',
    '/about': 'Расскажу о себе',
    '/continue': 'Продолжить сценарий',
    '/begin': 'Начать генерацию сценария',
    '/end': 'Закончить сценарий',
    '/change_person': 'Сменить персонажа',
    '/change_genre': 'Сменить жанр',
    '/change_location': 'Сменить локацию'
}


# функция для проверки выбора параметров пользователем
def check_parameters(message):
    data = db.get_data_for_user(get_id(message))
    if data['person'] == "":
        change_person(message)
    elif data['genre'] == "":
        change_genre(message)
    elif data['location'] == "":
        change_location(message)
    return data


# проверяет есть ли пользователь. Сбрасывает данные
def user_check(message):
    user_id = get_id(message)
    db.add_user(user_id, message.from_user.first_name)
    data = db.get_data_for_user(user_id)
    return data


# возвращает id пользователя
def get_id(message):
    return int(message.chat.id)


def make_keyboard(num=2):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if num == 1:
        button1 = telebot.types.InlineKeyboardButton(text='Новый сценарий', callback_data="begin")
        keyboard.add(button1)
    elif num == 2:
        button1 = telebot.types.InlineKeyboardButton(text='Новый сценарий', callback_data="begin")
        button2 = telebot.types.InlineKeyboardButton(text='Продолжить генерацию', callback_data="continue")
        keyboard.add(button1, button2)
    elif num == 3:
        button1 = telebot.types.InlineKeyboardButton(text='Новый сценарий', callback_data="begin")
        button2 = telebot.types.InlineKeyboardButton(text='Продолжить генерацию', callback_data="continue")
        button3 = telebot.types.InlineKeyboardButton(text='Закончить сценарий', callback_data="end")
        keyboard.add(button1, button2, button3)
    return keyboard


# создание клавиатуры для выбора жанра
def make_genre_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton('Фантастика')
    button2 = telebot.types.KeyboardButton('Детектив')
    button3 = telebot.types.KeyboardButton('Комедия')
    keyboard.add(button1, button2, button3)
    return keyboard


# создание клавиатуры для выбора персонажа
def make_person_keyboard(): 
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton('Вася')
    button2 = telebot.types.KeyboardButton('Саня')
    button3 = telebot.types.KeyboardButton('Маша')
    button4 = telebot.types.KeyboardButton('Вика')
    keyboard.add(button1, button2, button3, button4)
    return keyboard


# создание клавиатуры для выбора локации
def make_location_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton('Золотой дворец')
    button2 = telebot.types.KeyboardButton('Подземелье')
    button3 = telebot.types.KeyboardButton('Лес')
    keyboard.add(button1, button2, button3)
    return keyboard


# обработки команды start
@bot.message_handler(commands=['start'])
def start_message(message):
    data = user_check(message)
    bot.send_message(message.chat.id,'Привет')
    bot.send_message(message.chat.id, "Напиши /help для помощи!")
    data = check_parameters(message)
 

# обработка команды help
@bot.message_handler(commands=['help'])
def help_message(message):
    text = "Вот список команд, которые я могу выполнить:\n"
    for command, description in commands.items():
        text += f'{command} - {description}\n'
    bot.send_message(message.chat.id, text)


# обработка команды about
@bot.message_handler(commands=['about'])
def about_message(message):
    bot.send_message(message.chat.id, config.ABOUTS)


# обработка нажатия на кнопку со сменой персонажа
@bot.message_handler(func=lambda message: message.text in ['Вася', 'Саня', 'Маша', 'Вика'])
def change_person_callback(message):
    data = db.get_data_for_user(get_id(message))
    user_id = get_id(message)
    if message.text in ['Вася', 'Саня', 'Маша', 'Вика']:
        db.update_data(user_id, 'person', message.text)
    else:
       bot.send_message(message.chat.id, "Нет такого персонажа")
    logging.info("Смена персонажа произведена")
    bot.send_message(message.chat.id, "Персонаж успешно выбран.")
    check_parameters(message)
    

# обработка команды change_pearson для смены персонажа
@bot.message_handler(commands=['change_person'])
def change_person(message):
    data = db.get_data_for_user(get_id(message))
    keyboard = make_person_keyboard()
    bot.send_message(message.chat.id, 'Выберите персонажа', reply_markup=keyboard)
    bot.register_next_step_handler(message, change_person_callback)
    
    
# обработка нажатия на кнопку со сменой жанра
@bot.message_handler(func=lambda message: message.text in ['Фантастика', 'Детектив', 'Комедия'])
def change_genre_callback(message):
    data = db.get_data_for_user(get_id(message))
    user_id = get_id(message)
    if message.text in ['Фантастика', 'Детектив', 'Комедия']:
        db.update_data(user_id, 'genre', message.text)
    else:
        bot.send_message(message.chat.id, "Нет такого жанра")
    logging.info("Смена жанра произведена")
    bot.send_message(message.chat.id, "Жанр успешно выбран.")
    check_parameters(message)
    

# обработка команды change_genre для смены жанра задачи
@bot.message_handler(commands=['change_genre'])
def change_genre(message):
    data = db.get_data_for_user(get_id(message))
    keyboard = make_genre_keyboard()
    bot.send_message(message.chat.id, 'Выберите жанр', reply_markup=keyboard)
    bot.register_next_step_handler(message, change_genre_callback)


# обработка нажатия на кнопку со сменой локации
@bot.message_handler(func=lambda message: message.text in ['Золотой дворец', 'Подземелье', 'Лес'])
def change_location_callback(message):
    data = db.get_data_for_user(get_id(message))
    user_id = get_id(message)
    if message.text in ['Золотой дворец', 'Подземелье', 'Лес']:
        db.update_data(user_id, 'location', message.text)
    else:
        bot.send_message(message.chat.id, "Нет такой локации")
    logging.info("Смена локации произведена")
    bot.send_message(message.chat.id, "Локация успешно выбрана.")
    bot.send_message(message.chat.id, "Теперь можно начать сюжет через команду /begin")


# обработка команды для смены локации
@bot.message_handler(commands=['change_location'])
def change_location(message):
    data = db.get_data_for_user(get_id(message))
    keyboard = make_location_keyboard()
    bot.send_message(message.chat.id, 'Выберите локацию', reply_markup=keyboard)
    bot.register_next_step_handler(message, change_location_callback)


#отправка файла с логами
@bot.message_handler(commands=['debug'])
def send_logs(message):
    logging.info("Файл был отправлен")
    with open("log_file.log", "rb") as f:
        bot.send_document(message.chat.id, f)


# включение debug_mode
@bot.message_handler(commands=['debug_mode'])
def debug_mode(message):
    data = db.get_data_for_user(get_id(message))
    if data['debug_mode'] == 1:
        db.update_data(get_id(message), 'debug_mode', 0)
        bot.send_message(message.chat.id, "Debug mode отключен")
        logging.info("Debug mode отключен")
    else:
        db.update_data(get_id(message), 'debug_mode', 1)
        bot.send_message(message.chat.id, "Debug mode включен")
        logging.info("Debug mode включен")


# обработка нажатия на кнопку begin
@bot.callback_query_handler(func=lambda call: call.data in ['begin'])
def begin_callback_handler(call):
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    begin_handler(call.message)
    

@bot.message_handler(commands=['begin'])
def begin_handler(message):
    data = user_check(message)
    user_id = get_id(message)
    tokens = db.get_token_usage()
    if data['session_number'] >= config.MAX_SESSIONS:
        bot.send_message(message.chat.id, "Достигнут лимит сессий")
        return
    elif tokens >= config.MAX_TOKENS:
        bot.send_message(message.chat.id, "Достигнут лимит токенов бота. Генерация сценариев завершена.")
        return
    else:
        db.update_data(user_id, 'session_number', data['session_number'] + 1)
        db.update_data(user_id, 'prompt_active', 1)
        db.update_data(user_id, 'session_tokens', 0)
        bot.send_message(message.chat.id, "Выполняю запрос")
        gpt.clear_history()
        json, token1 = gpt.make_prompt(data, "begin")
        full_response = gpt.send_request(json)
        if data['debug_mode'] == 1:
            response = gpt.process_resp(full_response, data)
        else:
            response = gpt.process_resp(full_response)
        db.update_gpt(user_id, gpt.assistant_content)
        if not response[0]:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            bot.send_message(message.chat.id, response[1])
            logging.error(response[1])
        else:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            keyboard = make_keyboard(3)
            db.add_history(user_id, message.from_user.first_name, json['messages'][1]['text'], response[1])
            db.update_data(user_id, "session_tokens", data['session_tokens'] + gpt.count_tokens(response[1]))
            db.update_data(user_id, "tokens", data['tokens'] + gpt.count_tokens(response[1]))
            db.update_usage_token(db.get_token_usage() + gpt.count_tokens(response[1]) + token1)
            bot.send_message(message.chat.id, response[1], reply_markup=keyboard)
            logging.info("Бот закончил объяснение")


# обработка нажатия на кнопку end
@bot.callback_query_handler(func=lambda call: call.data in ['end'])
def begin_callback_handler(call):
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    end_handler(call.message)


@bot.message_handler(commands=['end'])
def end_handler(message):
    data = user_check(message)
    user_id = get_id(message)
    bot.send_message(message.chat.id, "Завершаю сценарий")
    if data['prompt_active']:
        if data['session_tokens'] >= config.MAX_SESSIONS_TOKENS:
            bot.send_message(message.chat.id, "Достигнут лимит токенов. Начните новый сценарий.")
            return
        if data['tokens'] >= config.MAX_TOKENS:
            bot.send_message(message.chat.id, "Достигнут лимит токенов бота. Генерация сценариев завершена.")
            return
        bot.send_message(message.chat.id, "Выполняю запрос")
        json, token1 = gpt.make_prompt(data, "end", data['session_tokens'])
        full_response = gpt.send_request(json)
        if data['debug_mode'] == 1:
            response = gpt.process_resp(full_response, data)
        else:
            response = gpt.process_resp(full_response)
        db.update_gpt(user_id, gpt.assistant_content)
        if response[1] == "Объяснение закончено":
            logging.info("Бот закончил объяснение")
            db.add_history(user_id, message.from_user.first_name, json['messages'][1]['text'], response[1])
            db.update_usage_token(db.get_token_usage() + gpt.count_tokens(response[1]))
            db.update_data(user_id, "prompt_active", 0)
            db.update_data(user_id, "session_tokens", data['session_tokens'] + gpt.count_tokens(response[1]))
            db.update_data(user_id, "tokens", data['tokens'] + gpt.count_tokens(response[1]))
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            keyboard = make_keyboard(1)
            bot.send_message(message.chat.id, response[1], reply_markup=keyboard)
            bot.send_message(message.chat.id, "Интересный сценарий получился")
        elif not response[0]:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            bot.send_message(message.chat.id, response[1])
            logging.error(response[1])
        else:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            keyboard = make_keyboard(1)
            bot.send_message(message.chat.id, response[1], reply_markup=keyboard)
            db.update_usage_token(db.get_token_usage() + gpt.count_tokens(response[1]) + token1)
            db.add_history(user_id, message.from_user.first_name, json['messages'][1]['text'], response[1])
            bot.send_message(message.chat.id, "Интересный сценарий получился")
            db.update_data(user_id, "prompt_active", 0)
            db.update_data(user_id, "session_tokens", data['session_tokens'] + gpt.count_tokens(response[1]))
    else:
        bot.send_message(message.chat.id, "У вас нет активного запроса.")
    

# обработка нажатия на кнопку continue
@bot.callback_query_handler(func=lambda call: True and call.data == "continue")
def call_back_continue(call):
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    continue_handler(call.message)


# функция продолжения запроса
@bot.message_handler(commands=['continue'])
def continue_handler(message):
    user_id = get_id(message)
    data = user_check(message)
    if data['prompt_active']:
        if data['session_tokens'] >= config.MAX_SESSIONS_TOKENS:
            bot.send_message(message.chat.id, "Достигнут лимит токенов. Начните новый сценарий.")
            return
        if data['tokens'] >= config.MAX_TOKENS:
            bot.send_message(message.chat.id, "Достигнут лимит токенов бота. Генерация сценариев завершена.")
            return
        bot.send_message(message.chat.id, "Выполняю запрос")
        json, token1 = gpt.make_prompt(data, "continue", data['session_tokens'])
        full_response = gpt.send_request(json)
        if data['debug_mode'] == 1:
            response = gpt.process_resp(full_response, data)
        else:
            response = gpt.process_resp(full_response)
        db.update_gpt(user_id, gpt.assistant_content)
        if response[1] == "Объяснение закончено":
            logging.info("Бот закончил объяснение")
            db.add_history(user_id, message.from_user.first_name, json['messages'][1]['text'], response[1])
            db.update_usage_token(db.get_token_usage() + gpt.count_tokens(response[1]))
            db.update_data(user_id, "prompt_active", 0)
            db.update_data(user_id, "session_tokens", data['session_tokens'] + gpt.count_tokens(response[1]))
            db.update_data(user_id, "tokens", data['tokens'] + gpt.count_tokens(response[1]))
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            keyboard = make_keyboard(1)
            bot.send_message(message.chat.id, response[1], reply_markup=keyboard)
        elif not response[0]:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            bot.send_message(message.chat.id, response[1])
            logging.error(response[1])
        else:
            if data['debug_mode'] == 1:
                bot.send_message(message.chat.id, response[2])
            keyboard = make_keyboard(3)
            bot.send_message(message.chat.id, response[1], reply_markup=keyboard)
            db.update_usage_token(db.get_token_usage() + gpt.count_tokens(response[1]) + token1)
            db.update_data(user_id, "session_tokens", data['session_tokens'] + gpt.count_tokens(response[1]))
            db.add_history(user_id, message.from_user.first_name, json['messages'][1]['text'], response[1])
            logging.info("Бот успешно выполнил запрос")
    else:
        bot.send_message(message.chat.id, "У вас нет активного запроса.")


# обработка текстовых запросов
@bot.message_handler(content_types=['text'])
def text_func(message):
    bot.send_message(message.chat.id, "Я тебя не понял!")


bot.polling()
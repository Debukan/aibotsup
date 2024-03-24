import sqlite3
import logging
import os
from config import db_name, table_name

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.log",
    filemode="a",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class DataBase:
    def __init__(self):
        self.conn = None

    # подготовка базы данных
    def prepare_db(self):
        try:
            self.conn = sqlite3.connect(db_name, check_same_thread=False)
            logging.info("Database is ready")
        except Exception as e:
            logging.error(e)


    # функция для отправки запроса
    def execute_query(self, sql_query, data=None):
        logging.info(f"DATABASE: Execute query: {sql_query}")

        cursor = self.conn.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)

        self.conn.commit()
        logging.info(f"DATABASE: Query executed successfully")


    # Функция для выполнения любого sql-запроса для получения данных (возвращает значение)
    def execute_selection_query(self, sql_query, data=None):
        logging.info(f"DATABASE: Execute query: {sql_query}")

        cursor = self.conn.cursor()

        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        rows = cursor.fetchall()
        logging.info(f"DATABASE: Query executed successfully")
        return rows


    # создание таблицы users
    def create_table(self):
        cursor = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            answer TEXT DEFAULT '',
            prompt TEXT DEFAULT '',
            prompt_active INTEGER DEFAULT 0,
            person TEXT DEFAULT '',
            genre TEXT DEFAULT '',
            location TEXT DEFAULT '',
            session_number INTEGER DEFAULT 0,
            session_tokens INTEGER DEFAULT 0,
            tokens INTEGER DEFAULT 0
        );
        """
        cursor.execute(create_table_query)
        self.conn.commit()
        logging.info(f"DATABASE: Table created")
    

    # создание таблицы history
    def create_table_history(self):
        cursor = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            prompt TEXT,
            answer TEXT
        );
        """
        cursor.execute(create_table_query)
        self.conn.commit()
        logging.info(f"DATABASE: History table created")


    # создание таблицы token_usage
    def create_table_token_usage(self):
        cursor = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY,
            number INTEGER DEFAULT 1,
            tokens INTEGER DEFAULT 0
        );
        """
        cursor.execute(create_table_query)
        self.conn.commit()
        logging.info(f"DATABASE: Token usage table created")


    # обновление значения в таблице users
    def update_data(self, user_id, column, value):
        cursor = self.conn.cursor()
        update_table_query = f"""
        UPDATE users SET {column} = ? WHERE user_id = ?;
        """
        cursor.execute(update_table_query, (value, user_id))
        self.conn.commit()
        logging.info(f"DATABASE: Table updated")


    # вставка значения в таблицу users
    def insert_data(self, user_id, subject, value):
        cursor = self.conn.cursor()
        insert_data_query = f"""
        INSERT INTO users ({subject})
        SELECT ?
        WHERE NOT EXISTS (SELECT * FROM users WHERE user_id = ?);
        """
        cursor.execute(insert_data_query, (value, user_id))
        self.conn.commit()
        logging.info(f"DATABASE: Data inserted")


    # добавление пользователя в базу данных
    def add_user(self, user_id, username = "", answer = "", prompt = "", prompt_active = 0, person = "", genre = "", location = "", session_number=0, session_tokens=0, tokens=0):
        add_user_query = f"""
        INSERT INTO users(user_id, username, answer, prompt, prompt_active, person, genre, location, session_number, session_tokens, tokens)
        SELECT ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE user_id = ?);
        """
        self.execute_query(add_user_query, [user_id, username, answer, prompt, prompt_active, person, genre, location, session_number, session_tokens, tokens, user_id])
        logging.info(f"DATABASE: User added")


    # проверка есть ли такой столбец в таблице users
    def is_value_in_table(self, column_name, value):
        sql_query = f'SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {column_name} = ?)'
        rows = self.execute_selection_query(sql_query, [value])
        return len(rows) > 0


    # получение словаря с данными пользователя из базы данных
    def get_data_for_user(self, user_id):
        if self.is_value_in_table('user_id', user_id):
            sql_query = f'SELECT *' \
                        f'FROM {table_name} WHERE user_id = ? LIMIT 1'
            row = self.execute_selection_query(sql_query, [user_id])[0]
            result = {
                "username": row[2],
                "answer": row[3],
                "prompt": row[4],
                "prompt_active": row[5],
                "person": row[6],
                "genre": row[7],
                "location": row[8],
                "session_number": row[9],
                "session_tokens": row[10],
                "tokens": row[11]
            }
            logging.info(f"DATABASE: The data has been returned")
            return result
        else:
            logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
            self.add_user(user_id)
            return {
                "username": "",
                "answer": "",
                "prompt": "",
                "prompt_active": 0,
                "person": "",
                "genre": "",
                "location": "",
                "session_number": 0,
                "session_tokens": 0,
                "tokens": 0,
            }


    # проверка есть ли такой пользователь в базе данных
    def user_exists(self, user_id):
        if not self.is_value_in_table('user_id', user_id):
            logging.info(f"DATABASE: Пользователь с id = {user_id} не найден")
            self.add_user(user_id)
            return True
        return False


    # обновление столбца в таблице users
    def update_gpt(self, user_id, answer):
        data = self.get_data_for_user(user_id)
        answer2 = data["answer"] + answer
        self.update_data(user_id, "answer", answer2)
        logging.info(f"DATABASE: Answer updated")


    # очистка таблицы users
    def clean_table(self):
        self.execute_query(f'DELETE FROM {table_name}')
        logging.info(f"DATABASE: Table cleaned")


    # добавление в историю запрос пользователя
    def add_history(self, user_id, username, prompt, answer):
        add_history_query = f"""
        INSERT INTO history(user_id, username, prompt, answer)
        SELECT ?, ?, ?, ?
        """
        self.execute_query(add_history_query, [user_id, username, prompt, answer])
        logging.info(f"DATABASE: History added")


    # получение истории запросов пользователя из базы данных
    def get_history(self, user_id):
        sql_query = f'SELECT *' \
                    f'FROM history WHERE user_id = ?'
        rows = self.execute_selection_query(sql_query, [user_id])
        return rows


    # обновление значения в таблице token_usage
    def update_usage_token(self, tokens):
        cursor = self.conn.cursor()
        update_table_query = f"""
        UPDATE token_usage SET tokens = ? WHERE number = 1;
        """
        cursor.execute(update_table_query, (tokens,))
        self.conn.commit()
        logging.info(f"DATABASE: Table updated")


    # получение токенов из token_usage
    def get_token_usage(self):
        cursor = self.conn.cursor()
        get_tokens_query = """
        SELECT tokens
        FROM token_usage
        """
        row = self.execute_selection_query(get_tokens_query)
        tokens = row[0][0]
        return tokens
    

    # добавление токенов в таблицу token_usage
    def insert_token_usage_data(self, tokens):
        cursor = self.conn.cursor()
        insert_data_query = f"""
        INSERT INTO token_usage (tokens)
        SELECT ?
        WHERE NOT EXISTS (SELECT * FROM token_usage WHERE number = 1);
        """
        cursor.execute(insert_data_query, (tokens,))
        self.conn.commit()
        logging.info(f"DATABASE: Data inserted")

import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        with open('schema.sql','r') as file:
            self.cursor.execute(file.read())   
        self.conn.commit()

    # Добавляет нового пользователя в БД используя схему из schema.sql
    def add_user(self, user_id: str):
        """Добавляет нового пользователя в БД"""
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        self.conn.commit()
   
    def get_user(self, user_id: str):
    # Получает данные пользователя
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ?", 
            (user_id,)
        )
        return self.cursor.fetchone()
    
    # Сортирует пользователей в таблице по столбцу и возвращает всю таблицу в порядке убывания
    def get_all_users(self):
        self.cursor.execute(
            f"SELECT * FROM users"
        )
        return self.cursor.fetchall()

    # Обновляет кол-во монет пользователя
    def update_balance(self, user_id: str, amount: int, act: str):
        if act == "+":
            self.cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (amount, user_id)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (amount, user_id)
            )
        self.conn.commit()
    # Обновляет кол-во поинтов пользователя
    def update_points(self,user_id: str, amount: int, act:str):
        if act == "+":
            self.cursor.execute(
                "UPDATE users SET point_balance = point_balance + ? WHERE user_id = ?",
                (amount,user_id)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET point_balance = point_balance - ? WHERE user_id = ?",
                (amount,user_id)
            )
            self.conn.commit()
    # Обновляет кол-во сообщений пользователя
    def add_message_to_counter(self,user_id: str):
        self.cursor.execute(
            "UPDATE users SET messages = messages + 1 WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()

    # Обновляет время последнего получения награды
    def update_claim_time(self, user_id: str):
        current_time = int(datetime.now().timestamp())
        self.cursor.execute(
            "UPDATE users SET last_claim = ? WHERE user_id = ?",
            (current_time, user_id)
        )
        self.conn.commit()

    # Обновляет когда В ПОСЛЕДНИЙ РАЗ пользователь зашел в войс
    def update_last_voice_time(self, user_id: str):
        current_time = int(datetime.now().timestamp())
        self.cursor.execute(
            "UPDATE users SET last_voice_time = ? WHERE user_id = ?",
            (current_time, user_id)
        )
        self.conn.commit()

    # Обновляет общее время проведенное в войсе (в минутах)
    def update_voice_time(self, user_id: str):
        current_time = int(datetime.now().timestamp())
        user_data = self.get_user(user_id)
        last_voice_time = user_data['last_voice_time']
        self.cursor.execute(
            "UPDATE users SET voice_time = voice_time + ? WHERE user_id = ?",
            ((current_time - last_voice_time)//60, user_id)
        )
        self.conn.commit()

    # Обновляет с кем помолвлен пользователь
    def update_married_with(self, user_id: str, target_id: str):
        self.cursor.execute(
            "UPDATE users SET married_with = ? WHERE user_id = ?",
            (target_id,user_id,)
        )
        self.conn.commit()
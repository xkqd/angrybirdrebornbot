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

    def add_user(self, user_id: str):
    # Добавляет нового пользователя в БД
        self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (user_id,)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (user_id, balance, last_claim, voice_time, last_voice_time, defeed, married_with) VALUES (?, 0, 0, 0, 0, 0, 0)",
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

    # Обновляет баланс пользователя
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
import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT,
            balance INTEGER,
            last_claim INTEGER
        )""")
        self.conn.commit()

    def add_user(self, user_id: str):
    # Добавляет нового пользователя в БД
        self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (user_id,)
        )
        if not self.cursor.fetchone():
            self.cursor.execute(
                "INSERT INTO users (user_id, balance, last_claim) VALUES (?, 0, 0)",
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

    def update_balance(self, user_id: str, amount: int):
    # Обновляет баланс пользователя
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, user_id)
        )
        self.conn.commit()

    def update_claim_time(self, user_id: str):
    # Обновляет время последнего получения награды
        current_time = int(datetime.now().timestamp())
        self.cursor.execute(
            "UPDATE users SET last_claim = ? WHERE user_id = ?",
            (current_time, user_id)
        )
        self.conn.commit()
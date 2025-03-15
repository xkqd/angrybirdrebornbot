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
        
        # Проверяем, существует ли пользователь
        self.cursor.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (user_id,)
        )
        if not self.cursor.fetchone():
            # Получаем информацию о столбцах из схемы
            self.cursor.execute("PRAGMA table_info(users)")
            columns = self.cursor.fetchall()
            
            # Создаем пустые списки для имен столбцов и значений
            column_names = []
            values = []
            
            # Заполняем список имен столбцов
            for column in columns:
                column_names.append(column['name'])
                values.append('?')
            
            # Создаем словарь со значениями по умолчанию
            default_values = {'user_id': user_id}
            
            # Заполняем значения для остальных столбцов
            values_to_insert = []
            for column_name in column_names:
                if column_name in default_values:
                    values_to_insert.append(default_values[column_name])
                else:
                    # Ищем значение по умолчанию для текущего столбца
                    for column in columns:
                        if column['name'] == column_name:
                            default_value = column['dflt_value'] or 0
                            values_to_insert.append(default_value)
                            break
            
            # Формируем SQL запрос
            columns_string = ','.join(column_names)
            values_string = ','.join(values)
            sql = f"INSERT INTO users ({columns_string}) VALUES ({values_string})"
            
            # Выполняем запрос
            self.cursor.execute(sql, values_to_insert)
            self.conn.commit()
   
    def get_user(self, user_id: str):
    # Получает данные пользователя
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ?", 
            (user_id,)
        )
        return self.cursor.fetchone()
    
    # Сортирует пользователей в таблице по столбцу и возвращает всю таблицу в порядке убывания
    def get_all_users_ordered_by(self, column: str):
        self.cursor.execute(
            f"SELECT * FROM users ORDER BY ? DESC",(column,)
        )
        return self.cursor.fetchall()

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
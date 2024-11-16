import sqlite3

# подключение к бд (если файла нет, то он будет создан)\
conn = sqlite3.connect("user_data.db")
cursor = conn.cursor()

# Создаем таблицу, если ее нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_cities (
               user_id INTEGER PRIMARY KEY,
               city TEXT NOT NULL
               )
               """)
conn.commit()

# Функ для получения города пользователя
def get_user_city(user_id):
    cursor.execute("SELECT city FROM user_cities WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

# Функ для сохр или обнов города юзера
def save_user_city(user_id, city):
    if get_user_city(user_id) is None:
        cursor.execute("INSERT INTO user_cities (user_id, city) VALUES (?, ?)", (user_id, city))
    else:
        cursor.execute("UPDATE user_cities SET city = ? WHERE user_id = ?", (city, user_id))
    conn.commit()

# Закрытие соединения(при завершении работы скрипта)
def close_connection():
    conn.close()
import sqlite3
from datetime import datetime

# Создаем базу данных, если её нет
def initialize_db():
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reminder_time TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Добавляем напоминание
def add_reminder(user_id: int, reminder_time: str, message: str):
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (user_id, reminder_time, message) VALUES (?, ?, ?)",
                   (user_id, reminder_time, message))
    conn.commit()
    conn.close()

# Получаем напоминания, время которых пришло
def get_due_reminders():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, message FROM reminders WHERE reminder_time <= ?", (now,))
    reminders = cursor.fetchall()
    conn.close()
    return reminders

# Удаляем напоминание после отправки
def delete_reminder(reminder_id: int):
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
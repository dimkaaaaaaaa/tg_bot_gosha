import sqlite3
from datetime import datetime
import asyncio
import os

class ReminderManager:
    def __init__(self, db_path):
        # Если база данных не существует, она будет создана
        if not os.path.exists(db_path):
            self.create_db(db_path)
        self.connection = sqlite3.connect(db_path)

    def create_db(self, db_path):
        """Метод для создания базы данных и необходимых таблиц"""
        with sqlite3.connect(db_path) as connection:
            cursor = connection.cursor()
            # Создаём таблицу, если её ещё нет
            cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                reminder_text TEXT,
                                remind_at TEXT
                              )''')
            connection.commit()

    def _init_db(self):
        """Инициализация бд"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reminder_text TEXT NOT NULL,
            remind_at TEXT NOT NULL         
        )
        """)
        conn.commit()
        conn.close()

    def add_reminder(self, user_id, remind_at, reminder_text):
        """Добавлеие напоминания в бд"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (user_id, remind_at, reminder_text) VALUES (?, ?, ?)",
            (user_id, remind_at, reminder_text)
        )
        conn.commit()
        conn.close()

    def get_due_reminders(self):
        now = datetime.now()
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, user_id, reminder_text FROM reminders WHERE remind_at <= ?", (now,))
            return cursor.fetchall()
    
    def delete_reminder(self, reminder_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))

    async def check_reminders(self, application):
        while True:
            now = datetime.now()
            reminders = self.get_due_reminders()

            for reminder in reminders:
                # Извлечение значений из базы данных
                reminder_id, user_id, reminder_text = reminder

                if user_id:  # Убедимся, что user_id определён
                    # Отправка сообщения пользователю
                    try:
                        await application.bot.send_message(chat_id=user_id, text=f"Напоминание: {reminder_text}")

                        # Удаление напоминания после отправки
                        self.delete_reminder(reminder_id)
                    except Exception as e:
                        await application.bot.send_message(f"Ошибка при отправке напоминания: {e}")
                else:
                    await application.bot.send_message(f"Пропущено напоминание с некорректным user_id: {reminder}")
        
            await asyncio.sleep(60)  # Проверяем напоминания каждую минуту
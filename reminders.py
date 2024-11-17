import sqlite3
from datetime import datetime
import asyncio

class ReminderManager:
    def __init__(self, db_path="reminders.db"):
        self.db_path = db_path
        self._init_db()

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
        """получение напоминаний, время которых наступило"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, reminder_text FROM reminders WHERE remind_at = ?", (now,))
        reminders = cursor.fetchall()
        conn.close()
        return reminders
    
    def delete_reminder(self, reminder_id):
        """удаление напоминания из бд"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()

    async def check_reminders(self, application):
        """проверка напоминаний и отправка сообщений"""
        while True:
            reminders = self.get_due_reminders()
            for reminder_id, user_id, reminder_text in reminders:
                #отправляем увед юзеру
                try:
                    await application.bot.send_message(chat_id=user_id, text=f"Напоминание: {reminder_text}")
                except Exception as e:
                    print(f"Ошибка отправки напоминания: {e}")

                # удаляем напоминание после отправки
                self.delete_reminder(reminder_id)
            await asyncio.sleep(60)
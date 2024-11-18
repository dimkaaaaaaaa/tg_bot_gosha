import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task TEXT,
        description TEXT,
        is_done BOOLEAN DEFAULT 0,
        priority TEXT DEFAULT 'Низкий', -- По умолчанию 'Обычный'
    )
    """)
    conn.commit()
    conn.close()

# Добавление задачи
def add_task(user_id, task, description, priority="Низкий"):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, task, description, priority) VALUES (?, ?, ?, ?)", (user_id, task, description, priority))
    conn.commit()
    conn.close()

# Получение всех задач пользователя
def get_tasks(user_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, task FROM tasks WHERE user_id = ? AND is_done = 0", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# Получение задачи по ID
def get_task(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT task, description FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return task

# Удаление задачи
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# Отметить задачу как выполненную
def mark_task_done(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET is_done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    # Команда добавления задачи
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Используйте формат: /add Название Задачи - Описание - Приоритет (Низкий, Обычный, Высокий). Приоритет по умолчанию 'Низкий'.")
        return
    task = args[0]
    description = " ".join(args[1:])
    priority = args[-1].capitalize() if len(args) > 2 else 'Низкий'
    add_task(user_id, task, description)
    await update.message.reply_text(f"Задача добавлена: {task}\nОписание: {description}")

# Команда просмотра списка задач
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    tasks_i = get_tasks(user_id)
    if not tasks_i:
        await update.message.reply_text("Список задач пуст.")
        return

    keyboard = [[InlineKeyboardButton(task, callback_data=f"view_{task_id}")] for task_id, task in tasks_i]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ваши задачи:", reply_markup=reply_markup)

# Команда для изменения приоритета задачи
async def change_priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if len(context.args) != 2:
        await update.message.reply_text("Используйте формат: /change_priority Название задачи - Низкий/Обычный/Высокий")
        return
    task_name = context.args[0]
    new_priority = context.args[1].capitalize()
    if new_priority not in ['Низкий', 'Обычный', 'Высокий']:
        await update.message.reply_text("Приоритет должен быть одним из следующих: Низкий, Обычный, Высокий")

    # поиск задачи по названию
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE user_id = ? AND task ?", (user_id, task_name))
    task = cursor.fetchone()

    if task is None:
        await update.message.reply_text(f"Задача с названием '{task_name}' не найдена.")
        conn.close()
        return
    
    task_id = task[0]

    # обнова приоритета задачи
    cursor.execute("UPDATE tasks SET priority = ? WHERE id = ? AND user_id = ?", (new_priority, task_id, user_id))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Приоритет задачи '{task_name}' изменен на {new_priority}.")
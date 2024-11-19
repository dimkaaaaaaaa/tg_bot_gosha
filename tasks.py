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
        priority TEXT DEFAULT 'Низкий'
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
    cursor.execute("""
    SELECT id, task, priority FROM tasks WHERE user_id = ? AND is_done = 0
    ORDER BY
        CASE priority
            WHEN 'Высокий' THEN 1
            WHEN 'Обычный' THEN 2
            WHEN 'Низкий' THEN 3
        END
    """, (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# Получение задачи по ID
def get_task(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT task, description, priority FROM tasks WHERE id = ?", (task_id,))
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
    query = update.callback_query
    
    if update.message:
        user_id = update.message.chat_id
    elif query:
        user_id = query.message.chat_id
    else:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Используйте формат: /add Название Задачи - Описание. Приоритет по умолчанию 'Низкий'.")
        return
    task = args[0]
    description = " ".join(args[1:])
    priority = args[-1].capitalize() if len(args) > 2 else 'Низкий'
    add_task(user_id, task, description)
    await update.message.reply_text(f"Задача добавлена: {task}\nОписание: {description}")
    await list_tasks(update, context)

# Команда просмотра списка задач
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        user_id = update.message.chat_id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        return

    tasks_i = get_tasks(user_id)
    if not tasks_i:
        await update.message.reply_text("Список задач пуст.")
        return

    priority_emoji = {
        'Низкий': "🟦",
        'Обычный': "🟨",
        'Высокий': "🟥",
    }

    keyboard = []
    for task_id, task, priority in tasks_i:
        emoji = priority_emoji.get(priority, "🟨")
        task_text = f"{task} ({priority} {emoji})"
        keyboard.append([InlineKeyboardButton(task_text, callback_data=f"view_{task_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Ваши задачи:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Ваши задачи:", reply_markup=reply_markup)

# Обработчик кнопок
async def button_callback_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    await query.answer()  # Ответ пользователю, чтобы кнопка не "висела"

    if data.startswith("view_"):
        task_id = int(data.split("_")[1])
        task = get_task(task_id)
        if task:
            task_name, description, priority = task
            keyboard = [
                [InlineKeyboardButton("Выполнить", callback_data=f"done_{task_id}")],
                [InlineKeyboardButton("Удалить", callback_data=f"delete_{task_id}")],
                [InlineKeyboardButton("Изменить приоритет", callback_data=f"change_priority_{task_id}")],
                [InlineKeyboardButton("Назад", callback_data="back_to_list")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Задача: {task_name}\nОписание: {description}\nПриоритет: {priority}",
                reply_markup=reply_markup
            )

    elif data.startswith("done_"):
        task_id = int(data.split("_")[1])
        mark_task_done(task_id)
        await query.edit_message_text("Задача выполнена.")

    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        delete_task(task_id)
        await query.edit_message_text("Задача удалена.")

    elif data.startswith("change_priority_"):
        task_id = int(data.split("_")[2])  # Извлекаем ID задачи
        keyboard = [
            [InlineKeyboardButton("Высокий 🟥", callback_data=f"set_priority_высокий_{task_id}")],
            [InlineKeyboardButton("Обычный 🟨", callback_data=f"set_priority_обычный_{task_id}")],
            [InlineKeyboardButton("Низкий 🟦", callback_data=f"set_priority_низкий_{task_id}")],
            [InlineKeyboardButton("Назад", callback_data="back_to_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите новый приоритет для задачи:", reply_markup=reply_markup)

    elif data.startswith("set_priority_"):
        priority = data.split("_")[2].capitalize()
        task_id = int(data.split("_")[3])
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
        conn.commit()
        conn.close()
        await query.edit_message_text(f"Приоритет задачи изменен на {priority}.")

    elif data == "back_to_list":
        await list_tasks(update, context)  # Исправленный вызов

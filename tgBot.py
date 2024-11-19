import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
from database import get_user_city, save_user_city
import currentTime, currentWeather, tasks
import sqlite3

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



# Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_cities
    query = update.callback_query
    user_id = update.message.from_user.id
    text = update.message.text
    keyboard = [
            [InlineKeyboardButton("Управление задачами", callback_data="tasks")],
            [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
            [InlineKeyboardButton("Текущее время", callback_data="time")],
            [InlineKeyboardButton("Изменить город", callback_data="change_city")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверка на команды "Привет", "Йоу", "Старт" и отправка кнопок
    if text.lower() in ["йоу", "чувак", "васап", "гоша", "привет", "старт", "здравствуй", "добрый день", "здарова", "приветик", "хай", "здарова", "hello", "hi", "приветствую", "здорово", "гошаа", "гошааа", "георгий", "григорий", "ты", "т"]:
        await update.message.reply_text(
            "Привет! Что хочешь сделать?",
            reply_markup=reply_markup
        )
        return  # Завершаем функцию, чтобы не выводить лишнее сообщение

    # Если не "Привет", продолжаем выполнять остальные действия
    if text.lower() in ["текущее время", "время", "time", "врем", "времяя", "времс", "врамс", "врему", "времени", "време", "вр"]:
        city = get_user_city(user_id) or "Moscow"
        current_time = currentTime.get_current_time(city)
        await update.message.reply_text(f"Текущее время в {city}: {current_time}")
    elif text.lower() in ["погода в моем городе", "погода", "погод", "пог", "пг", "погад", "пагод", "погоды", "погоде", "погоду"]:
        city = get_user_city(user_id) or "Moscow"
        weather = currentWeather.get_weather(city)
        await update.message.reply_text(weather)
    elif text.lower() in ["изменить город", "поменять город", "город", "гр"]:
        await update.message.reply_text("Напишите название нового города.")
        context.user_data["awaiting_city"] = True
    elif context.user_data.get("awaiting_city"):
        save_user_city(user_id, text)
        context.user_data["awaiting_city"] = False
        await update.message.reply_text(f"Ваш город сохранен: {text}.")
    elif text.lower() in ['задача', 'задачи', 'лист']:
        await tasks.list_tasks(update, context)
    else:
        await update.message.reply_text("Выберите действие из предложенных.", reply_markup=reply_markup)




# Обработка нажатий на кнопкиd
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    query: CallbackQuery = update.callback_query
    await query.answer()

    user_id = update.callback_query.from_user.id
    callback_data = query.data

    if data.startswith("view_"):
        task_id = int(data.split("_")[1])
        task = tasks.get_task(task_id)
        if task:
            task_name, description, priority = task
            keyboard = [
                [InlineKeyboardButton("Выполнить", callback_data=f"done_{task_id}")],
                [InlineKeyboardButton("Удалить", callback_data=f"delete_{task_id}")],
                [InlineKeyboardButton("Изменить приоритет", callback_data=f"change_priority_{task_id}")],
                [InlineKeyboardButton("Назад", callback_data="back_to_list")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Задача: {task_name}\nОписание: {description}\nПриоритет: {priority}", reply_markup=reply_markup)

    elif data.startswith("done_"):
        task_id = int(data.split("_")[1])
        tasks.mark_task_done(task_id)
        await query.answer("Задача выполнена.")
        await query.edit_message_text("Задача выполнена.")
        await query.message.reply_text("🎉")

    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        tasks.delete_task(task_id)
        await query.answer("Задача удалена.")
        await query.edit_message_text("Задача удалена.")
    
    elif data.startswith("change_priority_"):
        query = update.callback_query
        await query.answer()
        task_id = int(query.data.split('_')[2])  # Извлекаем ID задачи

        # Кнопки для выбора приоритета
        keyboard = [
            [InlineKeyboardButton("Высокий 🟥", callback_data=f"set_priority_высокий_{task_id}")],
            [InlineKeyboardButton("Обычный 🟨", callback_data=f"set_priority_обычный_{task_id}")],
            [InlineKeyboardButton("Низкий 🟦", callback_data=f"set_priority_низкий_{task_id}")],
            [InlineKeyboardButton("Назад", callback_data=f"back_to_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Выберите новый приоритет для задачи:",
            reply_markup=reply_markup
        )

    elif data.startswith("set_priority_низкий_"):
        query = update.callback_query
        await query.answer()

        task_id = int(query.data.split('_')[3])  # Получаем ID задачи
        new_priority = query.data.split('_')[2].capitalize()

        # Обновление приоритета в базе данных
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (new_priority, task_id))
        conn.commit()
        conn.close()

        await query.edit_message_text(f"Приоритет задачи изменен на {new_priority}.")
    elif data.startswith("set_priority_обычный_"):
        query = update.callback_query
        await query.answer()

        task_id = int(query.data.split('_')[3])  # Получаем ID задачи
        new_priority = query.data.split('_')[2].capitalize()

        # Обновление приоритета в базе данных
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (new_priority, task_id))
        conn.commit()
        conn.close()

        await query.edit_message_text(f"Приоритет задачи изменен на {new_priority}.")
    elif data.startswith("set_priority_высокий_"):
        query = update.callback_query
        await query.answer()

        task_id = int(query.data.split('_')[3])  # Получаем ID задачи
        new_priority = query.data.split('_')[2].capitalize()

        # Обновление приоритета в базе данных
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (new_priority, task_id))
        conn.commit()
        conn.close()

        await query.edit_message_text(f"Приоритет задачи изменен на {new_priority}.")

    elif data == "back_to_list":
        await tasks.list_tasks(query, context)

    if callback_data == "time":
        city = get_user_city(user_id) or "Moscow"
        current_time = currentTime.get_current_time(city)
        await query.message.reply_text(f"Текущее время в {city}: {current_time}")
    elif callback_data == "weather":
        city = get_user_city(user_id) or "Moscow"
        weather = currentWeather.get_weather(city)
        await query.message.reply_text(weather)
    elif callback_data == "change_city":
        await query.message.reply_text("Напишите название нового города.")
        context.user_data["awaiting_city"] = True
    elif callback_data == "tasks":
        await query.message.reply_text("Чтобы добавить задачу используйте формат: /add Название Задачи - Описание")
        await tasks.list_tasks(query, context)

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Управление задачами", callback_data="tasks")],
        [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
        [InlineKeyboardButton("Текущее время", callback_data="time")],
        [InlineKeyboardButton("Изменить город", callback_data="change_city")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Что хочешь сделать?",
        reply_markup=reply_markup
    )

# Функция запуска бота
def main():
    tasks.init_db()  # Проверка и создание базы данных

    application = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))  # Обработчик для кнопок Inline

    application.add_handler(CommandHandler("add", tasks.add))
    application.add_handler(CommandHandler("list", tasks.list_tasks))

    application.run_polling()

if __name__ == "__main__":
    main()
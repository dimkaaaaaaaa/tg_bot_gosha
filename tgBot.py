import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
from database import get_user_city, save_user_city
import currentTime, currentWeather, tasks

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)



# Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_cities
    user_id = update.message.from_user.id
    text = update.message.text

    # Проверка на команды "Привет", "Йоу", "Старт" и отправка кнопок
    if text.lower() in ["йоу", "чувак", "васап", "гоша", "привет", "старт", "здравствуй", "добрый день", "здарова", "приветик", "хай", "здарова", "hello", "hi", "приветствую", "здорово", "гошаа", "гошааа", "георгий", "григорий", "ты", "т"]:
        keyboard = [
            [InlineKeyboardButton("Текущее время", callback_data="time")],
            [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
            [InlineKeyboardButton("Изменить город", callback_data="change_city")],
            [InlineKeyboardButton("Управление задачами", callback_data="tasks")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
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
    else:
        await update.message.reply_text("Выберите действие из предложенных.")


# Команда добавления задачи
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Используйте формат: /add Название Задачи - Описание")
        return
    task = args[0]
    description = " ".join(args[1:])
    tasks.add_task(user_id, task, description)
    await update.message.reply_text(f"Задача добавлена: {task}\nОписание: {description}")

# Команда просмотра списка задач
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    tasks_i = tasks.get_tasks(user_id)
    if not tasks_i:
        await update.message.reply_text("Список задач пуст.")
        return

    keyboard = [[InlineKeyboardButton(task, callback_data=f"view_{task_id}")] for task_id, task in tasks_i]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Ваши задачи:", reply_markup=reply_markup)

async def set_commands(application):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("add", "Добавить задачу"),
        BotCommand("list", "Показать список задач"),
        BotCommand("done", "Отметить задачу как выполненную"),
        BotCommand("delete", "Удалить задачу"),
        BotCommand("help", "Помощь"),
    ]
    await application.bot.set_my_commands(commands)

# Обработка нажатий на кнопки
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
            task_name, description = task
            keyboard = [
                [InlineKeyboardButton("Выполнить", callback_data=f"done_{task_id}")],
                [InlineKeyboardButton("Удалить", callback_data=f"delete_{task_id}")],
                [InlineKeyboardButton("Назад", callback_data="back_to_list")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(f"Задача: {task_name}\nОписание: {description}", reply_markup=reply_markup)

    elif data.startswith("done_"):
        task_id = int(data.split("_")[1])
        tasks.mark_task_done(task_id)
        await query.answer("Задача выполнена.")
        await query.edit_message_text("Задача выполнена.")

    elif data.startswith("delete_"):
        task_id = int(data.split("_")[1])
        tasks.delete_task(task_id)
        await query.answer("Задача удалена.")
        await query.edit_message_text("Задача удалена.")

    elif data == "back_to_list":
        await list_tasks(query, context)

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
        await list_tasks(query, context)

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Текущее время", callback_data="time")],
        [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
        [InlineKeyboardButton("Изменить город", callback_data="change_city")],
        [InlineKeyboardButton("Управление задачами", callback_data="tasks")]
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

    application.bot_data["commands"] = set_commands(application)

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))  # Обработчик для кнопок Inline

    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("list", list_tasks))

    application.run_polling()

if __name__ == "__main__":
    main()
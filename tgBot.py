import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import currentTime
import currentWeather

# Для напоминаний
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
import json


TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"
user_cities = {}  # Словарь для хранения городов пользователей
reminders = {} # Словарь для хранения напоминаний

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация планировщика
scheduler = AsyncIOScheduler()
scheduler.start()

# Функ для загрузки напоминаний из файла
# Функция для загрузки напоминаний из файла
def load_reminders():
    global reminders
    if not os.path.exists("reminders.json"):  # Если файл не существует
        with open("reminders.json", "w") as f:
            json.dump({}, f)  # Создаём пустой JSON файл
        reminders = {}
    else:
        try:
            with open("reminders.json", "r") as f:
                content = f.read().strip()
                if content:
                    reminders = json.loads(content)
                else:
                    reminders = {}
        except json.JSONDecodeError:
            reminders = {}

# Функ для сохр напоминаний в файл
def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(reminders, f, indent=4)

# Функ для напоминания
async def send_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, message: str):
    await update.message.reply_text(f"Напоминание: {message}")
    if user_id in reminders:
        del reminders[user_id] # Удалить напоминание после отправки
    save_reminders()

# Функ для добавления напоминания
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    if len(text.split()) < 3:
        await update.message.reply_text("Пожалуйста, введите команду в формате: /reminder <дата и время> <сообщение>")
        return
    
    time_str = text.split(' ', 2)[1]
    message = text.split(' ', 2)[2]

    try:
        reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        await update.message.reply_text("Неверный формат времени. Используйте формат: YYYY-MM-DD HH:MM")
        return
    
    trigger = DateTrigger(run_date=reminder_time)
    scheduler.add_job(send_reminder, trigger, args=[update, context, user_id, message])

    reminders[user_id] = {"time": reminder_time.strftime("%Y-%m-%d %H:%M"), "message": message}
    save_reminders()

    await update.message.reply_text(f"Напоминание установлено на {reminder_time.strftime('%Y-%m-%d %H:%M')}")

# Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_cities
    user_id = update.message.from_user.id
    text = update.message.text

    # Проверка на команды "Привет", "Йоу", "Старт" и отправка кнопок
    if text.lower() in ["йоу", "чувак", "васап", "гоша", "привет", "старт"]:
        keyboard = [
            [InlineKeyboardButton("Текущее время", callback_data="time")],
            [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
            [InlineKeyboardButton("Изменить город", callback_data="change_city")],
            [InlineKeyboardButton("Добавить напоминание", callback_data="reminder")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Привет! Что хочешь сделать?",
            reply_markup=reply_markup
        )
        return  # Завершаем функцию, чтобы не выводить лишнее сообщение

    # Обработка команды добавления напоминания
    if text.lower().startswith("/reminder"):
        await set_reminder(update, context)
    else:
        await update.message.reply_text("Выберите действие из предложенных.")

# Обработка нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()

    user_id = update.callback_query.from_user.id
    callback_data = query.data

    if callback_data == "time":
        city = user_cities.get(user_id, "Moscow")
        current_time = currentTime.get_current_time(city)
        await query.message.reply_text(f"Текущее время в {city}: {current_time}")
    elif callback_data == "weather":
        city = user_cities.get(user_id, "Moscow")
        weather = currentWeather.get_weather(city)
        await query.message.reply_text(weather)
    elif callback_data == "change_city":
        await query.message.reply_text("Напишите название нового города на английском языке.")
        context.user_data["awaiting_city"] = True
    elif callback_data == "reminder":
        await query.message.reply_text("Введите команду в формате: /reminder <дата и время> <сообщение>.")

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Текущее время", callback_data="time")],
        [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
        [InlineKeyboardButton("Изменить город", callback_data="change_city")],
        [InlineKeyboardButton("Добавить напоминание", callback_data="reminder")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Что хочешь сделать?",
        reply_markup=reply_markup
    )

# Функция запуска бота
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))  # Обработчик для кнопок Inline

    # Загрузка напоминаний из файла при старте
    load_reminders()

    application.run_polling()

if __name__ == "__main__":
    main()
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta
import time
import sched

# Инициализация планировщика
scheduler = sched.scheduler(time.time, time.sleep)

# Словарь для хранения напоминаний
reminders = {}

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"
user_cities = {}  # Словарь для хранения городов пользователей

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция для отправки напоминания
async def send_reminder(update: Update, reminder_text: str) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Напоминание: {reminder_text}")

# Обработка команды /reminder
async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    try:
        # Извлекаем дату и время из сообщения
        parts = text.split(' ', 1)
        if len(parts) < 2:
            await update.message.reply_text("Ошибка: формат команды неверен. Используйте формат: /reminder DD.MM.YYYY HH:MM <текст напоминания>")
            return

        reminder_time_str = parts[0] + ' ' + parts[1][:5]  # Пример: 16.11.2024 05:03
        reminder_text = parts[1][6:]  # Текст напоминания

        # Парсим дату и время
        reminder_time = datetime.strptime(reminder_time_str, "%d.%m.%Y %H:%M")

        # Проверка, чтобы напоминание не было в прошлом
        if reminder_time < datetime.now():
            await update.message.reply_text("Ошибка: время напоминания в прошлом.")
            return

        # Сохраняем напоминание в словарь
        reminders[update.message.from_user.id] = (reminder_time, reminder_text)

        # Запланируем задачу
        delay = (reminder_time - datetime.now()).total_seconds()
        scheduler.enter(delay, 1, send_reminder, (update, reminder_text))
        await update.message.reply_text(f"Напоминание установлено на {reminder_time_str}: {reminder_text}")
    except ValueError:
        await update.message.reply_text("Ошибка: неверный формат даты и времени. Используйте формат: DD.MM.YYYY HH:MM <текст напоминания>")

# Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    # Если не "Привет", продолжаем выполнять остальные действия
    if text.lower() in ["текущее время", "время", "time"]:
        city = user_cities.get(update.message.from_user.id, "Moscow")
        current_time = currentTime.get_current_time(city)
        await update.message.reply_text(f"Текущее время в {city}: {current_time}")
    elif text.lower() in ["погода в моем городе", "погода"]:
        city = user_cities.get(update.message.from_user.id, "Moscow")
        weather = currentWeather.get_weather(city)
        await update.message.reply_text(weather)
    elif text.lower() in ["изменить город"]:
        await update.message.reply_text("Напишите название нового города на английском языке.")
        context.user_data["awaiting_city"] = True
    elif context.user_data.get("awaiting_city"):
        new_city = textuser_cities[update.message.from_user.id] = new_city
        context.user_data["awaiting_city"] = False
        await update.message.reply_text(f"Ваш город изменен на: {new_city}.")
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

# Запуск бота
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(CommandHandler("reminder", reminder))  # Команда для добавления напоминания
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обработка сообщений
    application.add_handler(CallbackQueryHandler(button_callback))  # Обработчик для кнопок Inline

    application.run_polling()

    # Запуск планировщика
    scheduler.run()

if __name__ == "__main__":
    main()
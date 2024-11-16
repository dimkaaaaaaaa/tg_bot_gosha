import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
from database import get_user_city, save_user_city
import currentTime
import currentWeather
from reminder_handler import initialize_db, add_reminder, get_due_reminders, delete_reminder

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда добавления напоминания
async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        # Ожидается формат: "/reminder 16.11.2024 18:30 Напомни выпить воды"
        command = update.message.text.split(" ", 2)
        reminder_time = datetime.strptime(command[1], "%d.%m.%Y %H:%M")
        message = command[2]

        # Сохраняем напоминание
        add_reminder(user_id, reminder_time.strftime("%Y-%m-%d %H:%M:%S"), message)
        await update.message.reply_text(f"Напоминание добавлено: {message} в {reminder_time}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Неправильный формат. Используй: /reminder DD.MM.YYYY HH:MM Текст")

# Проверка напоминаний
async def check_reminders(application):
    while True:
        reminders = get_due_reminders()
        for reminder in reminders:
            reminder_id, user_id, message = reminder
            try:
                # Отправляем напоминание пользователю
                await application.bot.send_message(chat_id=user_id, text=f"Напоминание: {message}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения: {e}")
            finally:
                # Удаляем напоминание после отправки
                delete_reminder(reminder_id)
        await asyncio.sleep(60)  # Проверяем раз в минуту


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
            [InlineKeyboardButton("Изменить город", callback_data="change_city")]
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

# Обработка нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()

    user_id = update.callback_query.from_user.id
    callback_data = query.data

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

# Функция для старта
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Текущее время", callback_data="time")],
        [InlineKeyboardButton("Погода в моем городе", callback_data="weather")],
        [InlineKeyboardButton("Изменить город", callback_data="change_city")]
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

    application.run_polling()

if __name__ == "__main__":
    main()
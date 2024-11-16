import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime, timedelta
from database import get_user_city, save_user_city
import currentTime
import currentWeather
import time, sched

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"
bot = Bot(token=TOKEN)

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

scheduler = sched.scheduler(time.time, time.sleep) # инициал планировщика
user_events = {} # словарь для хранения событий юзеров

# функ для отправки напоминания
def send_reminder(chat_id, event_name):
    bot.send_message(chat_id=chat_id, text=f"Напоминание: время для события '{event_name}'!")
# функ планиорования напоминания
def schedule_reminder(event_name, event_time, chat_id):
    # задержка в сек
    delay = (event_time - datetime.now()).total_seconds()

    #планируем напоминание
    scheduler.enter(delay, 1, send_reminder, argument=(chat_id, event_name))

# Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    global user_cities
    user_id = update.message.from_user.id
    text = update.message.text
    event_details = text.split(" ")

    if len(event_details) != 4:
        await update.message.reply_text("Неверный формат! Введите данные в следующем формате:\n/event Название_события Дата Время")
        return
    event_name, event_date, event_time = event_details[1], event_details[2], event_details[3]
    # формируем полную строку времени
    event_datetime_str = f"{event_date} {event_time}"
    event_datetime = datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
    #сохраняем событие
    user_events[chat_id] = {
        'event_name' : event_name,
        'event_datetime' : event_datetime
    }
    # планируем напоминание
    schedule_reminder(event_name, event_datetime, chat_id)
    # подтверждение от бота
    await update.message.reply_text(f"Событие '{event_name}' запланировано на {event_datetime}. Я напомню вам об этом!")

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

    application.add_handler(CommandHandler("event", handle_message))

    application.run_polling()

# комментарий
if __name__ == "__main__":
    main()
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from datetime import datetime
import currentTime
import currentWeather

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"
user_cities = {} # Словарь для хранения городов пользователей

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_cities
    user_id = update.message.from_user.id
    text = update.message.text

    if text.lower() in ["йоу", "чувак", "васап", "гоша", "привет", "старт"]:
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

    if text.lower() in ["текущее время", "время", "time"]:
        city = user_cities.get(user_id, "Moscow")
        curent_time = currentTime.get_current_time(city)
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Текущее время в {city}: {curent_time}")
    elif text.lower() in ["погода в моем городе", "погода"]:
        city = user_cities.get(user_id, "Moscow")
        weather = currentWeather.get_weather(city)
        await update.message.reply_text(weather)
    elif text.lower() in ["изменить город"]:
        await update.message.reply_text("Напишите название нового города на английском языке.")
        context.user_data["awaiting_city"] = True
    elif context.user_data.get("awaiting_city"):
        new_city = text
        user_cities[user_id] = new_city
        context.user_data["awaiting_city"] = False
        await update.message.reply_text(f"Ваш город изменен на: {new_city}.")
    else:
        await update.message.reply_text("Выберите действие из предложенных.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()

    user_id = update.callback_query.from_user.id
    callback_data = query.data

    if callback_data == "time":
        city = user_cities.get(user_id, "Moscow")
        curent_time = currentTime.get_current_time(city)
        now = datetime.now().strftime("%H:%M:%S")
        await query.message.reply_text(f"Текущее время в {city}: {curent_time}")
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
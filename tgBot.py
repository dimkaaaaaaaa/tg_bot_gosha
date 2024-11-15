import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import requests
import currentTime
import currentWeather

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"
user_cities = {} # Словарь для хранения городов пользователей

#Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keybord = [["Текущее время", "Погода в моем городе", "Изменить город"]]
    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keybord, resize_keyboard=True, one_time_keyboard=True)
    ) 

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

    if text == "Текущее время" or text == "Время" or text == "время":
        city = user_cities.get(user_id, "Moscow")
        curent_time = currentTime.get_current_time(city)
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Текущее время в {city}: {curent_time}")
    elif text == "Погода в моем городе" or text == "Погода" or text == "погода":
        city = user_cities.get(user_id, "Moscow")
        weather = currentWeather.get_weather(city)
        await update.message.reply_text(weather)
    elif text == "Изменить город":
        await update.message.reply_text("Напишите название нового города на английском языке.")
        context.user_data["awaiting_city"] = True
    elif context.user_data.get("awaiting_city"):
        new_city = text
        user_cities[user_id] = new_city
        context.user_data["awaiting_city"] = False
        await update.message.reply_text(f"Ваш город изменен на: {new_city}.")
    else:
        await update.message.reply_text("Выберите действие из предложенных.")
        
# Функ запуска бота
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main() 
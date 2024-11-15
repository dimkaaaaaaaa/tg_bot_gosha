import os
from flask import Flask
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import requests
import currentTime

app = Flask(__name__)

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"

#Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функ для получения погоды
def get_weather(city): 
    api_key = "bd5e378503939ddaee76f12ad7a97608"
    url =  f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("main"):
        main_data = response["main"]
        weather_data = response["weather"][0]
        wind_data = response["wind"]

        temperature = main_data["temp"]
        humidity = main_data["humidity"]
        weather_description = weather_data["description"]
        wind_speed = wind_data["speed"]

        return  f"Погода в городе {city}:\n" \
                f"Температура: {temperature}°C\n" \
                f"Влажность: {humidity}%\n" \
                f"Описание: {weather_description}\n" \
                f"Скорость ветра: {wind_speed} м/с"
    else:
        return "Город не найден. Проверьте правильность ввода."

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keybord = [["Текущее время", "Погода в моем городе"]]
    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keybord, resize_keyboard=True, one_time_keyboard=True)
    ) 

# Обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Текущее время" or text == "Время" or text == "время":
        city = "Smolensk"
        curent_time = currentTime.get_current_time(city)
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Текущее время в {city}: {curent_time}")
    elif text == "Погода в моем городе" or text == "Погода" or text == "погода":
        city = "Smolensk"
        weather = get_weather(city)
        await update.message.reply_text(weather)
    else:
        await update.message.reply_text("Выберите действие из предложенных.")
        
# Функ запуска бота
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()


@app.route('/')
def index():
    return "Bot is running!"
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    main() 
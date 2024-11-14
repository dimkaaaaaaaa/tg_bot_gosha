import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import requests

TOKEN = "7986596049:AAFtX6g_Q4iu9GBtG31giIONkUPd9oHmcYI"

#Логирование
logging.basicConfig(
    format='%(actime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функ для получения погоды
def get_weather(city): 
    api_key = "bd5e378503939ddaee76f12ad7a97608"
    url =  f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url).json()
    if response.get("main"):
        temperature = response["main"]["temp"]
        description = response["weather"][0]["description"]
        return f"Температура: {temperature}°C\nПогодные условия: {description}"
    else:
        return "Не удалось получить погоду."

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keybord = [["Текущее время", "Погода в моем городе"]]
    await update.message.reply_text(
        "Привет! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keybord, one_time_keyboard=True)
    ) 

# Обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Текущее время":
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Текущее время: {now}")
    elif text == "Погода в моем городе":
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

if __name__ == "__main__":
    main()
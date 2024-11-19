import time
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

async def wait_for_specific_time(target_time, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ждет до указанного времени и выводит сообщение.
    
    :param target_time: Время в формате 'YYYY-MM-DD HH:MM'
    """
    target_datetime = datetime.strptime(target_time, "%Y-%m-%d %H:%M")
    print(f"Ожидание до {target_datetime}...")
    
    while datetime.now() < target_datetime:
        time.sleep(60)  # Проверяем каждую секунду

    await update.message.reply_text("Настало время")


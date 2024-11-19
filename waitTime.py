import time, asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def wait_for_specific_time(target_time, update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_datetime = datetime.strptime(target_time, "%Y-%m-%d %H:%M")
    context.application.asyncio.run(update.message.reply_text(f"Ожидание до {target_datetime}..."))
    
    while datetime.now() < target_datetime:
        time.sleep(5)  # Проверяем каждую минуту (асинхронно)

    context.application.asyncio.run(update.message.reply_text("Настало время!"))

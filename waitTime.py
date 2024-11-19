import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def wait_for_specific_time(target_time, update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_datetime = datetime.strptime(target_time, "%Y-%m-%d %H:%M")
    await update.message.reply_text(f"Ожидание до {target_datetime}...")
    
    while datetime.now() < target_datetime:
        await asyncio.sleep(60)  # Проверяем каждую минуту (асинхронно)

    await update.message.reply_text("Настало время!")

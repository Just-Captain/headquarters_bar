from telegram import Update
from telegram.ext import ContextTypes

from bot.management.commands.start_keyboard import start_job_keyboard

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_job_keyboard(update, context)
    # Сбрасываем флаги ожидания
    context.user_data['waiting_for_id'] = False
    context.user_data['waiting_for_menu_total'] = False

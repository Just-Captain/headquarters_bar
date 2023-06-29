from telegram import Update
from telegram.ext import ContextTypes
import os

async def instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получение полного пути к файлу с инструкцией в папке media
    file_path = os.path.join('media', 'instructions', 'instruction.pdf')

    # Отправка документа и приглашение открыть файл
    with open(file_path, 'rb') as file:
        await context.bot.send_document(chat_id=update.effective_chat.id,document=file,caption='Пожалуйста, откройте инструкцию для просмотра')



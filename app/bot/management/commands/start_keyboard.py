from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, Updater


async def start_keyboard(update: Updater, context:ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton('🪪 Виртуальная карта'), KeyboardButton('👨‍💼 Профиль')],[KeyboardButton('📆 Афиша'), KeyboardButton('📗 Контакты')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='⤵️ Выберите действие:', reply_markup=reply_markup)

async def start_job_keyboard(update: Updater, context:ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton('🔳 Отсканировать QR-код'),KeyboardButton('👆 Ввести ID клиента')], [KeyboardButton('📋 Инструкция')]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id,text='⤵️ Выберите действие:', reply_markup=reply_markup)
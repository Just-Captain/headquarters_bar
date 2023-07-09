from django.core.management.base import BaseCommand
from django.conf import settings
from bot.management.commands.config import application
from telegram.ext import (
    CommandHandler, 
    ContextTypes,
    MessageHandler, 
    filters, 
    ConversationHandler
)
from telegram import (
    Update, 
    KeyboardButton, 
    ReplyKeyboardMarkup
)
import asyncio

from bot.management.commands.config import USER_TYPING, CHOOSING_OPTION_CLIENT, CHOOSING_OPTION_WORKER, CHECK_CORRECT, PHONE_NUMBER, CHOOSING_OPTION_PHONE

from bot.management.commands.sync_request import get_data_id_async
from bot.models import User, Worker
from .start_keyboard import start_keyboard, start_job_keyboard

"""client modules"""
from bot.management.commands.modules.client.afisha import afisha
from bot.management.commands.modules.client.contacts import contact
from bot.management.commands.modules.client.phone_number import phone_number
from bot.management.commands.modules.client.profile import profile
from bot.management.commands.modules.client.virtual_card import virtual_card

"""job modules"""
from bot.management.commands.modules.personal.scan_code import scan_code
from bot.management.commands.modules.personal.create_check import phone_number_billing, check, check_the_check
from bot.management.commands.modules.personal.instruction import instruction
from bot.management.commands.modules.personal.cancel_operation import cancel_operation


import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """client start"""
    context.bot_data['state'] = 'start'
    user = update.effective_user
    user_id = user.id
    try: 
        user_profile = await get_data_id_async(User, user_id)
        context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        await start_keyboard(update, context) 
    except User.DoesNotExist:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
    return CHOOSING_OPTION_CLIENT

async def start_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """job start"""
    context.bot_data['state'] = 'start_job'
    user = update.effective_user
    user_id = user.id
    # Проверяем, есть ли пользователь в базе данных
    try:
        job_profile = await get_data_id_async(Worker, user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы!')
        await start_job_keyboard(update, context)
    except Worker.DoesNotExist:
        # Отправляем запрос на номер телефона
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
    return CHOOSING_OPTION_WORKER


def main():
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start), CommandHandler('start_job', start_job)],
    states={
        CHOOSING_OPTION_CLIENT: [
            MessageHandler(filters.Text('👨‍💼 Профиль'), profile),
            MessageHandler(filters.Text('📆 Афиша'), afisha),
            MessageHandler(filters.Text('📗 Контакты'), contact),
            MessageHandler(filters.Text('🪪 Виртуальная карта'), virtual_card),
            MessageHandler(filters.CONTACT, phone_number)
            ],
        CHOOSING_OPTION_WORKER: [
            MessageHandler(filters.Text('🔳 Отсканировать QR-код'), scan_code),
            MessageHandler(filters.Text('📋 Инструкция'), instruction),
            MessageHandler(filters.Text('👆 Ввести ID клиента'), phone_number_billing),
            MessageHandler(filters.Text('↩️ Назад'), cancel_operation),
            MessageHandler(filters.CONTACT, phone_number),
        ],
        PHONE_NUMBER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, check,)
        ],
        CHECK_CORRECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, check_the_check,)
        ]
    },
    fallbacks=[]
)
    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=0.5)
class Command(BaseCommand):
    help = "Telegram - bot"
    def handle(self, *args, **kwargs):
        asyncio.run(main())
        


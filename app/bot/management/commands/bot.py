from django.core.management.base import BaseCommand
from django.conf import settings
from bot.management.commands.config import application
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
from telegram import KeyboardButton, ReplyKeyboardMarkup
import asyncio
from asgiref.sync import sync_to_async

from bot.models import UserProfile, JobProfile
from .start_keyboard import start_keyboard, start_job_keyboard

"""client modules"""
from bot.management.commands.modules.client.afisha import afisha
from bot.management.commands.modules.client.contacts import contact
from bot.management.commands.modules.client.phone_number import phone_number
from bot.management.commands.modules.client.profile import profile
from bot.management.commands.modules.client.virtual_card import virtual_card

"""job modules"""
from bot.management.commands.modules.personal.scan_code import scan_code
from bot.management.commands.modules.personal.add_menu_total_button import add_menu_total_button
from bot.management.commands.modules.personal.cancel_operation import cancel_operation
from bot.management.commands.modules.personal.handle_menu_total import handle_menu_total
from bot.management.commands.modules.personal.instruction import instruction

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



"""client start"""
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data['state'] = 'start'
    user = update.effective_user
    user_id = user.id

    try: 
        user_profile = await sync_to_async(UserProfile.objects.get)(external_id=user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        await start_keyboard(update, context) 
    except UserProfile.DoesNotExist:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))

"""job start"""
async def start_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data['state'] = 'start_job'
    user = update.effective_user
    user_id = user.id
    # Проверяем, есть ли пользователь в базе данных
    try:
        job_profile = await sync_to_async(JobProfile.objects.get)(external_id=user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы!')
        await start_job_keyboard(update, context)
    except JobProfile.DoesNotExist:
        # Отправляем запрос на номер телефона
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
        



def main():
    
    """client handler"""
    start_handler = CommandHandler("start", start)
    phone_number_handler = MessageHandler(filters.CONTACT, phone_number)
    profile_handler = MessageHandler(filters.Text('👨‍💼 Профиль'), profile)
    afisha_handler = MessageHandler(filters.Text('📆 Афиша'), afisha)
    contact_handler = MessageHandler(filters.Text('📗 Контакты'), contact)
    virtual_card_handler = MessageHandler(filters.Text('🪪 Виртуальная карта'), virtual_card)

    """job handler"""
    start_job_hander = CommandHandler('start_job', start_job)
    scan_code_handler = MessageHandler(filters.Text('🔳 Отсканировать QR-код'), scan_code)
    instruction_handler = MessageHandler(filters.Text('📋 Инструкция'), instruction)
    add_menu_total_button_handler = MessageHandler(filters.Text('👆 Ввести ID клиента'), add_menu_total_button)
    cancel_operation_handler = MessageHandler(filters.Text('↩️ Назад'), cancel_operation)
    handle_menu_total_handler = MessageHandler(filters.Text, handle_menu_total)

    application.add_handler(start_handler)
    application.add_handler(phone_number_handler)
    application.add_handler(profile_handler)
    application.add_handler(afisha_handler)
    application.add_handler(contact_handler)
    application.add_handler(virtual_card_handler)
    application.add_handler(start_job_hander)
    application.add_handler(scan_code_handler)
    application.add_handler(instruction_handler)
    application.add_handler(add_menu_total_button_handler)
    application.add_handler(cancel_operation_handler)
    application.add_handler(handle_menu_total_handler)
    
    """setting application"""
    application.run_polling(allowed_updates=Update.ALL_TYPES)


class Command(BaseCommand):

    help = "Telegram - bot"

    def handle(self, *args, **kwargs):
        asyncio.run(main())
        


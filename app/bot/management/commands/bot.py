from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from ...models import UserProfile, JobProfile
from io import BytesIO
from .start_keyboard import start_keyboard, start_job_keyboard
import re
from datetime import datetime
import decimal
#import cv2

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from bot.management.commands.config import application
from telegram.ext import CallbackQueryHandler, CallbackContext, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update
import asyncio
import os
from asgiref.sync import sync_to_async


# import client model
from bot.management.commands.modules.client.afisha import afisha
from bot.management.commands.modules.client.contacts import contact
from bot.management.commands.modules.client.create_signed_qr import create_signed_qr_code
from bot.management.commands.modules.client.phone_number import phone_number
from bot.management.commands.modules.client.profile import profile
from bot.management.commands.modules.client.virtual_card import virtual_card

# import job model
from bot.management.commands.modules.personal.scan_code import scan_code

import logging
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data['state'] = 'start'
    user = update.effective_user
    user_id = user.id

    try: 
        user_profile = await sync_to_async(UserProfile.objects.get)(external_id=user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
    except UserProfile.DoesNotExist:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
    finally:
        await start_keyboard(update, context)

"""
КОД ДЛЯ РАБОТНИКА
"""

async def start_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.bot_data['state'] = 'start_job'
    user = update.effective_user
    user_id = user.id
    # Проверяем, есть ли пользователь в базе данных
    try:
        job_profile = await sync_to_async(JobProfile.objects.get)(external_id=user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы уже зарегистрированы!')
    except JobProfile.DoesNotExist:
        # Отправляем запрос на номер телефона
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для этого нажмите на кнопку "Отправить номер 📲"', reply_markup=ReplyKeyboardMarkup([[KeyboardButton('📲 Отправить номер', request_contact=True)]], resize_keyboard=True, one_time_keyboard=True))
    finally:
        start_job_keyboard(update, context)


async def add_menu_total_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton('❌ Удалить сумму текущего заказа')],
        [KeyboardButton('↩️ Назад')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите 🆔 клиента.', reply_markup=reply_markup)
    # Устанавливаем флаг ожидания ID клиента
    context.user_data['waiting_for_id'] = True

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_job_keyboard(update, context)
    # Сбрасываем флаги ожидания
    context.user_data['waiting_for_id'] = False
    context.user_data['waiting_for_menu_total'] = False

async def handle_menu_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '❌ Удалить сумму текущего заказа':
        user_profile = context.user_data.get('user_profile')
        if user_profile:
            # Возврат суммы из предыдущего меню в текущую сумму меню
            user_profile.total_spent = user_profile.total_spent - decimal.Decimal(user_profile.menu_total)
            user_profile.menu_total = 0
            user_profile.save()
            await update.message.reply_text(f'✅ Сумма текущего заказа успешно отменена. Текущая сумма заказа: {user_profile.menu_total} руб.')
        else:
            await update.message.reply_text('🔴 Произошла ошибка. Пожалуйста, повторите попытку.')
            start_job_keyboard(update, context)

        # Сбрасываем флаги ожидания
        context.user_data['waiting_for_menu_total'] = False
        context.user_data.pop('user_profile', None)
    if context.user_data.get('waiting_for_id'):
        user_id = update.message.text
        if not user_id.isdigit():
            await update.message.reply_text('ID клиента должно быть числом, повторите ввод:')
        try:
            user_profile = UserProfile.objects.get(external_id=user_id)
            vip_status = "VIP-клиент ⭐️⭐️⭐️" if user_profile.is_special else "Обычный клиент ⭐️"
            # Формируем информацию о пользователе
            reply_message = f"Статус: {vip_status}\n"
            reply_message += f"🆔 ID клиента: {user_profile.external_id}\n"
            reply_message += f"📱 Номер телефона: {user_profile.phone_number}\n"
            reply_message += f"📉 Текущая скидка: {user_profile.discount_percentage}%\n"
            # Отправляем информацию о пользователе
            await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

        except ObjectDoesNotExist:
            await update.message.reply_text('Клиент с указанным ID не найден.')

        context.user_data['waiting_for_id'] = False
        context.user_data['user_profile'] = user_profile
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите 👆 сумму текущего заказа\n '
                                                                        'или отмените введенную ранее сумму заказа, нажав на кнопку\n'
                                                                        '"❌ Удалить сумму текущего заказа"')
        # Устанавливаем флаг ожидания суммы меню
        context.user_data['waiting_for_menu_total'] = True

    elif context.user_data.get('waiting_for_menu_total'):
        menu_total = update.message.text

        if not re.match(r'^\d+\.\d{2}$', menu_total.replace(',', '.')):
            await update.message.reply_text('Сумма заказа должна содержать рубли и копейки (0.00)')

        user_profile = context.user_data.get('user_profile')
        if user_profile:
            # Сохраняем предыдущую сумму меню
            user_profile.previous_menu_total = user_profile.menu_total

            # Обновляем сумму текущего меню в профиле пользователя
            user_profile.menu_total = '{:.2f}'.format(float(menu_total))
            user_profile.total_spent += decimal.Decimal(user_profile.menu_total)

            # Сохраняем дату и время обновления меню
            user_profile.menu_total_timestamp = datetime.now()
            user_profile.save()
            await update.message.reply_text(f'Сумма текущего заказа {user_profile.menu_total} руб. успешно добавлена.')
            vip_status = "VIP-клиент ⭐️⭐️⭐️" if user_profile.is_special else "Обычный клиент ⭐️"
            # Формируем информацию о пользователе
            reply_message = f"Статус: {vip_status}\n"
            reply_message += f"🆔 ID клиента: {user_profile.external_id}\n"
            reply_message += f"📱 Номер телефона: {user_profile.phone_number}\n"
            reply_message += f"📉 Текущая скидка: {user_profile.discount_percentage}%\n"
            reply_message += f"💵 Сумма текущего заказа: {user_profile.menu_total} руб.\n"
            # Отправляем информацию о пользователе
            await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
            start_job_keyboard(update, context)
        else:
            await update.message.reply_text('🔴 Произошла ошибка. Пожалуйста, повторите попытку.')
        # Сбрасываем флаги ожидания
        context.user_data['waiting_for_menu_total'] = False
        context.user_data.pop('user_profile', None)
    else:
        start_job_keyboard(update, context)

async def instruction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получение полного пути к файлу с инструкцией в папке media
    file_path = os.path.join('media', 'instructions', 'instruction.pdf')

    # Отправка документа и приглашение открыть файл
    with open(file_path, 'rb') as file:
        await context.bot.send_document(chat_id=update.effective_chat.id,document=file,caption='Пожалуйста, откройте инструкцию для просмотра')




def main():
    

    # client handler
    start_handler = CommandHandler("start", start)
    phone_number_handler = MessageHandler(filters.CONTACT, phone_number)
    profile_handler = MessageHandler(filters.Text('👨‍💼 Профиль'), profile)
    afisha_handler = MessageHandler(filters.Text('📆 Афиша'), afisha)
    contact_handler = MessageHandler(filters.Text('📗 Контакты'), contact)
    virtual_card_handler = MessageHandler(filters.Text('🪪 Виртуальная карта'), virtual_card)

    # job handler 
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



    
    # run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


class Command(BaseCommand):

    help = "Telegram - bot"

    def handle(self, *args, **kwargs):
        asyncio.run(main())
        


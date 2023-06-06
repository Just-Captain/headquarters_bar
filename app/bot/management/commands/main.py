from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import types
from bot.management.commands.config import bot
from telebot import types
#from PIL import Image
#from pyzbar.pyzbar import decode
from io import BytesIO
import os
#from pyqrcode import QRCode
import json


from bot.management.commands.func.client import card
from bot.management.commands.func.client import contact
from bot.management.commands.func.client import news

from bot.management.commands.func.personal.instruction import guidelines_for_employee
from bot.management.commands.func.personal.find_client_id import find_client_by_id



# handle start command
@bot.message_handler(commands=['start'])
def start_client(message):
    # add client's buttons
    card = types.KeyboardButton('💳 Виртуальная карта')
    news = types.KeyboardButton('📰 Афиша')
    links = types.KeyboardButton('📱 Контакты')
    back = types.KeyboardButton('🔙 Главное меню')

    # add a client's keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(card, news, links, back)
    bot.send_message(message.chat.id,
                     'Здравствуйте, {0}! Выберете подходящую опцию'.format(message.from_user.first_name),
                     reply_markup=keyboard)

# menu for an employee after check a number
@bot.message_handler(commands=['start_job'])
def start_job(message):
    # add employee's buttons
    scan_qr_code = types.KeyboardButton('🤳🏻 Отсканировать код')
    find_client_by_id = types.KeyboardButton('🔍 Найти клиента по ID')
    orders_history = types.KeyboardButton('⌚️ Последние заказы')
    guidelines = types.KeyboardButton('👆 Инструкция')
    back = types.KeyboardButton('🔙 Меню работника')

    # add employee's keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(scan_qr_code, find_client_by_id, orders_history, guidelines, back)
    bot.send_message(message.chat.id, 'Выберете действие', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def manu(message):
    if message.text == "💳 Виртуальная карта":
        card(message)
    elif message.text == "📰 Афиша":
        news(message)
    elif message.text == "📱 Контакты":
        contact(message)
    elif message.text == "🔙 Главное меню":
        start_client(message)
    elif message.text == "🤳🏻 Отсканировать код":
        pass
    elif message.text == "🔍 Найти клиента по ID":
        find_client_by_id(message)
    elif message.text == "⌚️ Последние заказы":
        pass
    elif message.text == "👆 Инструкция":
        guidelines_for_employee(message)
    elif message.text == "🔙 Меню работника":
        start_job(message)
    





class Command(BaseCommand):

    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        print('RUN BOT . . .')
        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.infinity_polling(none_stop=True)
        print('STOP BOT . . .')
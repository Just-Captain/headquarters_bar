from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import types
from bot.management.commands.config import bot
from telebot import types
from PIL import Image
#from pyzbar.pyzbar import decode
from io import BytesIO
import os
from pyqrcode import QRCode
import json





# handle start command
@bot.message_handler(commands=['start'])
def start(message):
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






class Command(BaseCommand):

    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        print('RUN BOT . . .')
        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.infinity_polling(none_stop=True)
        print('STOP BOT . . .')
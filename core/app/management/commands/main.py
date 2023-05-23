from django.core.management.base import BaseCommand
from django.conf import settings
from telebot import TeleBot

from app.management.commands.config import bot



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(chat_id=message.from_user.id, text="Подключился")























class Command(BaseCommand):

    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        print('RUN BOT . . .')
        bot.enable_save_next_step_handlers(delay=2)
        bot.load_next_step_handlers()
        bot.infinity_polling(none_stop=True)
        print('STOP BOT . . .')
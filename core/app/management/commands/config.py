import os
from dotenv import load_dotenv
import telebot

load_dotenv()

TOKEN_TELEGRAM = os.environ.get('TOKEN_TELEGRAM')
bot = telebot.TeleBot(TOKEN_TELEGRAM, threaded=False)
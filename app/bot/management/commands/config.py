import os
from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

TOKEN_TELEGRAM = os.environ.get('TOKEN_TELEGRAM')
application = Application.builder().token(TOKEN_TELEGRAM).build()
CHOOSING_OPTION_CLIENT, CHOOSING_OPTION_WORKER, USER_TYPING, PHONE_NUMBER, CHECK_CORRECT, CHOOSING_OPTION_PHONE = range(6)
import os
from dotenv import load_dotenv
from telegram.ext import Application

load_dotenv()

TOKEN_TELEGRAM = os.environ.get('TOKEN_TELEGRAM')
application = Application.builder().token(TOKEN_TELEGRAM).build()

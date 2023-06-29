from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

async def scan_code(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    button_text = '🔳 Отсканировать QR-код'
    button_url = 'https://www.online-qr-scanner.com/'
    keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Нажмите кнопку ниже, чтобы открыть сканер QR-кодов:', reply_markup=reply_markup)

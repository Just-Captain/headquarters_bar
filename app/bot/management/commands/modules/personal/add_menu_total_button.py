from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def add_menu_total_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton('❌ Удалить сумму текущего заказа')],
        [KeyboardButton('↩️ Назад')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите 🆔 клиента.', reply_markup=reply_markup)
    # Устанавливаем флаг ожидания ID клиента
    context.user_data['waiting_for_id'] = True

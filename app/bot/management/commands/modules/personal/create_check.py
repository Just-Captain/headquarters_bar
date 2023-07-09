from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, CallbackQueryHandler
from bot.management.commands.config import USER_TYPING, CHOOSING_OPTION_WORKER, CHECK_CORRECT, PHONE_NUMBER, application
from bot.models import User, Worker, Check
from bot.management.commands.sync_request import get_data_phone_async, create_data_check, get_data_id_async
from bot.management.commands.start_keyboard import start_job_keyboard

async def phone_number_billing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton('↩️ Назад')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите номер телефона клиента. Без +7 или 8 в начале номера', reply_markup=reply_markup)
    return PHONE_NUMBER

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone_number = f'+7{update.message.text}'
    try:
        user_profile = await get_data_phone_async(User, phone_number)
        context.user_data['user'] = user_profile
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите сумму чека за еду и алкоголь через пробел")
        return CHECK_CORRECT
    except User.DoesNotExist:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Пользователь с данным номером телефона: {phone_number}, не найден в базе данных")
        await start_job_keyboard(update, context)
        return CHOOSING_OPTION_WORKER

async def check_the_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    total = update.message.text.split()
    new_total:float = 0
    for i in total:
        new_total += float(i)
    worker_profile = await get_data_id_async(Worker, update.effective_user.id)
    keyboard = [
        [InlineKeyboardButton("Создать чек", callback_data='true_check')],
        [InlineKeyboardButton("Отменить чек", callback_data='false_check')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['worker'] = worker_profile
    context.user_data['amount'] = new_total
    text = f"<b>Клиент:</b> {context.user_data['user'].phone_number}\n<b>Сумма по еде и алкоголю:</b>{context.user_data['amount']}\n<b>Работник:</b>{context.user_data['worker']}"
    await update.message.reply_text(text=text, parse_mode="html")
    await update.message.reply_text('Выберите кнопку:', reply_markup=reply_markup)
    return CHOOSING_OPTION_WORKER
    


async def check_finaly(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'true_check':
        create_check = await create_data_check(
            Check, context.user_data['user'],
            context.user_data['worker'],
            context.user_data['amount']
        )
        amount = context.user_data['amount'] - (context.user_data['amount'] * context.user_data['user'].discount_percentage / 100)
        text = f"Чек был создан!\nСумма к оплате со скидкой: {amount} вместо {context.user_data['amount']}"
        await query.edit_message_text(text=text)
    elif query.data == 'false_check':
        await query.edit_message_text(text="Чек был отменён")
    await start_job_keyboard(update, context)
    return CHOOSING_OPTION_WORKER

button_handler = CallbackQueryHandler(check_finaly)
application.add_handler(button_handler)
    

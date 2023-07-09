from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardRemove
from bot.models import User, Worker
from bot.management.commands.start_keyboard import start_keyboard, start_job_keyboard
from bot.management.commands.sync_request import create_data_id_phone_async, get_data_phone_async, get_data_id_async, save_data_async

async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print('phone_number')
    state = context.bot_data.get('state')
    if state == 'start':
        user = update.effective_user
        user_id = user.id
        phone_number = update.effective_message.contact.phone_number
        # Проверяем, есть ли пользователь в базе данных
        try:
            user_profile = await get_data_id_async(User, user_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        except User.DoesNotExist:
            # Создаем профиль пользователя
            user_profile = await create_data_id_phone_async(User, user_id, phone_number)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='✅ Вы успешно зарегистрированы!')
            await context.bot.send_message(chat_id=update.effective_chat.id, text='📁 Данные будут доступны во вкладке "🪪 Виртуальная карта"')
            await start_keyboard(update, context)
            
    elif state == 'start_job':
        user = update.effective_user
        user_id = user.id
        phone_number = update.effective_message.contact.phone_number
        # Проверяем, есть ли пользователь в базе данных
        try:
            job_profile = await get_data_id_async(Worker, user_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        except Worker.DoesNotExist:
            job_profile = await create_data_id_phone_async(Worker, user_id, phone_number)
            await save_data_async(job_profile)
            # Отправляем информацию о работнике
            await context.bot.send_message(chat_id=update.effective_chat.id, text='✅ Вы успешно зарегистрированы!')
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваш ID: {job_profile.external_id}', reply_markup=ReplyKeyboardRemove()) 
            await start_job_keyboard(update, context)
    else:
        pass
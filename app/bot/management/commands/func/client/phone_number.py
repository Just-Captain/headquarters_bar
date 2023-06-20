from telegram.ext import ContextTypes
from telegram import Update, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from cryptography.hazmat.primitives.asymmetric import rsa

from bot.models import UserProfile, JobProfile
from bot.management.commands.start_keyboard import start_keyboard, start_job_keyboard
from bot.management.commands.func.client.create_signed_qr import create_signed_qr_code


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data.get('state')
    if state == 'start':
        user = update.effective_user
        user_id = user.id
        phone_number = update.effective_message.contact.phone_number
        # Проверяем, есть ли пользователь в базе данных
        try:
            user_profile = await sync_to_async(UserProfile.objects.get)(external_id=user_id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        except UserProfile.DoesNotExist:
            # Создаем профиль пользователя
            user_profile = await sync_to_async(UserProfile.objects.create)(external_id=user_id, phone_number=phone_number)
            # Создаем QR-код
            qr_data = f'🆔 ID : {user_profile.external_id}' \
                      f'📉 Скидка: {user_profile.discount_percentage}%'
            # Генерация ключевой пары RSA
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            qr_code = create_signed_qr_code(user_profile, qr_data, private_key)
            user_profile.qr_code = qr_code  # Привязываем QR-код к профилю пользователя
            user_profile.save()

            # Отправляем QR-код
            await context.bot.send_message(chat_id=update.effective_chat.id, text='✅ Вы успешно зарегистрированы!')
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'🆔 Ваш ID: {user_profile.external_id}\n🔳 Персональный QR-код: ',
                                     reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(qr_code, 'rb'))
            await context.bot.send_message(chat_id=update.effective_chat.id, text='📁 Данные будут доступны во вкладке "🪪 Виртуальная карта"')
            start_keyboard(update, context)
            
    elif state == 'start_job':
        user = update.effective_user
        user_id = user.id
        phone_number = update.effective_message.contact.phone_number

        # Проверяем, есть ли пользователь в базе данных
        try:
            job_profile = JobProfile.objects.get(external_id=user_id)
            context.bot.send_message(chat_id=update.effective_chat.id, text='🟢 Вы уже зарегистрированы!')
        except JobProfile.DoesNotExist:
            # Создаем профиль пользователя
            job_profile = JobProfile.objects.create(external_id=user_id, phone_number=phone_number)
            job_profile.save()

            # Отправляем информацию о работнике
            context.bot.send_message(chat_id=update.effective_chat.id, text='✅ Вы успешно зарегистрированы!')
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваш ID: {job_profile.external_id}', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            start_job_keyboard(update, context)
    else:
        pass
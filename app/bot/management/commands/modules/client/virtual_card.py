from telegram.ext import ContextTypes
from telegram import Update
from cryptography.hazmat.primitives.asymmetric import rsa
from bot.management.commands.modules.client.create_signed_qr import create_signed_qr_code
import qrcode
from bot.models import User
from bot.management.commands.start_keyboard import start_keyboard
from bot.management.commands.sync_request import get_data_id_async, save_data_async


async def virtual_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    user_profile = await get_data_id_async(User, user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='🪪 Ваша виртуальная карта:')

    # Создаем QR-код
    qr_data = f'ID : {user_profile.external_id}\n Скидка: {user_profile.discount_percentage}%\n'

    # Генерация ключевой пары RSA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    qr_code = await create_signed_qr_code(user_profile, qr_data, private_key)
    user_profile.qr_code = qr_code  # Привязываем QR-код к профилю пользователя
    await save_data_async(user_profile)

    # Отправляем QR-код
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'🆔 Ваш ID: {user_profile.external_id}\n🔳 Персональный QR-код:')
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(qr_code, 'rb'))
    await start_keyboard(update, context)
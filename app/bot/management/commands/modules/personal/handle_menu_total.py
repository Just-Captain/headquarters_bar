from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import decimal
from django.core.exceptions import ObjectDoesNotExist
import re

from bot.management.commands.start_keyboard import start_job_keyboard
from bot.models import UserProfile

from bot.management.commands.sync_request import get_data_async, save_data_async

async def handle_menu_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '❌ Удалить сумму текущего заказа':
        user_profile = context.user_data.get('user_profile')
        if user_profile:
            # Возврат суммы из предыдущего меню в текущую сумму меню
            user_profile.total_spent = user_profile.total_spent - decimal.Decimal(user_profile.menu_total)
            user_profile.menu_total = 0
            save_data_async(user_profile)
            await update.message.reply_text(f'✅ Сумма текущего заказа успешно отменена. Текущая сумма заказа: {user_profile.menu_total} руб.')
        else:
            await update.message.reply_text('🔴 Произошла ошибка. Пожалуйста, повторите попытку.')
            await start_job_keyboard(update, context)

        # Сбрасываем флаги ожидания
        context.user_data['waiting_for_menu_total'] = False
        context.user_data.pop('user_profile', None)
    if context.user_data.get('waiting_for_id'):
        user_id = update.message.text
        if not user_id.isdigit():
            await update.message.reply_text('ID клиента должно быть числом, повторите ввод:')
        try:
            user_profile = await get_data_async(user_id)
            vip_status = "VIP-клиент ⭐️⭐️⭐️" if user_profile.is_special else "Обычный клиент ⭐️"
            # Формируем информацию о пользователе
            reply_message = f"Статус: {vip_status}\n"
            reply_message += f"🆔 ID клиента: {user_profile.external_id}\n"
            reply_message += f"📱 Номер телефона: {user_profile.phone_number}\n"
            reply_message += f"📉 Текущая скидка: {user_profile.discount_percentage}%\n"
            # Отправляем информацию о пользователе
            await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

        except ObjectDoesNotExist:
            await update.message.reply_text('Клиент с указанным ID не найден.')

        context.user_data['waiting_for_id'] = False
        context.user_data['user_profile'] = user_profile
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, введите 👆 сумму текущего заказа\n '
                                                                        'или отмените введенную ранее сумму заказа, нажав на кнопку\n'
                                                                        '"❌ Удалить сумму текущего заказа"')
        # Устанавливаем флаг ожидания суммы меню
        context.user_data['waiting_for_menu_total'] = True

    elif context.user_data.get('waiting_for_menu_total'):
        menu_total = update.message.text

        if not re.match(r'^\d+\.\d{2}$', menu_total.replace(',', '.')):
            await update.message.reply_text('Сумма заказа должна содержать рубли и копейки (0.00)')

        user_profile = context.user_data.get('user_profile')
        if user_profile:
            # Сохраняем предыдущую сумму меню
            user_profile.previous_menu_total = user_profile.menu_total

            # Обновляем сумму текущего меню в профиле пользователя
            user_profile.menu_total = '{:.2f}'.format(float(menu_total))
            user_profile.total_spent += decimal.Decimal(user_profile.menu_total)

            # Сохраняем дату и время обновления меню
            user_profile.menu_total_timestamp = datetime.now()
            save_data_async(user_profile)
            await update.message.reply_text(f'Сумма текущего заказа {user_profile.menu_total} руб. успешно добавлена.')
            vip_status = "VIP-клиент ⭐️⭐️⭐️" if user_profile.is_special else "Обычный клиент ⭐️"
            # Формируем информацию о пользователе
            reply_message = f"Статус: {vip_status}\n"
            reply_message += f"🆔 ID клиента: {user_profile.external_id}\n"
            reply_message += f"📱 Номер телефона: {user_profile.phone_number}\n"
            reply_message += f"📉 Текущая скидка: {user_profile.discount_percentage}%\n"
            reply_message += f"💵 Сумма текущего заказа: {user_profile.menu_total} руб.\n"
            # Отправляем информацию о пользователе
            await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
            await start_job_keyboard(update, context)
        else:
            await update.message.reply_text('🔴 Произошла ошибка. Пожалуйста, повторите попытку.')
        # Сбрасываем флаги ожидания
        context.user_data['waiting_for_menu_total'] = False
        context.user_data.pop('user_profile', None)
    else:
        await start_job_keyboard(update, context)
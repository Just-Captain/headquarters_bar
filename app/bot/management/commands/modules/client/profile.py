from telegram.ext import ContextTypes
from telegram import Update
from asgiref.sync import sync_to_async

from bot.models import UserProfile

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    user_id = user.id
    # Проверяем, есть ли пользователь в базе данных
    try:
        user_profile = await sync_to_async(UserProfile.objects.get)(external_id=user_id)
    except UserProfile.DoesNotExist:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='🔴 Вы не зарегистрированы!')

    message = ""
    # Проверяем, является ли пользователь VIP
    if user_profile.is_special:
        message = "Статус: VIP клиент ⭐️⭐️⭐️"
        message += "\n📉 Ваша скидка - 15%"
        message += f"\n🆔 Ваш ID: {user_profile.external_id}"
        message += f"\n💰 Общая сумма заказов: {user_profile.total_spent} руб."
        message += f"\n💵 Сумма текущего заказа: {user_profile.menu_total} руб."
    else:
        discount_percentage = user_profile.calculate_discount_percentage()
        if discount_percentage == 10:
            message = f"Cтатус: Привилегированный клиент ⭐️⭐️"
            message += f"\n🆔 Ваш ID: {user_profile.external_id}"
            message += "\n📉 Ваша скидка максимальная - 10%"
            message += f"\n💰 Общая сумма заказов: {user_profile.total_spent} руб."
            message += f"\n💵 Сумма текущего заказа: {user_profile.menu_total} руб."
        else:
            message = f"Cтатус: Обычный клиент ⭐️"
            message += f"\n🆔 Ваш ID: {user_profile.external_id}"
            message += f"\n📉 Текущая скидка: {discount_percentage}%"
            message += f"\n💰 Общая сумма заказов: {user_profile.total_spent} руб."
            message += f"\n💵 Сумма текущего заказа: {user_profile.menu_total} руб."

    if not user_profile.is_special and discount_percentage != 10:
        # Определяем, сколько еще надо потратить для повышения скидочного процента
        thresholds = { 0: 0, 3: 1000, 5: 2000, 7: 3000, 10: 5000}
        for threshold, amount in thresholds.items():
            if user_profile.total_spent < amount:
                remaining_amount = amount - user_profile.total_spent
                message += f"\n📣 Для повышения скидки до {threshold}% необходимо потратить еще {remaining_amount} руб.\n"
                break
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)
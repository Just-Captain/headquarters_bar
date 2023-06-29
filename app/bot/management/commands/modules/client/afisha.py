from telegram.ext import ContextTypes
from telegram import Update
# Публикация актуальных новостей на неделю
async def afisha(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Афиша")
# Ссылки на источники контактов
from telegram.ext import ContextTypes
from telegram import Update

async def contact(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = "📚 Контакты:\n"
    message += "\\- 💻 [Сайт компании](http://www.example.com)\n"
    message += "\\- 📧 [Email](mailto:info@example.com)\n"
    message += "\\- ☎️ Телефон: \\+79132222234\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='MarkdownV2')
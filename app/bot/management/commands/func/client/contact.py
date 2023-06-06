from bot.management.commands.config import bot

# menu for client after choose 📱 Контакты
@bot.message_handler(func=lambda message: message.text == '📱 Контакты')
def contact_us(message):
    # store info about company
    company_contacts = '''
    Бар "Тропический Оазис"
    Адрес: Улица Пальмовая, 123, Городовия
    Телефон: +1 (555) 123-4567
    Электронная почта: info@tropicaloasisbar.com
    Веб-сайт: www.tropicaloasisbar.com 
    '''
    # if the message too long
    if len(company_contacts) > 4096:
        for x in range(0, len(company_contacts), 4096):
            bot.send_message(message.chat.id, company_contacts[x:x + 4096])

    # if the message normal size
    else:
        bot.send_message(message.chat.id, company_contacts)
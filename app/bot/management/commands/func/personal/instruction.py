from bot.management.commands.config import bot

@bot.message_handler(func=lambda message: message.text == '👆 Инструкция')
def guidelines_for_employee(message):

    # store guidelines for employee
    guidelines_command = '''
    Добро пожаловать в нашу команду!

    На основной панели есть следующие кнопки:
    🤳🏻 Отсканировать код - после отправки фото с qr-кодом будет отправлена считанная из него информация
    🔍 Найти клиента по ID - после ввода ID клиента будет показана информация о нем
    💵 Рассчитать клиента - позволяет создать заказ
    ⌚️ Последние заказы - выводит последние 5 заказов, также позволяет удалить их в случае ошибки
    🔙 Главное меню - выход из меню работника
    '''

    # if the message too long
    if len(guidelines_command) > 4096:
        for x in range(0, len(guidelines_command), 4096):
            bot.send_message(message.chat.id, guidelines_command[x:x + 4096])

    # if the message normal size
    else:
        bot.send_message(message.chat.id, guidelines_command)
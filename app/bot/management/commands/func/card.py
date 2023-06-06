from bot.management.commands.config import bot
from telebot import types
from bot.models import Client
import random


# menu for a client after choose 💳 Виртуальная карта
@bot.message_handler(func=lambda message: message.text == '💳 Виртуальная карта')
def card(message):
    # add a button for share the contact
    send_number = types.KeyboardButton(text='📲 Отправить свои контактные данные', request_contact=True)

    # add a button for back to the main menu
    back = types.KeyboardButton('🔙 Главное меню')

    # add keyboard for share contact
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(send_number, back)

    bot.send_message(message.chat.id, 'Зарегистрируйтесь в системе', reply_markup=keyboard)
    bot.register_next_step_handler(message, get_phone)

# get a client's phone
def get_phone(message):


    # if the client sends a number
    if message.contact is not None:
        # store the client's number
        phone = message.contact.phone_number
        client = Client.objects.get(phone=phone)
        # check if the client exists in the database
        if client != None:

            def get_client_id_by_phone(phone_number):
                if client.phone == phone:
                        return client.unique_id
                return None

            get_id = get_client_id_by_phone(phone)

            # add a button to redirect to the function where a QR code will be generated
            keyboard = types.InlineKeyboardMarkup()
            generate_qr_code = types.InlineKeyboardButton(text='🪄 Вжух и сгенерировался!', callback_data='generate_qr')
            keyboard.add(generate_qr_code)
            bot.send_message(message.chat.id, 'Рады снова Вас видеть, сгенерируйте QR-код!', reply_markup=keyboard)

        else:
            # store the client's phone
            new_id = random.randint(100000, 999999)
            while Client.objects.get(new_id) != None:
                new_id = random.randint(100000, 999999)
                
            new_client = Client(telegram_id=message.chat.id, unique_id=new_id, phone=phone)
            new_client.save()
            
            # add a button to redirect to the next step
            keyboard = types.InlineKeyboardMarkup()
            continue_user_registration = types.InlineKeyboardButton(text='📝 Продолжить заполнение',
                                                                    callback_data='continue')
            keyboard.add(continue_user_registration)

            bot.send_message(message.chat.id, 'Телефон получен. Нажмите кнопку, чтобы продолжить',
                             reply_markup=keyboard)

    # if something went wrong
    else:
        bot.send_message(message.chat.id, '❌ Авторизация не пройдена')

        # get the client's name
"""def get_name(message):
    global client_phone
    global client_id

    # store the client's name
    client_fio = message.text

    # generate a new id for the client
    new_id = random.randint(100000, 999999)
    while new_id in client_id:
        new_id = random.randint(100000, 999999)
    client_id.append(new_id)

    # create a discount and an amount fields
    create_discount = 3
    create_amount = 0

    # add the client's information to client_data
    add_client_info(new_id, client_fio, client_phone[-1], create_amount, create_discount)

    # add the button for redirect to the next step
    keyboard = types.InlineKeyboardMarkup()
    generate_qr_code = types.InlineKeyboardButton(text='🪄 Вжух и сгенерировался!', callback_data=f'generate_qr')
    keyboard.add(generate_qr_code)

    bot.send_message(message.chat.id, 'Осталось только сгенерировать QR-код!', reply_markup=keyboard)"""
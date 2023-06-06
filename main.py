import telebot
from telebot import types
from PIL import Image
from pyzbar.pyzbar import decode
from io import BytesIO
import os
from pyqrcode import QRCode
import png
import json
import random

from config import TOKEN_TELEGRAM

client_id = [0]
old_client_id = [0]
client_phone = []
client_store = []
check_amount_store = []
client_data = {}
employee_phone = ['+79676163430']
order_num = [0]

# get the telegram token
bot = telebot.TeleBot(TOKEN_TELEGRAM)


# handle start command
@bot.message_handler(commands=['start'])
def start(message):
    # add client's buttons
    card = types.KeyboardButton('💳 Виртуальная карта')
    news = types.KeyboardButton('📰 Афиша')
    links = types.KeyboardButton('📱 Контакты')
    back = types.KeyboardButton('🔙 Главное меню')

    # add a client's keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(card, news, links, back)
    bot.send_message(message.chat.id,
                     'Здравствуйте, {0}! Выберете подходящую опцию'.format(message.from_user.first_name),
                     reply_markup=keyboard)


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
    global client_phone
    global old_client_id

    # if the client sends a number
    if message.contact is not None:
        # store the client's number
        phone = message.contact.phone_number

        # check if the client exists in the database
        if phone in client_phone:

            # get a client's id
            def get_client_id_by_phone(phone_number):
                for client_id, client_info in client_data.items():
                    if client_info['phone'] == phone:
                        return client_id
                return None

            get_id = get_client_id_by_phone(phone)
            old_client_id.append(get_id)

            # add a button to redirect to the function where a QR code will be generated
            keyboard = types.InlineKeyboardMarkup()
            generate_qr_code = types.InlineKeyboardButton(text='🪄 Вжух и сгенерировался!', callback_data='generate_qr')
            keyboard.add(generate_qr_code)
            bot.send_message(message.chat.id, 'Рады снова Вас видеть, сгенерируйте QR-код!', reply_markup=keyboard)

        else:
            # store the client's phone
            client_phone.append(phone)

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


# ask for client's name
@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def continue_registration(call):
    bot.send_message(call.message.chat.id, 'Введите Ваше ФИО')

    bot.register_next_step_handler(call.message, get_name)


# get the client's name
def get_name(message):
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

    bot.send_message(message.chat.id, 'Осталось только сгенерировать QR-код!', reply_markup=keyboard)


# generate the client's QR code
@bot.callback_query_handler(func=lambda call: call.data == 'generate_qr')
def generate_qr_code_from_userdata(call):
    # get a client's id
    global client_id
    global old_client_id

    if len(old_client_id) > 1:
        user_id = old_client_id[-1]
    else:
        user_id = client_id[-1]

    # set the file's name
    message_id = call.message.message_id
    qr_file = f'{message_id}.png'

    # generate a user's data to the string
    client_info = client_data.get(user_id)

    if client_info is not None:
        text = f"ID: {user_id}\n"
        text += f"Имя: {client_info['name']}\n"
        text += f"Телефон: {client_info['phone']}\n"
        text += f"Скидка: {client_info['discount']}\n"

    if len(old_client_id) != 0:
        old_client_id.pop()

    # if a client's info wasn't loaded
    else:
        # add a button for back to the main menu
        back = types.KeyboardButton('🔙 Главное меню')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(back)

        bot.send_message(call.message.chat.id, '😢 Что-то пошло не так, попробуйте еще раз', reply_markup=keyboard)

    try:
        # generate the QR code
        qr_code = QRCode(text.encode('utf-8'))

        # save the QR code as image
        qr_code.png(qr_file, scale=10)

        # Send QR code photo
        with open(qr_file, "rb") as photo:
            bot.send_photo(call.message.chat.id, photo, reply_to_message_id=message_id, caption="Ваш QR-код готов!")

        os.remove(qr_file)

    # if something went wrong
    except Exception as e:
        print(e)
        bot.send_message(call.message.chat.id, "😢 Что-то пошло не так, попробуйте еще раз")

    # add a button for back to the main menu
    back = types.KeyboardButton('🔙 Главное меню')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(back)

    bot.send_message(call.message.chat.id, 'Вы можете вернуться в главное меню', reply_markup=keyboard)








# menu for employee
@bot.message_handler(commands=['start_job'])
def choose_employee(message):
    # add button for share contact
    send_number = types.KeyboardButton(text='📲 Отправить свой номер', request_contact=True)

    # add keyboard for share contact
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(send_number)

    bot.send_message(message.chat.id, 'Пройдите авторизацию по номеру телефона', reply_markup=keyboard)


# check if a phone number in the database
@bot.message_handler(content_types=['contact'])
def check_number(message):
    global employee_phone

    # if user shared
    if message.contact is not None:
        # save phone number from contact data
        phone_number = message.contact.phone_number

        # set the flag
        found = False

        # check if a phone number in the database
        for number in employee_phone:
            if number == phone_number:
                # change the flag
                found = True

        # if a number is in the database
        if found:

            # add button for redirect to the next step
            keyboard = types.InlineKeyboardMarkup()
            seccsessful_employee_registration = types.InlineKeyboardButton(text='🫡 Приступить к работе',
                                                                           callback_data='start_job')
            keyboard.add(seccsessful_employee_registration)
            bot.send_message(message.chat.id, 'Авторизация пройдена', reply_markup=keyboard)

        # if a number isn't in the database
        else:
            bot.send_message(message.chat.id, '❌ Авторизация не пройдена')

    # if something went wrong
    else:
        bot.send_message(message.chat.id, '❌ Авторизация не пройдена')



# for an employee after choose 🤳🏻 Отсканировать код
@bot.message_handler(func=lambda message: message.text == '🤳🏻 Отсканировать код')
def scan(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию с QR-кодом")


# transform the qr code to a text
@bot.message_handler(content_types=['photo'])
def decode_qr(message):
    if message.photo:
        # get info about the photo
        photo = message.photo[-1]
        file_id = photo.file_id

        # get info about the file
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path

        # download the file
        downloaded_file = bot.download_file(file_path)

        try:
            # transformate the image in object
            image = Image.open(BytesIO(downloaded_file))

            # decode the image
            qr_codes = decode(image)

            # get info from qr-code
            if qr_codes:
                qr_data = qr_codes[0].data.decode('utf-8')
                bot.send_message(message.chat.id, f"Обнаружен QR-код:\n {qr_data}")
            else:
                bot.send_message(message.chat.id, "QR-код не обнаружен")

        # if something went wrong
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при сканировании QR-кода: {str(e)}")

    # if no photo
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию с QR-кодом")



# ask for an id input
@bot.callback_query_handler(func=lambda call: call.data == 'pay_a_customer_by_id')
def get_id_for_calculate(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, введите id клиента")
    bot.register_next_step_handler(call.message, ask_for_check_amount)


def ask_for_check_amount(message):

    global client_store

    # store a client's id
    client = message.text
    client_store.append(client)

    # search a client's info by id
    client_info = client_data.get(int(client))

    # if a client is in the database
    if client_info is not None:
        bot.send_message(message.chat.id, "Пожалуйста, введите сумму текущего чека")
        bot.register_next_step_handler(message, confirm_the_order)

    # if a client isn't in the database
    else:
        keyboard = types.InlineKeyboardMarkup()
        back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Меню работника', callback_data='start_job')
        keyboard.add(back_to_employee_menu)
        bot.send_message(message.chat.id, 'Такого клиента нет в базе', reply_markup=keyboard)


# ask an employee for confirm the order
def confirm_the_order(message):

    # store a check amount
    check_amount = message.text
    check_amount_store.append(check_amount)

    # keyboard for confirm the order
    keyboard = types.InlineKeyboardMarkup()
    confirm_order = types.InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm')
    back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Отменить заказ', callback_data='start_job')
    keyboard.add(confirm_order, back_to_employee_menu)
    bot.send_message(message.chat.id, f'Вы ввели сумму {check_amount}', reply_markup=keyboard)


# calculate the order
@bot.callback_query_handler(func=lambda call: call.data == 'confirm')
def calculate_the_order(call):

    # get a client's id
    global client_store
    client = client_store[-1]

    # get an order's amount
    global check_amount_store
    check_amount = check_amount_store[-1]

    # get an order's num
    global order_num
    generate_order_num = order_num[-1] + 1
    order_num.append(generate_order_num)

    # get a client's info
    client_info = client_data.get(int(client))

    # add a check amount to the previous amount
    client_info["amount"] += float(check_amount)

    # calculate a discount
    if client_info["amount"] > 300000:
        client_info["discount"] = 15
    elif client_info["amount"] > 150000:
        client_info["discount"] = 7
    elif client_info["amount"] > 50000:
        client_info["discount"] = 5

    # calculate the order's amount
    discount_decimal = client_info["discount"] / 100
    result_amount = float(check_amount) - (float(check_amount) * discount_decimal)

    # print an order's data
    order = {
        "ID клиента": client,
        "Номер заказа": generate_order_num,
        "Сумма без скидки": check_amount,
        "Скидка": client_info["discount"],
        "К оплате": result_amount
    }

    # add an order's data to the log file
    def add_order_to_log(order_info):
        with open('log.json', 'a', encoding='utf-8') as file:
            json.dump(order_info, file, ensure_ascii=False)
            file.write('\n')

    add_order_to_log(order)

    client_store.pop()
    check_amount_store.pop()

    # add a keyboard for back
    keyboard = types.InlineKeyboardMarkup()

    back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Меню работника', callback_data='start_job')
    keyboard.add(back_to_employee_menu)

    # send the order's info
    order_str = f"ID клиента: {order['ID клиента']}\n" \
                f"Номер заказа: {order['Номер заказа']}\nСумма без скидки: {order['Сумма без скидки']}\n" \
                f"Скидка: {order['Скидка']}\nК оплате: {order['К оплате']}\n"
    bot.send_message(call.message.chat.id, order_str, reply_markup=keyboard)


# for an employee after choosing ⌚️ Последние заказы
@bot.message_handler(func=lambda message: message.text == '⌚️ Последние заказы')
def print_orders_log(message):

    # get last orders
    def get_orders_log():
        with open('log.json', 'r', encoding='utf-8') as file:
            last_orders = [json.loads(line) for line in file]
        return last_orders

    send_last_orders = get_orders_log()

    # transform them to string (canceled ignoring)
    orders_str = "Текущие заказы\n"
    inline_keyboard = []
    for order in send_last_orders:
        if not order.get('ОТМЕНА'):
            order_num = order.get('Номер заказа')
            order_str = f"ID: {order.get('ID клиента')}\nНомер заказа: {order_num}\n" \
                        f"Сумма без скидки: {order.get('Сумма без скидки')}\nСкидка: {order.get('Скидка')}\n" \
                        f"К оплате: {order.get('К оплате')}\n"
            orders_str += order_str + "\n"
            cancel_button = types.InlineKeyboardButton(text=f"Отменить заказ №{order_num}",
                                                       callback_data=f"cancel_order_{order_num}")
            inline_keyboard.append(cancel_button)

    # add a keyboard for canceling orders
    keyboard = types.InlineKeyboardMarkup()
    for button in inline_keyboard:
        keyboard.add(button)
    back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Меню работника', callback_data='start_job')
    keyboard.add(back_to_employee_menu)

    bot.send_message(message.chat.id, orders_str, reply_markup=keyboard)


# delete an order after press the button
@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_order_'))
def cancel_order(call):
    # get a list of last orders
    def get_orders_log():
        with open('log.json', 'r', encoding='utf-8') as file:
            last_orders = [json.loads(line) for line in file]
        return last_orders

    # get a client info
    global client_info

    # get an order number
    order_number = call.data.split('_')[2]
    orders = get_orders_log()

    for order in orders:
        if order.get('Номер заказа') == int(order_number):
            order['ОТМЕНА'] = True
            client = order.get('ID клиента')

            # find client info by ID
            with open('log.json', 'r', encoding='utf-8') as file:
                client_orders = [json.loads(line) for line in file if json.loads(line).get('ID клиента') == client]

            # get a client's info
            client_info = client_data.get(int(client))

            # calculate discount and update client info
            for client_order in client_orders:
                client_info["amount"] -= float(client_order.get('Сумма без скидки'))
            if client_info["amount"] > 300000:
                client_info["discount"] = 15
            elif client_info["amount"] > 150000:
                client_info["discount"] = 7
            elif client_info["amount"] > 50000:
                client_info["discount"] = 5

    with open('log.json', 'w', encoding='utf-8') as file:
        for order in orders:
            json.dump(order, file, ensure_ascii=False)
            file.write('\n')

    # send a message to the chat
    bot.send_message(call.message.chat.id, f"Заказ №{order_number} был успешно удален.")


# for an employee after choose 👆 Инструкция
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


# handle back command
@bot.message_handler(func=lambda message: message.text == '🔙 Главное меню')
def back(message):

    # add client's buttons
    card = types.KeyboardButton('💳 Виртуальная карта')
    news = types.KeyboardButton('📰 Афиша')
    links = types.KeyboardButton('📱 Контакты')
    back = types.KeyboardButton('🔙 Главное меню')

    # add client's keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(card, news, links, back)
    bot.send_message(message.chat.id,
                     'Здравствуйте, {0.first_name}! Выберете подходящую опцию'.format(message.from_user),
                     reply_markup=keyboard)


# start the bot
bot.polling(non_stop=True)

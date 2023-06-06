from telebot import types
from bot.management.commands.config import bot
from bot.models import Client

@bot.message_handler(func=lambda message: message.text == '🔍 Найти клиента по ID')
def find_client_by_id(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите id клиента")
    bot.register_next_step_handler(message, get_info)

def get_info(message):
    client_id = message.text 
    client = Client.objects.filter(unique_id=client_id).first()
    if client != None:
        info = f"ID: {client.unique_id}\n"
        info += f"Телефон: {client.phone}\n"
        info += f"Скидка: {client.balance}\n"
        data = f"client_{client.unique_id}"
        calculate_client = types.InlineKeyboardButton(text="💵 Рассчитать клиента", callback_data=data)
        back = types.InlineKeyboardButton(text="🔙 Меню работника", callback_data="back")
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(calculate_client, back)
        bot.send_message(message.chat.id, info, reply_markup=reply_markup, parse_mode="html")
    else: 
        info = "Клиент с указанным ID не найден."
        back = types.KeyboardButton('🔙 Меню работника')
        reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reply_markup.add(back)
        bot.send_message(message.chat.id, info, reply_markup=reply_markup)

@bot.callback_query_handler(func=lambda call: "client_" in call.data)
def pay_a_customer(call):
    print('hdfhdfhfd')
    keyboard = types.InlineKeyboardMarkup()
    pay_a_customer_by_id = types.InlineKeyboardButton(text='🪪 Рассчитать по ID', callback_data='pay_a_customer_by_id')
    back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Меню работника', callback_data='start_job')
    keyboard.add(pay_a_customer_by_id, back_to_employee_menu)
    bot.send_message(call.message.chat.id, 'Выберете опцию', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'pay_a_customer_by_id')
def get_id_for_calculate(call):
    bot.send_message(call.message.chat.id, "Пожалуйста, введите id клиента")
    bot.register_next_step_handler(call.message, ask_for_check_amount)

def ask_for_check_amount(message):
    client_id = message.text
    client = Client.objects.filter(unique_id=client_id).first()
    if client != None:
        client_info = f"ID: {client.unique_id}\n"
        client_info += f"Телефон: {client.phone}\n"
        client_info += f"Скидка: {client.balance}\n" 
        bot.send_message(message.chat.id, client_info) 
        bot.send_message(message.chat.id, "Пожалуйста, введите сумму текущего чека") 
        bot.register_next_step_handler(message, confirm_the_order) 
    else:
        keyboard = types.InlineKeyboardMarkup() 
        back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Меню работника', callback_data='start_job') 
        keyboard.add(back_to_employee_menu)
        bot.send_message(message.chat.id, 'Такого клиента нет в базе', reply_markup=keyboard)

def confirm_the_order(message):
    check_amount = message.text
    keyboard = types.InlineKeyboardMarkup()
    confirm_order = types.InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm')
    back_to_employee_menu = types.InlineKeyboardButton(text='🔙 Отменить заказ', callback_data='start_job')
    keyboard.add(confirm_order, back_to_employee_menu)
    bot.send_message(message.chat.id, f'Вы ввели сумму {check_amount}', reply_markup=keyboard)


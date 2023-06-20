def scan_code(update, context):
    button_text = '🔳 Отсканировать QR-код'
    button_url = 'https://www.online-qr-scanner.com/'
    keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Нажмите кнопку ниже, чтобы открыть сканер QR-кодов:', reply_markup=reply_markup)

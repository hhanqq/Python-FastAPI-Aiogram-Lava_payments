from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text='Список курсов 🔥', callback_data='list_courses')]])

courses = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text='Программирование на python 3.x 👨‍💻', callback_data='python')]])

buy_or_not = InlineKeyboardMarkup(inline_keyboard=
    [[InlineKeyboardButton(text='Купить ✅', callback_data='buy')],
     [InlineKeyboardButton(text='Выйти ❌', callback_data='exit')]])
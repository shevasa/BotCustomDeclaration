from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ready_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='✔️Готово', callback_data='ready')
    ]
])
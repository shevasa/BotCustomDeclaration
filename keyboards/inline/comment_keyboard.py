from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

comment_markup_callback = CallbackData("comment", "action")

comment__inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='✅Добавить', callback_data=comment_markup_callback.new(action='add'))
    ],
    [
        InlineKeyboardButton(text='↩️Изменить', callback_data=comment_markup_callback.new(action='edit'))
    ],
    [
        InlineKeyboardButton(text='❌Отменить', callback_data=comment_markup_callback.new(action='cancel'))
    ]
])
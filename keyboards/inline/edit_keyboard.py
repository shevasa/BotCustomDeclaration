from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

edit_callback = CallbackData("edit_task", "action")

edit_document_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='📸Отправить новые фото', callback_data=edit_callback.new(action="send_new"))
    ],
    [
        InlineKeyboardButton(text='❌Отменить', callback_data=edit_callback.new(action="cancel_editing"))
    ]
])
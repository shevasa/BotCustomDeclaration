from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

edit_document_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='📸Отправить новые фото', callback_data="send_new")
    ],
    [
        InlineKeyboardButton(text='❌Отменить', callback_data="cancel_editing")
    ]
])
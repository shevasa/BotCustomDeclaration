from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

comment_markup_callback = CallbackData("comment", "action")
text_doc_markup_callback = CallbackData("text_doc", 'action', 'document_type_id')

comment_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
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


def get_text_doc_inline_keyboard(document_type_id: int, add_button: bool = True):
    keyboard = InlineKeyboardMarkup()

    add = InlineKeyboardButton(text='✅Добавить',
                               callback_data=text_doc_markup_callback.new(action='add',
                                                                          document_type_id=document_type_id))

    edit = InlineKeyboardButton(text='↩️Изменить',
                                callback_data=text_doc_markup_callback.new(action='edit',
                                                                           document_type_id=document_type_id))

    cancel = InlineKeyboardButton(text='❌Отменить',
                                  callback_data=text_doc_markup_callback.new(action='cancel',
                                                                            document_type_id=document_type_id))
    if add_button:
        keyboard.add(add)

    keyboard.add(edit)
    keyboard.add(cancel)

    return keyboard

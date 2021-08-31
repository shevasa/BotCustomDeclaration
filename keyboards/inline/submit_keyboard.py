from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

comment_markup_callback = CallbackData("comment", "action")
text_doc_markup_callback = CallbackData("text_doc", 'action', 'document_type_id', 'clear_cancel')
admin_comment_callback = CallbackData("admin_comment", 'action', 'task_id')

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


def get_text_doc_inline_keyboard(document_type_id: int, add_button: bool = True, clear: bool = True):
    keyboard = InlineKeyboardMarkup()

    add = InlineKeyboardButton(text='✅Добавить',
                               callback_data=text_doc_markup_callback.new(action='add',
                                                                          document_type_id=document_type_id,
                                                                          clear_cancel=True))

    edit = InlineKeyboardButton(text='↩️Изменить',
                                callback_data=text_doc_markup_callback.new(action='edit',
                                                                           document_type_id=document_type_id,
                                                                           clear_cancel=True))

    cancel = InlineKeyboardButton(text='❌Отменить',
                                  callback_data=text_doc_markup_callback.new(action='cancel',
                                                                             document_type_id=document_type_id,
                                                                             clear_cancel=clear))
    if add_button:
        keyboard.add(add)

    keyboard.add(edit)
    keyboard.add(cancel)

    return keyboard


def get_admin_comment_inline_keyboard(task_id: int):
    keyboard = InlineKeyboardMarkup()

    add = InlineKeyboardButton(text='✅Добавить',
                               callback_data=admin_comment_callback.new(action='add',
                                                                        task_id=task_id))

    edit = InlineKeyboardButton(text='↩️Изменить',
                                callback_data=admin_comment_callback.new(action='edit',
                                                                         task_id=task_id))

    cancel = InlineKeyboardButton(text='❌Отменить',
                                  callback_data=admin_comment_callback.new(action='exit',
                                                                           task_id=task_id))

    keyboard.add(add)

    keyboard.add(edit)
    keyboard.add(cancel)

    return keyboard

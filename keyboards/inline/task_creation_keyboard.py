import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from typing import Union

from loader import db

task_creation_callback = CallbackData("task", 'action', 'document_type_id')
task_creation_else_callback = CallbackData("task_else", 'action')


async def get_task_creation_keyboard(state_data: Union[None, dict]):
    keyboard = InlineKeyboardMarkup()

    all_needed_documents = list(await db.all_needed_documents_by_task_name(state_data.get('task_type_name')))

    for document_dict in all_needed_documents:
        document_type_name = document_dict.get('document_type_name')
        document_type_id = document_dict.get('document_type_id')

        logging.info(f"{bool(state_data[document_type_name])}")

        if not bool(state_data.get(document_type_name)):
            button_text = f"➕Добавить-{document_type_name}"
            callback_data = task_creation_callback.new(action='add', document_type_id=document_type_id)
        else:
            button_text = f"↩️Изменить-{document_type_name}"
            callback_data = task_creation_callback.new(action="edit", document_type_id=document_type_id)

        button = InlineKeyboardButton(text=button_text,
                                      callback_data=callback_data)
        keyboard.add(button)

    if not state_data['comment']:
        comment_button_text = "✍🏼Написать комментарий"
        action = "add_comment"
    else:
        comment_button_text = "↩️Изменить комментарий"
        action = 'edit_comment'

    comment_button = InlineKeyboardButton(text=comment_button_text,
                                          callback_data=task_creation_else_callback.new(action=action))
    send_button = InlineKeyboardButton(text='📤Отправить заявку',
                                       callback_data=task_creation_else_callback.new(action='finish'))

    keyboard.add(comment_button)
    keyboard.add(send_button)

    return keyboard

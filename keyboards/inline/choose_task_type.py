import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from loader import db

choose_task_type_callback = CallbackData("t", "type_name")


async def get_choose_task_type_keyboard():
    keyboard = InlineKeyboardMarkup()
    all_task_types = list(await db.get_all_task_types())
    for task_type_dict in all_task_types:
        task_type_name = task_type_dict.get('task_type_name')
        task_type_emoji = task_type_dict.get('task_type_emoji')
        button = InlineKeyboardButton(text=f'{task_type_name}{task_type_emoji}',
                                      callback_data=choose_task_type_callback.new(type_name=task_type_name))
        keyboard.add(button)
    return keyboard

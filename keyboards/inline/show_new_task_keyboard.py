from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

new_task_callback = CallbackData('show_new_task', "task_id")


def get_new_task_keyboard(task_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='👀Просмотреть заявку', callback_data=new_task_callback.new(task_id=f'{task_id}'))
        ]
    ])
    return keyboard

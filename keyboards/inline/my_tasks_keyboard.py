from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

my_task_callback = CallbackData('my_task', 'action', 'task_id')


def get_my_task_keyboard(task_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='✍🏼Редактировать заявку',
                                 callback_data=my_task_callback.new(action='edit', task_id=task_id))
        ]
    ])
    return keyboard

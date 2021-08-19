from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

worker_task_callback = CallbackData("worker_task", 'action', 'task_id')


def get_worker_new_task_keyboard(task_id: int):
    keyboard = InlineKeyboardMarkup()

    take_to_work = InlineKeyboardButton(text="🛠Принять в работу",
                                        callback_data=worker_task_callback.new(action='take_to_work',
                                                                               task_id=task_id))
    send_to_editing = InlineKeyboardButton(text="📤Отправить на исправление",
                                           callback_data=worker_task_callback.new(action='send_to_editing',
                                                                                  task_id=task_id))

    keyboard.add(take_to_work)
    keyboard.add(send_to_editing)

    return keyboard

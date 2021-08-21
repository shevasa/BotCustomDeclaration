from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

worker_task_callback = CallbackData("worker_task", 'action', 'task_id')
task_in_work_callback = CallbackData("task_in_work", 'action', 'task_id')
task_in_editing_callback = CallbackData("task_in_editing", 'action', 'task_id')


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


def get_worker_task_in_work_keyboard(task_id: int, show_info: bool = True):
    keyboard = InlineKeyboardMarkup()

    show_task_info = InlineKeyboardButton(text='👀Просмотреть заявку',
                                          callback_data=task_in_work_callback.new(action='show_info', task_id=task_id))

    finish_success = InlineKeyboardButton(text='✅Сообщить о готовности',
                                          callback_data=task_in_work_callback.new(action='finish', task_id=task_id))

    if show_info:
        keyboard.add(show_task_info)
    keyboard.add(finish_success)

    return keyboard


def get_worker_task_in_editing_keyboard(task_id: int, show_info: bool = True):
    keyboard = InlineKeyboardMarkup()

    show_task_info = InlineKeyboardButton(text='👀Просмотреть заявку',
                                          callback_data=task_in_editing_callback.new(action='show_info',
                                                                                     task_id=task_id))

    remind_user = InlineKeyboardButton(text='💡Напомнить о необходимости изменить заявку',
                                       callback_data=task_in_editing_callback.new(action='remind_user',
                                                                                  task_id=task_id))

    if show_info:
        keyboard.add(show_task_info)
    keyboard.add(remind_user)

    return keyboard


def get_worker_task_finished_keyboard(task_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f'Заявка №{task_id}', callback_data='finished_task')
        ]
    ])
    return keyboard

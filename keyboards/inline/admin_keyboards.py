from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

admin_ignored_callback = CallbackData('ignored_task', 'action', 'task_id')
admin_system_callback = CallbackData('admin_system', 'action')


def get_admin_ignored_task_keyboard(task_id: int, info: bool = True):
    keyboard = InlineKeyboardMarkup()

    show_info = InlineKeyboardButton(text='👀Просмотреть заявку',
                                     callback_data=admin_ignored_callback.new(action='show_info', task_id=task_id))
    admin_comment = InlineKeyboardButton(text='✍🏼Добавить комментарий админа',
                                         callback_data=admin_ignored_callback.new(action='admin_comment',
                                                                                  task_id=task_id))
    if info:
        keyboard.add(show_info)
    keyboard.add(admin_comment)

    return keyboard


def get_admin_system_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗃Все непринятые заявки МД",
                                 callback_data=admin_system_callback.new(action='show_md'))
        ]
    ])
    return keyboard

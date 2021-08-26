from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import db


async def get_start_worker_keyboard(admin: bool = False):
    n_tasks = int(await db.get_number_of_tasks_by_status_id(1))+int(await db.get_number_of_tasks_by_status_id(4))
    start_worker_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [
            KeyboardButton(
                text=f"📥Заявки на проверку ({n_tasks})")
        ],
        [
            KeyboardButton(text=f"🛠Заявки в работе ({await db.get_number_of_tasks_by_status_id(2)})")
        ],
        [
            KeyboardButton(text=f"🖋Заявки в исправлении ({await db.get_number_of_tasks_by_status_id(3)})")
        ],
        [
            KeyboardButton(text=f"🗃Архив заявок ({await db.get_number_of_tasks_by_status_id(5)})")
        ],
    ])
    admin_system_button = KeyboardButton(text="🧑‍💼Админ система")
    if admin:
        start_worker_keyboard.add(admin_system_button)
    return start_worker_keyboard

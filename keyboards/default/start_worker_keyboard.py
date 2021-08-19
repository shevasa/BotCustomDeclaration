from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_worker_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [
        KeyboardButton(text="📥Новые заявки")
    ],
    [
        KeyboardButton(text="🛠Заявки в работе")
    ],
    [
        KeyboardButton(text="🖋Заявки в исправлении")
    ],
    [
        KeyboardButton(text="🗃Архив заявок")
    ],
])
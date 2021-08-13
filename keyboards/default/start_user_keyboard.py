from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_user_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Оформить заявку✍🏼"),
        KeyboardButton(text="Мои заявки🗃")
    ],
    [
        KeyboardButton(text="Подробние об услугах🔍")
    ],
    [
        KeyboardButton(text="Наши контакты📱")
    ]
], resize_keyboard=True)



import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from asyncpg import UniqueViolationError

from keyboards.default import start_user_keyboard
from loader import dp, db


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = message.from_user
    try:
        user = await db.add_user(telegram_id=user.id,
                                 full_name=user.full_name,
                                 username=user.username,
                                 tg_url=user.url
                                 )
    except UniqueViolationError:
        pass

    await message.answer(f"👋🏻{user.full_name}, рады приветсвовать вас!\n\n"
                         "В этом боте вы можете создать заявку на оформление таких документов:\n"
                         "🔸Т1 ЕС\n"
                         "🔸Т1 Турция\n"
                         "🔹МД\n"
                         "🔸ЭПИ Беларусь\n"
                         "🔹Укр. транзит\n"
                         "🔸ЗДП\n"
                         "Воспользуйтесь клавиатурой для работы с ботом🤖", parse_mode='html',
                         reply_markup=start_user_keyboard)


@dp.message_handler(text="Наши контакты📱")
async def get_our_contact(message: types.Message):
    await message.answer('<b>Брокерское агенство "Транзит Рени":</b>\n\n'
                         "Баланел Александр Николаевич\n"
                         "      📞тел. +380675035983\n"
                         "    📧email: logisticse2e@gmail.com\n\n"
                         "68800, Украина, Одесская область,\n"
                         " г. Рени, ул. дорога Дружбы 1/б"
                         )



from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS
from loader import bot, db


async def send_15_minutes_in_work_alarm(task_id: int):
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_status_id = task_info.get("status_id")
    worker_tg_id = int(task_info.get('worker_tg_id'))
    if task_status_id == 2:
        for admin in ADMINS:
            await bot.send_message(chat_id=admin,
                                   text=f"❗️Заявка №{task_id} находится в работе больше 15 минут❗️",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       InlineKeyboardButton(text="Написать исполнителю МД",
                                                            url=f"tg://user?id={worker_tg_id}")
                                   ]))
    else:
        return


async def send_20_minutes_ignored_alarm(task_id: int):
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_status_id = task_info.get("status_id")
    worker_tg_id = int(task_info.get('worker_tg_id'))
    if task_status_id == 1 or task_status_id == 4:
        for admin in ADMINS:
            await bot.send_message(chat_id=admin, text=f"❗️Заявка №{task_id} непринимается в работу 20 минут❗️",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                       [
                                           InlineKeyboardButton(text="Написать исполнителю МД",
                                                                url=f"tg://user?id={worker_tg_id}")
                                       ]
                                   ]))
    else:
        return

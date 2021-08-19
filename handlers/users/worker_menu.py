import logging

from aiogram import types

from filters import IsWorker
from keyboards.default import start_worker_keyboard
from loader import dp, db


@dp.message_handler(IsWorker(), text="/start")
async def worker_start(message: types.Message):
    await message.answer(f'Здравствуйте {message.from_user.full_name}\n\n'
                         f'Воспользуйтесь клавиатурой для работы с ботом!',
                         reply_markup=start_worker_keyboard)


# @dp.message_handler(IsWorker(), text="📥Новые заявки")
# async def new_tasks(message: types.Message):
#     all_new_tasks = [dict(dictionary) for dictionary in
#                      list(await db.get_tasks_by_status_id(status_id=1))]
#     logging.info(all_new_tasks)
#     for new_task in all_new_tasks:
#         task_text = create_task_for_worker_text(new_task)


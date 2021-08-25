import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from filters import IsWorker
from keyboards.default import get_start_worker_keyboard
from keyboards.inline import get_new_task_keyboard, get_worker_task_in_work_keyboard, task_in_work_callback, \
    get_worker_task_in_editing_keyboard, task_in_editing_callback, get_my_task_keyboard, \
    get_worker_task_finished_keyboard
from loader import dp, db, bot
from utils.misc import create_worker_task_text


@dp.message_handler(IsWorker(), text="/start")
async def worker_start(message: types.Message):
    await message.answer(f'Здравствуйте {message.from_user.full_name}\n\n'
                         f'Воспользуйтесь клавиатурой для работы с ботом!',
                         reply_markup=await get_start_worker_keyboard())


@dp.message_handler(IsWorker(), Text(contains="📥Заявки на проверку"))
async def new_tasks(message: types.Message):
    all_new_tasks = [dict(dictionary) for dictionary in
                     list(await db.get_tasks_by_status_id(status_id=1))]
    all_edited_tasks = [dict(dictionary) for dictionary in
                        list(await db.get_tasks_by_status_id(status_id=4))]
    all_tasks = all_new_tasks + all_edited_tasks
    logging.info(all_tasks)
    if all_tasks:
        for task in all_tasks:
            task_id = task.get('task_id')
            task_text = create_worker_task_text(task)
            await message.answer(text=task_text, reply_markup=get_new_task_keyboard(task_id))
    else:
        await message.answer('📭Новых заявок на данный момент нет!', reply_markup=await get_start_worker_keyboard())


@dp.message_handler(IsWorker(), Text(contains="🛠Заявки в работе"))
async def tasks_in_work(message: types.Message):
    all_tasks_in_work = [dict(dictionary) for dictionary in
                         list(await db.get_tasks_by_status_id(status_id=2))]
    if all_tasks_in_work:
        for task in all_tasks_in_work:
            task_id = task.get('task_id')
            task_text = create_worker_task_text(task)
            await message.answer(text=task_text, reply_markup=get_worker_task_in_work_keyboard(task_id))
    else:
        await message.answer('📭Заявок в работе на данный момент нет!', reply_markup=await get_start_worker_keyboard())


@dp.message_handler(IsWorker(), Text(contains="🖋Заявки в исправлении"))
async def tasks_in_editing(message: types.Message):
    all_tasks_in_work = [dict(dictionary) for dictionary in
                         list(await db.get_tasks_by_status_id(status_id=3))]
    if all_tasks_in_work:
        for task in all_tasks_in_work:
            task_id = task.get('task_id')
            task_text = create_worker_task_text(task)
            await message.answer(text=task_text, reply_markup=get_worker_task_in_editing_keyboard(task_id))
    else:
        await message.answer('📭Заявок в исправлении на данный момент нет!',
                             reply_markup=await get_start_worker_keyboard())


@dp.message_handler(IsWorker(), Text(contains="🗃Архив заявок"))
async def tasks_archive(message: types.Message):
    all_tasks_in_work = [dict(dictionary) for dictionary in
                         list(await db.get_tasks_by_status_id(status_id=5))]
    if all_tasks_in_work:
        for task in all_tasks_in_work:
            task_id = task.get('task_id')
            task_text = create_worker_task_text(task)
            await message.answer(text=task_text, reply_markup=get_worker_task_finished_keyboard(task_id))
    else:
        await message.answer('📭Завершенных заявок на данный момент нет!',
                             reply_markup=await get_start_worker_keyboard())


@dp.callback_query_handler(IsWorker(), task_in_work_callback.filter(action='finish'))
async def finish_task_in_work(call: types.CallbackQuery, callback_data: dict):
    task_id = int(callback_data['task_id'])
    user_tg_id = int(await db.change_task_status(task_id=task_id, new_task_status_id=5))
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_type_name = task_info.get('task_type_name')

    await bot.send_message(chat_id=user_tg_id,
                           text=f"🙌Ваша декларация <b>{task_type_name}</b> (заявка №{task_id}) готова!")

    await call.message.edit_text(f"🎆Заявка <b>№{task_id}</b> обозначена как успешно зевершенная!")


@dp.callback_query_handler(IsWorker(), task_in_editing_callback.filter(action='remind_user'))
async def remind_user(call: types.CallbackQuery, callback_data: dict):
    task_id = int(callback_data['task_id'])
    task_info = dict(await db.get_task_by_task_id(task_id))
    user_tg_id = task_info.get('user_tg_id')
    worker_comment = task_info.get('worker_comment')

    await bot.send_message(chat_id=user_tg_id,
                           text=f"❗️Исполнитель напоминает вам, что нужно отредактировать заявку №{task_id}❗️\n\n" +
                                f"Комментарий исполнителя➡️<b>{worker_comment}</b>",
                           reply_markup=get_my_task_keyboard(task_id))

    await call.message.edit_text(text=f'💡Вы успешно отправили напоминание о необходимости изменить заявку №{task_id}')

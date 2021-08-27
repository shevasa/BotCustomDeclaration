import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline import get_my_task_keyboard, my_task_callback, get_task_creation_keyboard
from loader import dp, db
from states.task_creation_states import Task_creation
from utils.misc import create_my_task_text, create_state_dict


@dp.message_handler(text="Мои заявки🗃")
async def show_tasks(message: types.Message):
    user_tg_id = message.from_user.id

    all_user_tasks = [dict(task) for task in list(await db.get_all_tasks_by_user_tg_id(user_tg_id))]

    await message.answer("👇🏼ВАШИ ЗАЯВКИ👇🏼")
    for task in all_user_tasks:
        task_text = create_my_task_text(task)
        task_id = task.get('task_id')
        task_status_name = task.get('task_status_name')

        if task_status_name == "Завершена" or task_status_name == "Изменённая заявка":
            reply_markup = None
        else:
            reply_markup = get_my_task_keyboard(task_id)

        await message.answer(text=task_text, disable_notification=True, reply_markup=reply_markup)


@dp.callback_query_handler(my_task_callback.filter())
async def edit_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_id = int(callback_data.get('task_id'))
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_type_name = await db.get_task_type_name_by_task_id(task_id)
    comment = task_info.get('comment')
    worker_comment = task_info.get('worker_comment')

    all_needed_documents = list(await db.all_needed_documents_by_task_name(task_type_name))
    await state.update_data(data=create_state_dict(all_needed_documents))
    await state.update_data(task_type_name=task_type_name)
    await state.update_data(comment=comment)

    for dictionary in all_needed_documents:
        document_type_name = dictionary.get('document_type_name')
        document_type_id = dictionary.get('document_type_id')

        all_saved_files = [dict(file) for file in await db.get_all_task_files(task_id, document_type_id)]

        await state.update_data({document_type_name: all_saved_files})

    await state.update_data(my_task_id=task_id)
    if worker_comment:
        await state.update_data(worker_comment=worker_comment)

    state_data = await state.get_data()
    logging.info(state_data)

    text = f"<b>Ваша заявка №{task_id}</b>\n\n" \
           f"Тип услуги: <b>{state_data.get('task_type_name')}</b>\n\n"

    if state_data.get('comment'):
        text += f"Ваш комментарий: <b>{state_data['comment']}</b>\n\n"
    if state_data.get('worker_comment'):
        text += f"Комментарий исполнителя: <b>{worker_comment}</b>\n\n"
    if state_data.get('admin_comment'):
        text += f"Комментарий администратора: <b>{state_data['admin_comment']}</b>\n\n"

    text += f"📲Воспользуйтесь кнопками, чтобы продолжить создание заявки!"

    await call.message.answer(text,
                              reply_markup=await get_task_creation_keyboard(state_data=state_data))
    await Task_creation.create_process.set()

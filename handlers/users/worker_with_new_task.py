import datetime
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from keyboards.default import start_user_keyboard, get_start_worker_keyboard
from keyboards.inline import new_task_callback, get_worker_new_task_keyboard, worker_task_callback, \
    comment_inline_keyboard, comment_markup_callback, get_my_task_keyboard, task_in_work_callback, \
    get_worker_task_in_work_keyboard, task_in_editing_callback, get_worker_task_in_editing_keyboard
from loader import dp, db, bot, scheduler
from utils.misc import create_state_dict
from utils.misc.x_minutes_ignored import send_15_minutes_in_work_alarm


@dp.callback_query_handler(task_in_editing_callback.filter(action='show_info'))
@dp.callback_query_handler(task_in_work_callback.filter(action='show_info'))
@dp.callback_query_handler(comment_markup_callback.filter(action='cancel'), state="comment_confirm")
@dp.callback_query_handler(new_task_callback.filter())
async def show_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_id = int(callback_data.get('task_id')) if callback_data.get('task_id') else int((await state.get_data()).get(
        'task_id'))
    if await state.get_state():
        await state.reset_state()
    logging.info(callback_data)
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_type_name = await db.get_task_type_name_by_task_id(task_id)
    comment = task_info.get('comment')
    worker_comment = task_info.get('worker_comment')

    all_needed_documents = await db.all_needed_documents_by_task_name(task_type_name)
    documents_with_saved_files = create_state_dict(all_needed_documents)

    await call.message.answer(f"=========================")
    await call.message.answer(f"<b>ЗАЯВКА №{task_id}</b>")

    for dictionary in all_needed_documents:
        document_type_name = dictionary.get('document_type_name')
        document_type_id = dictionary.get('document_type_id')

        text_types_id = [dictionary['document_type_id'] for dictionary in
                         list(await db.get_document_type_id_that_can_be_text())]

        all_saved_files = [dict(file) for file in await db.get_all_task_files(task_id, document_type_id)]
        documents_with_saved_files[document_type_name] = all_saved_files

        if document_type_id in text_types_id:
            if all_saved_files:
                await call.message.answer(f'{document_type_name}➡️ '
                                          f"<b>{all_saved_files[0].get('media')}</b>", disable_notification=True)
            else:
                await call.message.answer(f'⬇️{document_type_name}⬇️', disable_notification=True)
                await call.message.answer("----------Пусто---------", disable_notification=True)

        else:
            await call.message.answer(f"⬇️{document_type_name}⬇️", disable_notification=True)
            if all_saved_files:
                await call.message.answer_media_group(media=all_saved_files, disable_notification=True)
            else:
                await call.message.answer("----------Пусто---------", disable_notification=True)

    if comment:
        await call.message.answer(f"Комментарий пользователя➡️ <b>{comment}</b>", disable_notification=True)

    if worker_comment and callback_data['@'] == 'task_in_editing':
        await call.message.answer(f"Комментарий исполнителя➡️ <b>{worker_comment}</b>", disable_notification=True)

    await call.message.answer(f"=========================")

    if callback_data['@'] == 'task_in_work':
        await call.message.answer("Что делаем с этой заявкой?",
                                  reply_markup=get_worker_task_in_work_keyboard(task_id=task_id, show_info=False))
    elif callback_data['@'] == 'task_in_editing':
        await call.message.answer("Что делаем с этой заявкой?",
                                  reply_markup=get_worker_task_in_editing_keyboard(task_id=task_id, show_info=False))
    else:
        await call.message.answer("Что делаем с этой заявкой?",
                                  reply_markup=get_worker_new_task_keyboard(task_id=task_id))


@dp.callback_query_handler(worker_task_callback.filter(action='take_to_work'))
async def take_task_to_work(call: types.CallbackQuery, callback_data: dict):
    worker_tg_id = call.from_user.id
    admin = str(call.message.from_user.id) in ADMINS
    task_id = int(callback_data.get('task_id'))
    user_tg_id = int(await db.change_task_status(task_id=task_id, new_task_status_id=2))

    await call.message.edit_reply_markup()
    await call.message.answer(f"✅Заявка №{task_id} успешно принята в работу",
                              reply_markup=await get_start_worker_keyboard(admin, worker_tg_id))

    await bot.send_message(chat_id=user_tg_id,
                           text=f"✅Ваша заявка №{task_id} успешно принята исполнителем и находиться в работе!",
                           reply_markup=start_user_keyboard)

    time_to_play = datetime.datetime.now() + datetime.timedelta(minutes=2)
    scheduler.add_job(send_15_minutes_in_work_alarm, "date", run_date=time_to_play, args=(task_id, ))


@dp.callback_query_handler(comment_markup_callback.filter(action='edit'), state="comment_confirm")
@dp.callback_query_handler(worker_task_callback.filter(action='send_to_editing'))
async def ask_worker_comment(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.message.answer("✍🏼Напишите комментарий, чтобы пользователь знал, что в заявке нужно изменить!")
    await state.update_data(data=dict(callback_data))
    await state.set_state("worker_comment")


@dp.message_handler(state="worker_comment")
async def send_task_to_editing(message: types.Message, state: FSMContext):
    worker_comment = message.text
    await state.update_data(worker_comment=worker_comment)

    await message.answer(f"Отправить заявку на исправление с этим комментарием: <b>{worker_comment}</b>?",
                         reply_markup=comment_inline_keyboard)

    await state.set_state("comment_confirm")


@dp.callback_query_handler(comment_markup_callback.filter(action='add'), state="comment_confirm")
async def send_task_to_editing(call: types.CallbackQuery, state: FSMContext):
    worker_tg_id = call.message.from_user.id
    admin = str(call.message.from_user.id) in ADMINS

    state_data = await state.get_data()
    logging.info(state_data)

    worker_comment = state_data["worker_comment"]
    task_id = int(state_data.get('task_id'))
    user_tg_id = int(await db.change_task_status(task_id=task_id, new_task_status_id=3, worker_comment=worker_comment))
    task = dict(await db.get_task_by_task_id(task_id))
    task_type_name = str(await db.get_task_type_name_by_task_id(task_id))

    task_text = f"Заявка <b>№{task_id}</b>\n\nТип услуги: <b>{task_type_name}</b>"

    await bot.send_message(chat_id=user_tg_id,
                           text=task_text + f"\n\n‼️Комментарий исполнителя‼️\n<b>{worker_comment}</b>",
                           reply_markup=get_my_task_keyboard(task_id))

    await call.message.answer("📬Заявка отправлена на исправление",
                              reply_markup=await get_start_worker_keyboard(admin, worker_tg_id))

    await state.reset_state()

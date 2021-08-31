import datetime
import logging
from typing import List, Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, MediaGroup, ReplyKeyboardMarkup, KeyboardButton

from filters import Check_text_document
from keyboards.default import start_user_keyboard
from keyboards.inline import get_choose_task_type_keyboard, choose_task_type_callback, get_task_creation_keyboard, \
    task_creation_callback, ready_keyboard, edit_document_keyboard, edit_callback, task_creation_else_callback, \
    comment_markup_callback, get_new_task_keyboard, comment_inline_keyboard, \
    text_doc_markup_callback, get_text_doc_inline_keyboard
from loader import dp, db, bot, scheduler
from states.task_creation_states import Task_creation
from utils.edit_my_task_in_db import edit_my_task
from utils.misc import create_state_dict
from utils.misc.x_minutes_ignored import send_20_minutes_ignored_alarm
from utils.save_new_task_to_db import save_new_task_to_db


@dp.message_handler(text="Оформить заявку✍🏼")
async def choose_task_type(message: types.Message):
    await message.answer("Выберите тип декларации, который хотите оформить",
                         reply_markup=await get_choose_task_type_keyboard())


@dp.callback_query_handler(choose_task_type_callback.filter())
async def start_to_create_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_type_name = callback_data.get('type_name')
    task_type_emoji = str(
        dict(await db.get_task_type_id_and_emoji_by_task_type_name(task_type_name)).get('task_type_emoji'))

    all_needed_documents = list(await db.all_needed_documents_by_task_name(task_type_name))

    await state.update_data(data=create_state_dict(all_needed_documents))
    await state.update_data(task_type_name=task_type_name)
    await state.update_data(comment='')

    await call.message.answer(f"Вы выбрали тип услуги: {task_type_name}{task_type_emoji}\n\n"
                              "📲Воспользуйтесь кнопками, чтобы поочередно отправить все нужные документы",
                              reply_markup=await get_task_creation_keyboard(state_data=await state.get_data()))

    await Task_creation.create_process.set()


@dp.callback_query_handler(text_doc_markup_callback.filter(action='edit'), state=Task_creation.catch_text_file)
@dp.callback_query_handler(task_creation_callback.filter(action='add'), Check_text_document(),
                           state=Task_creation.create_process)
async def ask_text_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    document_type_id = int(callback_data.get('document_type_id'))
    document_to_ask_for = await db.get_document_type_name_by_id(document_type_id)

    await call.message.answer(
        f"✍🏼Напишите всю нужную информацию по поводу документа:\n\n <b>{document_to_ask_for}</b>")

    await Task_creation.catch_text_file.set()
    await state.update_data(now_editing=f"{document_to_ask_for}")

    logging.info(f'{await state.get_data()}')


@dp.callback_query_handler(task_creation_callback.filter(action='add'), state=Task_creation.create_process)
async def ask_for_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    document_type_id = int(callback_data.get('document_type_id'))
    document_to_ask_for = await db.get_document_type_name_by_id(document_type_id)

    await call.message.answer(f"📸Пришлите мне все нужные фото документа: <b>{document_to_ask_for}</b>")

    await Task_creation.catch_photo_file.set()
    await state.update_data(now_editing=f"{document_to_ask_for}")

    logging.info(f'{await state.get_data()}')


@dp.callback_query_handler(task_creation_else_callback.filter(action="edit_comment"),
                           state=Task_creation.create_process)
@dp.callback_query_handler(comment_markup_callback.filter(action='edit'), state=Task_creation.catch_comment)
@dp.callback_query_handler(task_creation_else_callback.filter(action="add_comment"), state=Task_creation.create_process)
async def ask_for_comment(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    if not state_data.get('comment'):
        text = '🖊Отправьте комментарий, который хотите добавить к своей заявке📃'
    else:
        text = '🖊Отправьте новый комментарий, который хотите добавить к своей заявке📃'
    await call.message.answer(text=text)
    await Task_creation.catch_comment.set()


@dp.message_handler(state=Task_creation.catch_text_file)
async def catch_text_document(message: types.Message, state: FSMContext):
    text_document = message.text

    file_dict = {'media': text_document, 'type': message.content_type}

    async with state.proxy() as data:
        now_editing = data.get("now_editing")
        data[now_editing] = [file_dict]
        logging.info(f'{data}')

    document_type_id = int(await db.get_document_type_id_by_doc_name(now_editing))
    await message.answer(f"Добавить к заявке❓\n\n🔸{now_editing}:\n<b>{text_document}</b>",
                         reply_markup=get_text_doc_inline_keyboard(document_type_id))


@dp.message_handler(state=Task_creation.catch_comment)
async def catch_comment(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text

    await message.answer(f"Ваш комментарий: <b>{message.text}</b>\n\n"
                         f"Добавить его к вашей заявке?",
                         reply_markup=comment_inline_keyboard)


@dp.message_handler(is_media_group=True, content_types=[ContentType.PHOTO, ContentType.DOCUMENT],
                    state=Task_creation.catch_photo_file)
async def handle_albums(message: types.Message, album: List[types.Message], state: FSMContext):
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id

        else:
            file_id = obj[obj.content_type].file_id

        file_dict = {'media': file_id, 'type': obj.content_type}

        async with state.proxy() as data:
            now_editing = data.get("now_editing")
            data[now_editing].append(file_dict)
            logging.info(f'{data}')

    await message.answer(f"Нажмите ✔️ГОТОВО, если это все фото документа: <b>{now_editing}</b>.\n\n"
                         f"Если нет, то продалжайте загружать нужные фото!",
                         reply_markup=ready_keyboard)


@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.DOCUMENT], state=Task_creation.catch_photo_file)
async def catch_document(message: types.Message, state: FSMContext):
    file_id = 0
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    file_dict = {'media': file_id, 'type': message.content_type}
    async with state.proxy() as data:
        now_editing = data.get("now_editing")
        data[now_editing].append(file_dict)
        logging.info(f'{data}')

    await message.answer(f"Нажмите ✔️ГОТОВО, если это все фото документа: <b>{now_editing}</b>.\n\n"
                         f"Если нет, то продалжайте загружать нужные фото!",
                         reply_markup=ready_keyboard)


@dp.callback_query_handler(task_creation_callback.filter(action='edit'), Check_text_document(),
                           state=Task_creation.create_process)
async def edit_text_doc(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    document_type_id = int(callback_data.get('document_type_id'))
    document_type_name = await db.get_document_type_name_by_id(document_type_id)

    state_data = await state.get_data()
    text_doc = state_data.get(document_type_name)[0]
    text_doc = text_doc.get('media')

    await call.message.answer(f"{document_type_name}➡️ "
                              f"<b>{text_doc}</b>\n\n"
                              f"Изменить иформацию?",
                              reply_markup=get_text_doc_inline_keyboard(document_type_id=document_type_id,
                                                                        add_button=False, clear=False))
    await Task_creation.catch_text_file.set()


@dp.callback_query_handler(task_creation_callback.filter(action='edit'), state=Task_creation.create_process)
async def ask_for_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    media_group_photo = MediaGroup()
    media_group_document = MediaGroup()

    document_type_id = int(callback_data.get('document_type_id'))
    document_to_edit = await db.get_document_type_name_by_id(document_type_id)

    state_data = await state.get_data()
    all_files_for_this_document = state_data.get(document_to_edit)

    for file_dict in all_files_for_this_document:
        if file_dict['type'] == 'photo':
            media_group_photo.attach(file_dict)
        if file_dict['type'] == 'document':
            media_group_document.attach(file_dict)

    if media_group_document.media:
        await call.message.answer_media_group(media=media_group_document)
    if media_group_photo.media:
        await call.message.answer_media_group(media=media_group_photo)

    await call.message.answer(f"Это фото вашего документа: <b>{document_to_edit}</b>\n\n",
                              reply_markup=edit_document_keyboard)

    await Task_creation.edit_files.set()
    await state.update_data(now_editing=document_to_edit)


@dp.callback_query_handler(edit_callback.filter(action='send_new'), state=Task_creation.edit_files)
async def catch_new_files(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    document_to_edit = state_data.get('now_editing')

    await call.message.answer(f"📸Пришлите мне новые фото документа: <b>{document_to_edit}</b>")
    async with state.proxy() as data:
        data[document_to_edit] = []

    await Task_creation.catch_photo_file.set()


@dp.callback_query_handler(text_doc_markup_callback.filter(action='cancel'), state=Task_creation.catch_text_file)
@dp.callback_query_handler(text_doc_markup_callback.filter(action='add'), state=Task_creation.catch_text_file)
@dp.callback_query_handler(comment_markup_callback.filter(action='cancel'), state=Task_creation.catch_comment)
@dp.callback_query_handler(comment_markup_callback.filter(action='add'), state=Task_creation.catch_comment)
@dp.callback_query_handler(edit_callback.filter(action='cancel_editing'), state=Task_creation.edit_files)
@dp.callback_query_handler(state=Task_creation.catch_photo_file)
async def submit(call: types.CallbackQuery, state: FSMContext, callback_data: Union[None, dict] = None):
    current_state = await state.get_state()
    now_editing = (await state.get_data()).get('now_editing')

    if callback_data is not None and callback_data.get(
            'action') == 'cancel' and current_state == 'Task_creation:catch_text_file':
        if callback_data.get('clear_cancel') == "False":
            pass
        else:
            async with state.proxy() as data:
                data[now_editing] = []

    elif callback_data is not None and callback_data.get(
            'action') == 'cancel' and current_state == 'Task_creation:catch_comment':
        await state.update_data(comment='')

    state_data = await state.get_data()
    logging.info(f"{state_data}")
    worker_comment = state_data.get('worker_comment')

    text = f"<b>Ваша заявка</b>\n\n" \
           f"Тип услуги: <b>{state_data.get('task_type_name')}</b>\n\n"

    if state_data.get('comment'):
        text += f"Ваш комментарий: <b>{state_data['comment']}</b>\n\n"
    elif state_data.get('worker_comment'):
        text += f"Комментарий исполнителя: <b>{worker_comment}</b>"

    text += f"📲Воспользуйтесь кнопками, чтобы продолжить создание заявки!"

    await call.message.answer(text,
                              reply_markup=await get_task_creation_keyboard(state_data=state_data))
    await Task_creation.create_process.set()


@dp.callback_query_handler(task_creation_else_callback.filter(action='finish'), state=Task_creation.create_process)
async def finish_task_creation(call: types.CallbackQuery, state: FSMContext):
    task_id = None
    new_task_id = None

    state_data = await state.get_data()
    logging.info(f'{state_data}')

    if state_data.get('my_task_id'):
        task_id, worker_tg_id = await edit_my_task(state_data)
    else:
        task_type_id = dict(await db.get_task_type_id_and_emoji_by_task_type_name(state_data.get('task_type_name')))[
            'task_type_id']
        task_type_id = int(task_type_id)

        worker_tg_id = int(await db.select_worker_by_task_type_id(task_type_id=task_type_id))

        new_task_id = await save_new_task_to_db(state_data, user_tg_id=call.from_user.id, worker_tg_id=worker_tg_id)

    await call.message.edit_reply_markup()
    await call.message.answer("💾Ваша заявка успешно сохранена и отправлена на обработку",
                              reply_markup=start_user_keyboard)

    await state.reset_state()

    if new_task_id:
        text = f"‼️ Новая заявка от: {call.from_user.get_mention()}"
        await bot.send_message(chat_id=worker_tg_id, text=text,
                               reply_markup=get_new_task_keyboard(new_task_id))

        time_to_play = datetime.datetime.now() + datetime.timedelta(minutes=1)
        scheduler.add_job(send_20_minutes_ignored_alarm, "date", run_date=time_to_play, args=(new_task_id,))

    elif task_id:
        text = f"‼️ Изменённая заявка от: {call.from_user.get_mention()}"
        await bot.send_message(chat_id=worker_tg_id, text=text,
                               reply_markup=get_new_task_keyboard(task_id))

        time_to_play = datetime.datetime.now() + datetime.timedelta(minutes=1)
        scheduler.add_job(send_20_minutes_ignored_alarm, "date", run_date=time_to_play, args=(task_id,))

        # 925075502


@dp.callback_query_handler(task_creation_else_callback.filter(action='exit'), state=Task_creation.create_process)
async def exit_task_creation(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.message.edit_text('🚪Вы вышли из редактора заявки')
    await call.message.answer('⌨️Воспользуйтесь клавиатурой⬇️',
                              reply_markup=start_user_keyboard)

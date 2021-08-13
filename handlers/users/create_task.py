import asyncio
import logging
from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, MediaGroup
from typing import List

from keyboards.inline import get_choose_task_type_keyboard, choose_task_type_callback, get_task_creation_keyboard, \
    task_creation_callback, ready_keyboard, edit_document_keyboard
from loader import dp, db, bot
from states.task_creation_states import Task_creation
from utils.misc import create_state_dict


@dp.message_handler(text="Оформить заявку✍🏼")
async def choose_task_type(message: types.Message, state: FSMContext):
    await message.answer("Выберите тип декларации, который хотите оформить",
                         reply_markup=await get_choose_task_type_keyboard())


@dp.callback_query_handler(choose_task_type_callback.filter())
async def start_to_create_task(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    task_type_name = callback_data.get('type_name')
    task_type_emoji = str(await db.get_task_type_emoji_by_task_type_name(task_type_name))

    all_needed_documents = list(await db.all_needed_documents_by_task_name(task_type_name))

    await state.update_data(data=create_state_dict(all_needed_documents))
    await state.update_data(task_type_name=task_type_name)

    await call.message.answer(f"Вы выбрали тип услуги: {task_type_name}{task_type_emoji}\n\n"
                              "📲Воспользуйтесь кнопками, чтобы поочередно отправить все нужные документы",
                              reply_markup=await get_task_creation_keyboard(state_data=await state.get_data()))

    await Task_creation.create_process.set()

    await state.update_data(data=create_state_dict(all_needed_documents))
    await state.update_data(task_type_name=task_type_name)


@dp.callback_query_handler(task_creation_callback.filter(action='add'), state=Task_creation.create_process)
async def ask_for_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    document_type_id = int(callback_data.get('document_type_id'))
    document_to_ask_for = await db.get_document_type_name_by_id(document_type_id)

    await call.message.answer(f"📸Пришлите мне все нужные фото документа: <b>{document_to_ask_for}</b>")

    await Task_creation.catch_photo_file.set()
    await state.update_data(now_editing=f"{document_to_ask_for}")

    logging.info(f'{await state.get_data()}')


@dp.callback_query_handler(task_creation_callback.filter(action='edit'), state=Task_creation.create_process)
async def ask_for_document(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    media_group = MediaGroup()

    document_type_id = int(callback_data.get('document_type_id'))
    document_to_edit = await db.get_document_type_name_by_id(document_type_id)

    state_data = await state.get_data()
    all_files_for_this_document = state_data.get(document_to_edit)

    for file_dict in all_files_for_this_document:
        media_group.attach(file_dict)

    await call.message.answer_media_group(media=media_group)
    await call.message.answer(f"Это фото вашего документа: {document_to_edit}\n\n",
                              reply_markup=edit_document_keyboard)

    await Task_creation.edit_files.set()
    await state.update_data(now_editing=document_to_edit)


@dp.callback_query_handler(state=Task_creation.edit_files)
async def catch_new_files(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    document_to_edit = state_data.get('now_editing')

    await call.message.answer(f"📸Пришлите мне новые фото документа: <b>{document_to_edit}</b>")
    async with state.proxy() as data:
        data[document_to_edit] = []

    await Task_creation.catch_photo_file.set()


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


@dp.callback_query_handler(state=Task_creation.catch_photo_file)
async def submit(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    logging.info(f"{state_data}")
    await call.message.answer(f"Тип услуги: {state_data.get('task_type_name')}\n\n"
                              f"📲Воспользуйтесь кнопками, чтобы продолжить создание заявки!",
                              reply_markup=await get_task_creation_keyboard(state_data=state_data))
    await Task_creation.create_process.set()

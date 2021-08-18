import logging

from aiogram import types

from keyboards.inline import new_task_callback
from loader import dp, db
from utils.misc import create_state_dict


@dp.callback_query_handler(new_task_callback.filter())
async def show_task(call: types.CallbackQuery, callback_data: dict):
    logging.info(call)
    task_id = int(callback_data.get('task_id'))
    task_info = dict(await db.get_task_by_task_id(task_id))
    task_type_name = await db.get_task_type_name_by_task_id(task_id)
    comment = task_info.get('comment')

    all_needed_documents = await db.all_needed_documents_by_task_name(task_type_name)
    documents_with_saved_files = create_state_dict(all_needed_documents)

    for dictionary in all_needed_documents:
        document_type_name = dictionary.get('document_type_name')
        document_type_id = dictionary.get('document_type_id')

        text_types_id = [dictionary['document_type_id'] for dictionary in
                     list(await db.get_document_type_id_that_can_be_text())]

        all_saved_files = [dict(file) for file in await db.get_all_task_files(task_id, document_type_id)]
        documents_with_saved_files[document_type_name] = all_saved_files

        if document_type_id in text_types_id:
            await call.message.answer(f'⬇️{document_type_name}⬇️', disable_notification=True)
            if all_saved_files:
                await call.message.answer(f"<b>{all_saved_files[0].get('media')}</b>", disable_notification=True)
            else:
                await call.message.answer("----------Пусто---------", disable_notification=True)

        else:
            await call.message.answer(f"⬇️{document_type_name}⬇️", disable_notification=True)
            if all_saved_files:
                await call.message.answer_media_group(media=all_saved_files, disable_notification=True)
            else:
                await call.message.answer("----------Пусто---------", disable_notification=True)

    if comment:
        await call.message.answer(f"Комментарий➡️ <b>{comment}</b>", disable_notification=True)









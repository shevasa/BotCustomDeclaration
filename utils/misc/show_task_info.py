from aiogram import types

from loader import db
from utils.misc import create_state_dict


async def show_task_full_info(call: types.CallbackQuery, task_dict: dict, reply_markup):
    task_id = task_dict.get('task_id')
    task_type_name = task_dict.get('task_type_name')
    comment = task_dict.get('comment')
    worker_comment = task_dict.get('worker_comment')
    status_id = task_dict.get('status_id')

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

    if worker_comment and status_id == 3:
        await call.message.answer(f"Комментарий исполнителя➡️ <b>{worker_comment}</b>", disable_notification=True)

    await call.message.answer(f"=========================")
    await call.message.answer("Что делаем с этой заявкой?",
                              reply_markup=reply_markup)
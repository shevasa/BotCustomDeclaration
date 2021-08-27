from loader import db


async def edit_my_task(state_data: dict):
    task_id = state_data.get('my_task_id')
    task_info = await db.get_task_by_task_id(task_id)
    worker_tg_id = task_info.get('worker_tg_id')

    await db.delete_task_files_by_task_id(task_id)
    await db.change_task_status(task_id, new_task_status_id=4)

    all_needed_documents = list(await db.all_needed_documents_by_task_name(state_data.get('task_type_name')))
    for document_dict in all_needed_documents:
        document_type_name = document_dict.get('document_type_name')
        document_type_id = document_dict.get('document_type_id')

        saved_document_files = state_data.get(document_type_name)

        for file in saved_document_files:
            document_file_id = file.get('media')
            document_content_type = file.get('type')
            await db.save_new_document_to_db(document_file_id=document_file_id, task_id=task_id,
                                             document_type_id=document_type_id,
                                             document_content_type=document_content_type)

    return int(task_id), int(worker_tg_id)


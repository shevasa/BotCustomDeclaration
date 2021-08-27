from loader import db


async def save_new_task_to_db(state_data: dict, user_tg_id, worker_tg_id: int):
    task_type_id = int(
        dict(await db.get_task_type_id_and_emoji_by_task_type_name(state_data.get('task_type_name'))).get(
            'task_type_id'))
    new_task_dict = dict(await db.create_new_task(task_type_id=task_type_id, user_tg_id=user_tg_id,
                                                  comment=state_data.get('comment'), worker_tg_id=worker_tg_id))
    all_needed_documents = list(await db.all_needed_documents_by_task_name(state_data.get('task_type_name')))
    new_task_id = new_task_dict.get('task_id')

    text_types_id = [dictionary['document_type_id'] for dictionary in
                     list(await db.get_document_type_id_that_can_be_text())]

    for document_dict in all_needed_documents:
        document_type_name = document_dict.get('document_type_name')
        document_type_id = document_dict.get('document_type_id')

        saved_document_files = state_data.get(document_type_name)

        for file in saved_document_files:
            if document_type_id in text_types_id:
                document_text = file.get('media')
                document_content_type = file.get('type')
                await db.save_new_text_document_to_db(task_id=new_task_id, document_type_id=document_type_id,
                                                      document_content_type=document_content_type,
                                                      document_text=document_text)
            else:
                document_file_id = file.get('media')
                document_content_type = file.get('type')
                await db.save_new_document_to_db(document_file_id=document_file_id, task_id=new_task_id,
                                                 document_type_id=document_type_id,
                                                 document_content_type=document_content_type)

    return new_task_id

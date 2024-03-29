def create_my_task_text(task: dict):
    task_num = task.get('task_id')
    task_type_name = task.get('task_type_name')
    comment = task.get('comment')
    num_of_files = task.get('num_of_files')
    status_name = task.get('task_status_name')
    text = f"Заявка №{task_num}\n\n"
    if task_type_name:
        text += f"Тип услуги: <b>{task_type_name}</b>\n\n"
    if comment:
        text += f"Комментарий: <b>{comment}</b>\n\n"
    if num_of_files:
        text += f"Количество файлов: <b>{num_of_files}\n\n</b>"
    if status_name:
        text += f"Статус заявки: <b>{status_name}</b>"
    return text


def create_worker_task_text(task: dict):
    task_num = task.get('task_id')
    user_fullname = task.get('full_name')
    task_type_name = task.get('task_type_name')
    comment = task.get('comment')
    status_name = task.get('task_status_name')
    worker_full_name = task.get('worker_full_name')

    text = f"Заявка №{task_num}\n\n"
    if task_type_name:
        text += f"Тип услуги: <b>{task_type_name}</b>\n\n"
    if user_fullname:
        text += f"Автор: <b>{user_fullname}</b>\n\n"
    if worker_full_name:
        text += f"Исполнитель: <b>{worker_full_name}</b>\n\n"
    if comment:
        text += f"Комментарий пользователя: <b>{comment}</b>\n\n"
    if status_name:
        text += f"Статус заявки: <b>{status_name}</b>"

    return text

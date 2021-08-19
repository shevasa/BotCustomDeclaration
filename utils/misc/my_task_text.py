
def create_my_task_text(task: dict):
    task_type_name = task.get('task_type_name')
    comment = task.get('comment')
    num_of_files = task.get('num_of_files')
    status_name = task.get('task_status_name')
    text = ""
    if task_type_name:
        text += f"Тип услуги: <b>{task_type_name}</b>\n\n"
    if comment:
        text += f"Комментарий: <b>{comment}</b>\n\n"
    if num_of_files:
        text += f"Количество файлов: <b>{num_of_files}\n\n</b>"
    if status_name:
        text += f"Статус заявки: <b>{status_name}</b>"
    return text



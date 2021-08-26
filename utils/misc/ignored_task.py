from keyboards.inline import get_admin_ignored_task_keyboard
from loader import db, bot


async def get_ignored_tasks(chat_id: int = 329760591):
    all_md_ignored = [dict(task) for task in list(await db.get_ignored_tasks())]
    await bot.send_message(chat_id=chat_id,
                           text=f"У исполнителя МД есть {len(all_md_ignored)} "
                                f"непринятых заявки, которые были созданы больше чем 1 минута назад")
    for task_dict in all_md_ignored:
        task_id = task_dict.get('task_id')
        task_status_name = task_dict.get('task_status_name')
        task_type_name = task_dict.get('task_type_name')
        user_fullname = task_dict.get('full_name')
        created_at = task_dict.get('created_at')

        text = f"<b>Заявка №{task_id}</b>\n\nСтатус заявки: <b>{task_status_name}</b>\n\n"
        text += f"Тип услуги: <b>{task_type_name}</b>\n\n"
        if user_fullname:
            text += f"Пользователь: <b>{user_fullname}</b>\n\n"
        text += f"Время создания: <b>{created_at}</b>"

        await bot.send_message(chat_id=329760591, text=text,
                               reply_markup=get_admin_ignored_task_keyboard(task_id=int(task_id)))

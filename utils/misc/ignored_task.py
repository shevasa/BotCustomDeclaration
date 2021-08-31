import logging
import datetime

from keyboards.inline import get_admin_ignored_task_keyboard, get_admin_system_keyboard
from loader import db, bot


async def get_ignored_tasks(chat_id: int = 329760591):
    ignored_tasks = [dict(task) for task in list(await db.get_ignored_tasks())]
    logging.info(ignored_tasks)
    worker_tg_id = int(await db.select_worker_by_task_type_id(2))
    num_of_tasks_work = await db.get_number_of_tasks_by_status_id(status_id=2, worker_tg_id=worker_tg_id)
    num_of_task_in_editing = await db.get_number_of_tasks_by_status_id(status_id=3, worker_tg_id=worker_tg_id)
    num_of_finished_tasks_today = await db.get_number_of_tasks_by_status_id(status_id=5, worker_tg_id=worker_tg_id)
    num_of_finished_tasks_month = await db.get_number_of_tasks_by_status_id(status_id=5, worker_tg_id=worker_tg_id,
                                                                            month=True)

    num_of_ignored_tasks = len(ignored_tasks)
    today = datetime.date.today()
    text = "Информацию про работу исполнителя МД:\n\n" \
           f"За сегодня ({today.strftime('%B %d, %Y')})\n\n" \
           f"🔸{num_of_ignored_tasks} непринятых заявки, которым больше 20 минут\n\n" \
           f"🔹{num_of_tasks_work} заявки в работе\n\n" \
           f"🔸{num_of_task_in_editing} заявки в процессе редактирования\n\n" \
           f"🔹{num_of_finished_tasks_today} выполненых заявки\n\n\n" \
           f"За этот месяц ({today.strftime('%B %Y')}) \n\n" \
           f"🔹{num_of_finished_tasks_month} выполненых заявки"
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=get_admin_system_keyboard())


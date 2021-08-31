from loader import db, scheduler
from utils.misc.ignored_task import get_ignored_tasks
from utils.set_bot_commands import set_default_commands


async def on_startup(dp):
    import filters
    import middlewares
    filters.setup(dp)
    middlewares.setup(dp)

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await set_default_commands(dp)

    scheduler.add_job(get_ignored_tasks, "cron", day_of_week='mon-fri', hour='12, 16, 20')

    await db.create()
    await db.create_table_users()
    await db.create_table_workers()
    await db.create_table_document_types()
    await db.create_table_task_status()
    await db.create_table_task_types()
    await db.create_table_worker_task_types()
    await db.create_table_needed_documents()
    await db.create_table_tasks()
    await db.create_table_documents()

    await db.create_and_run_procedure_insert()


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)

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

    scheduler.add_job(get_ignored_tasks, "interval", seconds=20)
    await db.create()
    await db.create_table_users()


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from filters import IsAdmin
from keyboards.default import get_start_worker_keyboard
from keyboards.inline import get_admin_system_keyboard, admin_system_callback, admin_ignored_callback, \
    get_admin_ignored_task_keyboard, comment_inline_keyboard, comment_markup_callback
from loader import dp, db
from utils.misc.show_task_info import show_task_full_info
from utils.misc.ignored_task import get_ignored_tasks


@dp.message_handler(Text(equals="🧑‍💼Админ система"))
async def show_admin_system(message: types.Message):
    ignored_tasks = [dict(task) for task in list(await db.get_ignored_tasks())]
    num_of_tasks_work = await db.get_number_of_tasks_by_status_id(status_id=2, task_type_id=2)
    num_of_task_in_editing = await db.get_number_of_tasks_by_status_id(status_id=3, task_type_id=2)
    num_of_finished_tasks = await db.get_number_of_tasks_by_status_id(status_id=4, task_type_id=2)
    num_of_ignored_tasks = len(ignored_tasks)
    text = "Информацию про работу исполнителя МД:\n\n" \
           f"🔸{num_of_ignored_tasks} непринятых заявки, которым больше 1 минуты\n\n" \
           f"🔹{num_of_tasks_work} заявки в работе\n\n" \
           f"🔸{num_of_task_in_editing} заявки в процессе редактирования\n\n" \
           f"🔹{num_of_finished_tasks} выполненых заявки"
    await message.answer(text=text, reply_markup=get_admin_system_keyboard())


@dp.callback_query_handler(IsAdmin(), comment_markup_callback.filter(action='exit'), state='admin_comment_confirm')
@dp.callback_query_handler(IsAdmin(), admin_system_callback.filter())
async def show_ignored_tasks(call: types.CallbackQuery, state: FSMContext):
    if await state.get_state():
        await state.reset_state()
    await get_ignored_tasks(call.from_user.id)


@dp.callback_query_handler(IsAdmin(), admin_ignored_callback.filter(action='show_info'))
async def show_task_info(call: types.CallbackQuery, callback_data: dict):
    task_id = int(callback_data.get('task_id'))
    task_info = await db.get_task_by_task_id(task_id)
    await show_task_full_info(call=call, task_dict=task_info,
                              reply_markup=get_admin_ignored_task_keyboard(task_id=task_id, info=False))


@dp.callback_query_handler(IsAdmin(), comment_markup_callback.filter(action='edit'), state='admin_comment_confirm')
@dp.callback_query_handler(IsAdmin(), admin_ignored_callback.filter(action='admin_comment'))
async def add_admin_comment(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    task_id = int(callback_data.get('task_id'))
    await call.message.answer(f"Отправьте комментарий от администратора для заявки №{task_id}")
    await state.set_state('catch_admin_comment')
    await state.update_data(task_id=task_id)


@dp.message_handler(IsAdmin(), state='catch_admin_comment')
async def catch_admin_comment(message: types.Message, state: FSMContext):
    admin_comment = message.text

    await state.update_data(admin_comment=admin_comment)

    await message.answer(f"Добавить этот комментарий администратора к заявке: <b>{admin_comment}</b>?",
                         reply_markup=comment_inline_keyboard)

    await state.set_state("admin_comment_confirm")


@dp.callback_query_handler(IsAdmin(), comment_markup_callback.filter(action='add'), state='admin_comment_confirm')
async def confirm_admin_comment(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()

    task_id = state_data.get('task_id')
    admin_comment = state_data.get('admin_comment')

    await db.add_admin_comment_by_task_id(int(task_id), admin_comment)

    await call.message.answer(f'✅Комментарий алминистратора к заявке №{task_id} успешно добавлена',
                              reply_markup=await get_start_worker_keyboard(admin=True))


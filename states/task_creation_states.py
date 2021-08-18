from aiogram.dispatcher.filters.state import StatesGroup, State


class Task_creation(StatesGroup):
    create_process = State()
    catch_photo_file = State()
    catch_text_file = State()
    edit_files = State()
    catch_comment = State()

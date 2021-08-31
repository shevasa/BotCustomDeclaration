from .choose_task_type import get_choose_task_type_keyboard, choose_task_type_callback
from .task_creation_keyboard import get_task_creation_keyboard, task_creation_callback, task_creation_else_callback
from .ready_button_keyboard import ready_keyboard
from .edit_keyboard import edit_document_keyboard, edit_callback
from .submit_keyboard import comment_inline_keyboard, comment_markup_callback, get_text_doc_inline_keyboard, \
    text_doc_markup_callback, admin_comment_callback, get_admin_comment_inline_keyboard
from .show_new_task_keyboard import get_new_task_keyboard, new_task_callback
from .my_tasks_keyboard import get_my_task_keyboard, my_task_callback
from .worker_task_keyboard import get_worker_new_task_keyboard, worker_task_callback, get_worker_task_in_work_keyboard, \
    task_in_work_callback, get_worker_task_in_editing_keyboard, task_in_editing_callback, \
    get_worker_task_finished_keyboard
from .admin_keyboards import get_admin_ignored_task_keyboard, admin_ignored_callback, get_admin_system_keyboard, \
    admin_system_callback


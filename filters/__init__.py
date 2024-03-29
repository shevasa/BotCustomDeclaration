from aiogram import Dispatcher

from filters.IsWorker import IsWorker
from filters.text_document import Check_text_document
from filters.IsAdmin import IsAdmin


def setup(dp: Dispatcher):
    dp.filters_factory.bind(Check_text_document)
    dp.filters_factory.bind(IsWorker)
    dp.filters_factory.bind(IsAdmin)

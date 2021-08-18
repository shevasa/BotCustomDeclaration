from aiogram import Dispatcher

from filters.text_document import Check_text_document


def setup(dp: Dispatcher):
    dp.filters_factory.bind(Check_text_document)

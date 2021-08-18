import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from loader import db


class Check_text_document(BoundFilter):
    async def check(self, call: types.CallbackQuery) -> bool:
        text_types = [dictionary['document_type_id'] for dictionary in
                      list(await db.get_document_type_id_that_can_be_text())]
        document_type_id = int(call.data.split(":")[2])

        if document_type_id in text_types:
            return True
        else:
            return False

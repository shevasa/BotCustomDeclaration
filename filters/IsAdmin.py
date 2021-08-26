import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS


class IsAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        logging.info(ADMINS)
        if str(message.from_user.id) in ADMINS:
            return True
        else:
            return False

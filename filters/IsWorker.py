import logging

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import WORKERS


class IsWorker(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        logging.info(WORKERS)
        if str(message.from_user.id) in WORKERS:
            return True
        else:
            return False

from aiogram import Dispatcher

from .for_albums import AlbumMiddleware
from .throttling import ThrottlingMiddleware


def setup(dp: Dispatcher):
    dp.middleware.setup(ThrottlingMiddleware())
    dp.middleware.setup(AlbumMiddleware())

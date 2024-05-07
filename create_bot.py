import logging
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config


storage = MemoryStorage()  # в данную переменную будем сохранять данные о машино состоянии

# Авторизация бота
bot = Bot(token=config.TB_TOKEN, parse_mode=types.ParseMode.HTML)
# передаем переменную storage в бота
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())  # включаем логирование
logging.basicConfig(level=logging.INFO)

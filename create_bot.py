from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import os


storage = MemoryStorage()

# bot = Bot(token=os.getenv('TOKEN'))
bot = Bot(token='5525955265:AAFgKtqEKaiBSwP9YmvyTw9hFfbOoeNaprg')
dp = Dispatcher(bot, storage=storage)
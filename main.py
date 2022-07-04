import asyncio
from aiogram import Bot, Dispatcher, executor
    # Bot -  класс бота
    # Dispatcher - доставщик update'ов (youtube: Physics is Simple - Разработка телеграм бота на Python(плейлист))
    # executor - запуск бота
from config import BOT_TOKEN


loop = asyncio.new_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop)


def main():
    from handlers import dp, send_to_admin
    executor.start_polling(dp, on_startup=send_to_admin)


if __name__ == '__main__':
    main()

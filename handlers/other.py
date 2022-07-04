from aiogram import types, Dispatcher
from create_bot import bot


# @dp.message_handler()
async def echo_send(message: types.message):
    await message.answer(text=message.text)
    # or
    await message.reply(text=message.text)
    # or
    await bot.send_message(chat_id=message.from_user.id, text=message.text)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)
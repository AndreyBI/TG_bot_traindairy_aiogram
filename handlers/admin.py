from aiogram import types, Dispatcher
from config import admin_id


async def make_changes_command(message: types.Message):
    if message.from_user.id == admin_id:
        await message.reply('Что нужно хозяин?')
    else:
        await message.reply('Ты не хозяин!')


# Регестрируем хэндлеры
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['moderator'])
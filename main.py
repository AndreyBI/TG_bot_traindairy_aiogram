from aiogram.utils import executor
from create_bot import dp
from database import mongo_db


async def on_starup(_):
    print('Bot online')
    mongo_db.sql_start()


from handlers import client, admin, other

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_starup)

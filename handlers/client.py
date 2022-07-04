from aiogram import types, Dispatcher
from create_bot import bot, dp
from keyboards import kb_client
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database import mongo_db
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar



########################################################################################################################
'''***************************************************** Begin ******************************************************'''
########################################################################################################################


# @dp.message_handler(commands='start')
async def command_start(message: types.message):
    exist = await mongo_db.sql_add_users(message)
    sti = open('sticker/AnimatedStickerHello.tgs', 'rb')
    await bot.send_sticker(chat_id=message.from_user.id, sticker=sti)
    if not exist:
        await message.answer(text=f"Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>DiaryOfTraining</b>, бот созданный для хранения данных о твоих тренировках.\nНа данный момент я нахожусь еще в процессе рождения.", parse_mode='html', reply_markup=kb_client)
    else:
        await message.answer(text=f"Привет, {message.from_user.first_name}!\nЧто мы будем делать?", parse_mode='html', reply_markup=kb_client)


########################################################################################################################
'''********************************** Actions when pressing the main menu buttons ***********************************'''
########################################################################################################################


async def history_training(message: types.message):
    await message.answer(text=f"Ищем...", parse_mode='html')


async def add_size(message: types.message):
    await message.answer(text=f"Добавляем...", parse_mode='html')


async def show_size(message: types.message):
    await message.answer(text=f"Смотрим...", parse_mode='html')


########################################################################################################################
'''******************************************* Adding data about training *******************************************'''
########################################################################################################################

class FSMAdmin(StatesGroup):
    date = State()
    type = State()
    description = State()
    dist = State()
    av_speed = State()
    time = State()
    photo = State()


# Начало диалога загрузки нового пункта меню
async def cm_start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text='Небольшая инструкция перед тем, как Вы будете загружать данные о своей тренировке:\n.')
    await nav_cal_handler(message)


# Показ календаря
async def nav_cal_handler(message: types.Message):
    await message.answer("Выберите дату тренировки: ", reply_markup=await SimpleCalendar().start_calendar())


# Выбор даты из календаря
# Поле обязательно
@dp.callback_query_handler(simple_cal_callback.filter())
async def get_date(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.answer(
            f'You selected {date.strftime("%d/%m/%Y")}'
        )
        date_train = date.strftime("%d/%m/%Y")
        await FSMAdmin.date.set()
        async with state.proxy() as data:
            data['date'] = date_train
        await FSMAdmin.next()
        await bot.send_message(chat_id=callback_query.message.chat.id, text='Введите/выберите тип тренировки')


# Вводится тип тренировки: велосипед, бег, плавание...
# Поле обязательно
async def get_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text.replace(" ", "_")
    await FSMAdmin.next()
    await message.reply('Введите описание тренировки')


# Вводится описание тренировки, самочувствие
# Поле необязательно, можно пропустить
async def get_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text.replace(" ", "_")
    await FSMAdmin.next()
    await message.reply('Введите дистанцию (км)')


# Вводится дистанция, которая была преодолена за тренировку
# Поле необязательно, можно пропустить
async def get_dist(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['dist'] = float(message.text.replace(",", "."))
    await FSMAdmin.next()
    await message.reply('Введите среднюю скорость или нажмите "Посчитать"')


# Вводится средняя скорость тренировки
# Поле необязательно, можно пропустить
# При желании, может быть посчитано автоматически, но должно быть расстояни и продолжительность
async def get_av_speed(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['av_speed'] = float(message.text.replace(",", "."))
    await FSMAdmin.next()
    await message.reply('Введите время тренировки\nФормат: ЧЧ ММ')


# Вводится продолжительность тренировки
# Поле необязательно, можно пропустить
async def get_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text.replace(" ", "_")
    await FSMAdmin.next()
    await message.reply('Отправьте фото с тренировки, если хотите. Если нет, нажмите "Пропустить"')


# Загружается фото с тренировки
# Поле необязательно, можно пропустить
async def get_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            data['photo'] = message.photo[0].file_id
        except:
            data['photo'] = 'None'
    await mongo_db.sql_add(state, str(message.from_user.id))
    await state.finish()


# Выход из состояния (добавления тренировки)
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')


########################################################################################################################
'''****************************************** Регистрация хэндлеров *************************************************'''
########################################################################################################################


def register_handlers_client(dp: Dispatcher):
    # Основные команды
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_start, commands=['skip'])
    dp.register_message_handler(command_start, commands=['menu'])

    # Главное меню
    dp.register_message_handler(cm_start, Text(equals='Добавить тренировку', ignore_case=True), state=None)
    dp.register_message_handler(history_training, Text(equals='История тренировок', ignore_case=True))
    dp.register_message_handler(add_size, Text(equals='Добавить измерения', ignore_case=True))
    dp.register_message_handler(show_size, Text(equals='История измерений', ignore_case=True))

    # Отмена добавления данных о тренировке
    dp.register_message_handler(cancel_handler, state="*", commands=['отмена'])
    dp.register_message_handler(cancel_handler, Text(equals=['отмена', 'Отмена', 'отменить', 'Отменить'], ignore_case=True), state="*")

    # Добавление данных о тренировке
    dp.register_callback_query_handler(get_date, state=FSMAdmin.date)
    dp.register_message_handler(get_type, state=FSMAdmin.type)
    dp.register_message_handler(get_description, state=FSMAdmin.description)
    dp.register_message_handler(get_dist, state=FSMAdmin.dist)
    dp.register_message_handler(get_av_speed, state=FSMAdmin.av_speed)
    dp.register_message_handler(get_time, state=FSMAdmin.time)
    dp.register_message_handler(get_photo, content_types=['photo', 'text'], state=FSMAdmin.photo)
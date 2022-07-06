from aiogram import types, Dispatcher
from create_bot import bot, dp
from keyboards import kb_client_main, kb_client_repeat_add_training, kb_skip, kb_skip_or_calc, kb_client_ifNone_add_train
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database import mongo_db
from aiogram_calendar import simple_cal_callback, SimpleCalendar
import re
import asyncio


########################################################################################################################
'''***************************************************** Begin ******************************************************'''
########################################################################################################################


# @dp.message_handler(commands='start')
async def command_start(message: types.message):
    exist = await mongo_db.sql_add_users(message)
    sti = open('sticker/AnimatedStickerHello.tgs', 'rb')
    await bot.send_sticker(chat_id=message.from_user.id, sticker=sti)
    if not exist:
        await message.answer(text=f"Добро пожаловать, {message.from_user.first_name}!\nЯ - <b>DiaryOfTraining</b>, бот созданный для хранения данных о твоих тренировках.\nНа данный момент я нахожусь еще в процессе рождения. Но ты уже можешь добавлять данные о тренировках и смотреть данные о тренировках.", parse_mode='html', reply_markup=kb_client_main)
    else:
        await message.answer(text=f"Привет, {message.from_user.first_name}!\nЧто мы будем делать?", parse_mode='html', reply_markup=kb_client_main)


########################################################################################################################
'''*********************************************** To main menu *****************************************************'''
########################################################################################################################


async def command_menu(message: types.message):
    await message.answer(text=f"И что же мы будем делать?", parse_mode='html', reply_markup=kb_client_main)


########################################################################################################################
'''********************************************** Skip question *****************************************************'''
########################################################################################################################


async def command_skip(message: types.message):
    pass


########################################################################################################################
'''********************************** Actions when pressing the main menu buttons ***********************************'''
########################################################################################################################


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
    time = State()
    av_speed = State()
    photo = State()


method_calendar = True


# Начало диалога загрузки нового пункта меню
async def cm_start(message: types.Message):
    global method_calendar
    method_calendar = True
    await bot.send_message(chat_id=message.from_user.id, text='Небольшая инструкция перед тем, как Вы будете загружать данные о своей тренировке:\nЧтобы отменить добавление тренировки просто напишите "отмена" либо "отменить".')
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
        if method_calendar:
            await callback_query.message.answer(
                f'You selected {date.strftime("%d/%m/%Y")}'
            )
            date_train = date.strftime("%d/%m/%Y")
            await FSMAdmin.date.set()
            async with state.proxy() as data:
                data['date'] = date_train
            await FSMAdmin.next()
            await bot.send_message(chat_id=callback_query.message.chat.id, text='Введите/выберите тип тренировки')
        else:
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
            data_training = date.strftime("%d/%m/%Y")
            await calendar(callback_query, enter=1, data_training=data_training)


# Вводится тип тренировки: велосипед, бег, плавание...
# Поле обязательно
async def get_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text.replace(" ", "_")
    await FSMAdmin.next()
    await message.reply('Введите описание тренировки', reply_markup=kb_skip)


# Вводится описание тренировки, самочувствие
# Поле необязательно, можно пропустить
async def get_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Пропустить':
            data['description'] = 'None'
        else:
            data['description'] = message.text.replace("\n", " => ").replace(" ", "_")
    await FSMAdmin.next()
    await message.reply('Введите дистанцию (км)', reply_markup=kb_skip)


# Вводится дистанция, которая была преодолена за тренировку
# Поле необязательно, можно пропустить
async def get_dist(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Пропустить':
            data['dist'] = 'None'
        else:
            data['dist'] = round(float(message.text.replace(",", ".")), )
    await FSMAdmin.next()
    await message.reply('Введите время тренировки\nФормат: ЧЧ ММ', reply_markup=kb_skip)


# Вводится продолжительность тренировки
# Поле необязательно, можно пропустить
async def get_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Пропустить':
            data['time'] = 'None'
        else:
            time = re.split("\D+", message.text)
            data['time'] = round(int(time[1]) / 60 + int(time[0]), 2)
    await FSMAdmin.next()
    await message.reply('Введите среднюю скорость или нажмите "Посчитать"', reply_markup=kb_skip_or_calc)


# Вводится средняя скорость тренировки
# Поле необязательно, можно пропустить
# При желании, может быть посчитано автоматически, но должно быть расстояние и продолжительность
async def get_av_speed(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Пропустить':
            data['av_speed'] = 'None'
        elif message.text == 'Посчитать' and data['dist'] != 'None' and data['time'] != 'None':
            data['av_speed'] = round(data['dist'] / data['time'], 2)
        else:
            data['av_speed'] = round(float(message.text.replace(",", ".")), 2)
    await FSMAdmin.next()
    await message.reply('Отправьте фото с тренировки, если хотите)', reply_markup=kb_skip)


# Загружается фото с тренировки
# Поле необязательно, можно пропустить
async def get_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == 'Пропустить':
            data['photo'] = 'None'
        else:
            data['photo'] = message.photo[0].file_id
    res = await mongo_db.sql_add_training(state, str(message.from_user.id))
    await state.finish()
    if res:
        await bot.send_message(chat_id=message.chat.id, text='Тренировка успешно добавлена!\nЧем займемся теперь?', reply_markup=kb_client_main)
    else:
        await bot.send_message(chat_id=message.chat.id, text='Приносим извенения, но произошла ошибка и тренирвка не была добавлена.\nПопробуете снова?', reply_markup=kb_client_repeat_add_training)


# Выход из состояния (добавления тренировки)
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK')
    await bot.send_message(chat_id=message.chat.id, text=f'Что будем делать?', reply_markup=kb_client_main)


########################################################################################################################
'''***************************** Actions when pressing the history of training button *******************************'''
########################################################################################################################


data_of_history_training = []
photo_id_last = 0
message_id = 0
chat_id = 0


def text_history_training(page, param=''):
    message = ''
    photo = ''

    if param != '':
        if param > data_of_history_training[0]['date']:
            page = 0
        elif data_of_history_training[-1]['date'] > param:
            page = len(data_of_history_training) - 1
        else:
            for i in range(1, len(data_of_history_training)):
                if data_of_history_training[i]['date'] <= param and param <= data_of_history_training[i - 1]['date']:
                    page = i

    data = data_of_history_training[page]
    headers = ['Дата тренировки: ', 'Тип тренировки: ', 'Описание: ', 'Дистанция (км): ', 'Продолжительность (ч): ', 'Средняя скорость (км/ч): ', 'Фото: ']
    headers_col = ['date', 'type', 'description', 'dist', 'time', 'av_speed', 'photo']

    for i in range(0, len(headers_col)):
        if data[headers_col[i]] == 'None':
            message += headers[i] + 'отсутствует \n'
            photo = data[headers_col[i]]
        elif headers_col[i] == 'photo':
            photo = data['photo']
        elif headers_col[i] == 'type' or headers_col[i] == 'description':
            text_msg = data[headers_col[i]].replace("_", " ")
            message += headers[i] + text_msg + '\n'
        else:
            message += headers[i] + data[headers_col[i]] + '\n'
    return message, photo, page


@dp.callback_query_handler(text_startswith="prev")
async def prev_page(call: types.CallbackQuery):
    global photo_id_last

    if int(call.data.split(":")[1]) > -1:
        page = int(call.data.split(":")[1])
        text, photo, _ = text_history_training(page=page, param='')

        markup = InlineKeyboardMarkup(row_width=3).add(
            InlineKeyboardButton("<<", callback_data=f"prev:{page - 1}:{call.data.split(':')[2]}"),
            InlineKeyboardButton(str(page), callback_data="null"),
            InlineKeyboardButton(">>", callback_data=f"next:{page + 1}:{call.data.split(':')[2]}"),
            InlineKeyboardButton("Выбрать дату", callback_data=f"calendar")
        )

        await call.message.edit_text(text=text, reply_markup=markup)

        if photo_id_last != 0:
            await bot.delete_message(chat_id=call.message.chat.id, message_id=photo_id_last)

        if photo != 'None':
            msg = await bot.send_photo(chat_id=call.message.chat.id, photo=photo)
            photo_id_last = msg['message_id']
        else:
            photo_id_last = 0
    else:
        await bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text='Это последнняя добавленная тренировка!')


@dp.callback_query_handler(text_startswith="next")
async def next_page(call: types.CallbackQuery, date='no_date'):
    global photo_id_last
    global message_id
    global chat_id

    if date == 'no_date':
        if int(call.data.split(":")[1]) < int(call.data.split(":")[2]):
            page = int(call.data.split(":")[1])
            text, photo, _ = text_history_training(page=page, param='')
        else:
            await bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='Это все данные о тренировках!')
            return 0
    else:
        text, photo, page = text_history_training(page=-1, param=date)
        if page == -1:
            await bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text='В этот день не было тренеровки!')
            return 0

    markup = InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("<<", callback_data=f"prev:{page - 1}:{len(data_of_history_training)}:"),
        InlineKeyboardButton(str(page), callback_data="null"),
        InlineKeyboardButton(">>", callback_data=f"next:{page + 1}:{len(data_of_history_training)}"),
        InlineKeyboardButton("Выбрать дату", callback_data=f"calendar")
    )

    if date == 'no_date':
        await call.message.edit_text(text=text, reply_markup=markup)
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=markup)

    if photo_id_last != 0:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=photo_id_last)

    if photo != 'None':
        msg = await bot.send_photo(chat_id=call.message.chat.id, photo=photo)
        photo_id_last = msg['message_id']
    else:
        photo_id_last = 0


@dp.callback_query_handler(text_startswith="calendar")
async def calendar(call: types.CallbackQuery, enter=0, data_training=''):
    if enter == 0:
        global message_id
        global chat_id

        message_id = call.message.message_id
        chat_id = call.message.chat.id

        await asyncio.gather(
            call.answer(),
            nav_cal_handler(call.message)
        )
    else:
        await next_page(call, date=data_training)


async def history_training(message: types.Message):
    global method_calendar
    global data_of_history_training
    global photo_id_last

    method_calendar = False
    data_of_history_training = await mongo_db.sql_search_training(message)

    if data_of_history_training == 'None':
        await message.reply('У вас еще нет добавленых тренировок. Хотите добавить?', reply_markup=kb_client_ifNone_add_train)
    else:
        text, photo, _ = text_history_training(page=0, param='')
        markup = InlineKeyboardMarkup(row_width=3).add(
            InlineKeyboardButton("<<", callback_data=f"prev:-1:{len(data_of_history_training)}"),
            InlineKeyboardButton("0", callback_data="date_history_training"),
            InlineKeyboardButton(">>", callback_data=f"next:1:{len(data_of_history_training)}"),
            InlineKeyboardButton("Выбрать дату", callback_data=f"calendar")
        )
        await message.answer(text=text, reply_markup=markup)

        if photo != 'None':
            msg = await bot.send_photo(chat_id=message.chat.id, photo=photo)
            photo_id_last = msg['message_id']
        else:
            photo_id_last = 0


########################################################################################################################
'''****************************************** Регистрация хэндлеров *************************************************'''
########################################################################################################################


def register_handlers_client(dp: Dispatcher):
    # Основные команды
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_skip, commands=['skip'])
    dp.register_message_handler(command_menu, commands=['menu'])
    dp.register_message_handler(command_menu, Text(equals=['Вернуться в меню'], ignore_case=True))

    # Главное меню
    dp.register_message_handler(cm_start, Text(equals='Добавить тренировку', ignore_case=True), state=None)
    dp.register_message_handler(history_training, Text(equals='История тренировок', ignore_case=True))
    dp.register_message_handler(add_size, Text(equals='Добавить измерения', ignore_case=True))
    dp.register_message_handler(show_size, Text(equals='История измерений', ignore_case=True))

    # Отмена добавления данных о тренировке
    dp.register_message_handler(cancel_handler, state="*", commands=['отмена'])
    dp.register_message_handler(cancel_handler, Text(equals=['отмена', 'отменить'], ignore_case=True), state="*")

    # Добавление данных о тренировке
    dp.register_callback_query_handler(get_date, state=FSMAdmin.date)
    dp.register_message_handler(get_type, state=FSMAdmin.type)
    dp.register_message_handler(get_description, state=FSMAdmin.description)
    dp.register_message_handler(get_dist, state=FSMAdmin.dist)
    dp.register_message_handler(get_time, state=FSMAdmin.time)
    dp.register_message_handler(get_av_speed, state=FSMAdmin.av_speed)
    dp.register_message_handler(get_photo, content_types=['photo', 'text'], state=FSMAdmin.photo)

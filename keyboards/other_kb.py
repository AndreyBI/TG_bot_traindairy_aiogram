from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


btn_skip = KeyboardButton('Пропустить')
kb_skip = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_skip.add(btn_skip)


btn_calc = KeyboardButton('Посчитать')
kb_calc = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_calc.add(btn_calc)


kb_skip_or_calc = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
kb_skip_or_calc.add(btn_skip, btn_calc)
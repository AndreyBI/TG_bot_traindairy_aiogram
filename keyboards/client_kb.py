from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


btn1 = KeyboardButton('Добавить тренировку')
btn2 = KeyboardButton('История тренировок')
btn3 = KeyboardButton('Добавить измерения')
btn4 = KeyboardButton('История измерений')
# btn5 = KeyboardButton('Поделиться номером', request_contact=True)
# btn6 = KeyboardButton('Отправить где я', request_location=True)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
# one_time_keyboard - прячет клавиатуру после выбора ответа, но пользователь может ее открыть. Для удаления 'ReplyKeyboardRemove': bot.send_message(chat_id=message.from_user.id, text=message.text, reply_markup=ReplyKeyboardRemove())


kb_client.add(btn1, btn2, btn3, btn4)
# .add() -  с новой строки                          \
# .insert() - если есть место, то в ту же строчку   | - можно компонировать
# .row() - все в строку                             /
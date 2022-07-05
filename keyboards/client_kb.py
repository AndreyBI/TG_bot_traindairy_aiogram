from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


########################################################################################################################
'''********************************************** Button of main menu ***********************************************'''
########################################################################################################################


btn_main_1 = KeyboardButton('Добавить тренировку')
btn_main_2 = KeyboardButton('История тренировок')
btn_main_3 = KeyboardButton('Добавить измерения')
btn_main_4 = KeyboardButton('История измерений')
# btn5 = KeyboardButton('Поделиться номером', request_contact=True)
# btn6 = KeyboardButton('Отправить где я', request_location=True)
kb_client_main = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
# one_time_keyboard - прячет клавиатуру после выбора ответа, но пользователь может ее открыть. Для удаления 'ReplyKeyboardRemove': bot.send_message(chat_id=message.from_user.id, text=message.text, reply_markup=ReplyKeyboardRemove())
kb_client_main.add(btn_main_1, btn_main_2, btn_main_3, btn_main_4)
# .add() -  с новой строки                          \
# .insert() - если есть место, то в ту же строчку   | - можно компонировать
# .row() - все в строку                             /


########################################################################################################################
'''******************************* Button if we have a problem with connection to DB ********************************'''
########################################################################################################################


btn_repeat_add_train_1 = KeyboardButton('Повторить')
btn_repeat_add_train_2 = KeyboardButton('Вернуться в меню')
kb_client_repeat_add_training = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
kb_client_repeat_add_training.add(btn_repeat_add_train_1, btn_repeat_add_train_2)

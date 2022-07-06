from pymongo import MongoClient

########################################################################################################################
'''************************************* Работа с базой данных (MongoDB) ********************************************'''
########################################################################################################################


# Подключение к базе данных
def sql_start():
    global db
    try:
        client = MongoClient(port=PORT)
        db = client["TG_bot_traindairy"]
        print('Data base connected successfully')
    except:
        print("connection error")


# Проверка наличия пользователя. Если его нету, то добавление данных в БД
async def sql_add_users(message):
    user_col = db['users']
    user_id = message.from_user.id
    exist = True
    if user_col.find_one({"user_id": user_id}) != None:
        print('Old user:', message.from_user.id, ' - ', message.from_user.first_name, ' ', message.from_user.last_name, ' (', message.from_user.username, ')')
    else:
        user_info = {'user_id': user_id, 'first_name': message.from_user.first_name,
                     'username': message.from_user.username, 'last_name': message.from_user.last_name, 'weight': None,
                     'height': None, 'date_of_birth': None}
        user_col.insert_one(user_info)
        print('New user:', message.from_user.id, ' - ', message.from_user.first_name, ' ', message.from_user.last_name, ' (', message.from_user.username, ')')
        exist = False
    return exist


# Добавление данных о тренировке
async def sql_add_training(state, user_id):
    quit = True
    try:
        head_col = ['date', 'type', 'description', 'dist', 'time', 'av_speed', 'photo']
        data_insert = {}
        async with state.proxy() as data:
            begin = str(data.values()).find("'") + 1
            end = str(data.values()).rfind("'")
            new_data = str(data.values())[begin:end]
            new_data = new_data.replace(",", "").replace("'", "").split(" ")
            for i in range(0, len(head_col)):
                data_insert[head_col[i]] = new_data[i]
        col = db[user_id]
        col.insert_one(data_insert)
    except:
        quit = False
    return quit


# Поиск истории тренировок
async def sql_search_training(message):
    try:
        user_col = db[str(message.from_user.id)]
        data = []
        for item in user_col.find({}).sort("date", -1):
            data.append(item)
        return data
    except:
        return 'None'


###################################
# ==== УСТАРЕВШИЙ ФУНКЦИОНАЛ ==== #
###################################

import sqlite3
import time

# Подключение к базам данных
con = sqlite3.connect('./Twig/SQL/db/vodka_balalaika.db')
cur = con.cursor()


# Инициализатор БД
def sqlite_data():
    cur.execute("CREATE TABLE IF NOT EXISTS data(user INTEGER, xp INTEGER, lastTimeEdited INTEGER)")
    con.commit()
    print('[CORE:SQL] Data workers initialized!')


# Получить топ 5 лидеров по XP
def fetch_top_5():
    cur.execute('SELECT user, xp FROM data ORDER BY xp DESC Limit 5')
    data = cur.fetchall()
    temp_data = []

    for elem in data:
        temp_data.append(str(elem[0]) + ' $$$ ' + str(elem[1]))

    data = temp_data
    del temp_data
    return data  # Возвращает список вида ['user.id $$$ xp-balance']...


# Получить список всех пользователей в БД
def fetch_whole_table():
    cur.execute("SELECT user FROM data")
    data = cur.fetchall()
    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data
    del new_data
    return data


# Поиск и получение данных из БД
def fetch_data(fetch_this, where_is, where_val):
    cur.execute(f"SELECT %s FROM data where %s=%s" % (fetch_this, where_is, where_val))
    data = cur.fetchall()
    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data
    del new_data
    # Если данных не существует в БД, то возвращается None
    if len(data) <= 0:
        del data
        return None
    else:
        return data[0]


# Обновление каких-либо параметров в БД
async def update_data(update_this, update_to, where_is, where_val):
    cur.execute(f"UPDATE data SET %s=%s WHERE %s=%s" % (update_this, update_to, where_is, where_val))
    return con.commit()


# Добавление новых пользователей в БД
async def add_user_into_data(user_id):
    called_at = int(time.time() - 300)
    cur.execute("INSERT INTO data VALUES(%s, 0, %s)" % (user_id, called_at))
    con.commit()


# Удаляет пользователя из БД
async def del_user_form_data(user_id):
    cur.execute("DELETE FROM data WHERE user=%s" % user_id)
    con.commit()

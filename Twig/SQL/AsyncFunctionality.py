import sqlite3
import time
import aiosqlite

DEFAULT_DB_FILENAME = 'twig-and-xp'


async def connect_sqlite(filename):
    return await aiosqlite.connect(f'./Twig/SQL/db/{str(filename)}.sqlite')


# Инициализатор БД
async def sqlite_data(db=DEFAULT_DB_FILENAME):
    con = await aiosqlite.connect(f'./Twig/SQL/db/{db}.sqlite')

    await con.execute("CREATE TABLE IF NOT EXISTS data(user INTEGER, xp INTEGER, lastTimeEdited INTEGER)")
    await con.commit()

    await con.close()
    print(f'[CORE:SQL] Database Twig/SQL/db/{db}.sqlite initialized!')


# Получить топ 5 лидеров по XP
async def fetch_top_5(db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    cur = await con.execute('SELECT user, xp FROM data ORDER BY xp DESC Limit 5')
    data = await cur.fetchall()

    temp_data = []

    for elem in data:
        temp_data.append(str(elem[0]) + ' $$$ ' + str(elem[1]))

    data = temp_data

    await cur.close()
    await con.close()
    del con, cur, temp_data

    return data  # Возвращает список вида ['user.id $$$ xp-balance']...


# Получить список всех пользователей в БД
async def fetch_whole_table(db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    cur = await con.execute("SELECT user FROM data")
    data = await cur.fetchall()

    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data

    await cur.close()
    await con.close()
    del new_data, con, cur
    return data


# Поиск и получение данных из БД
async def fetch_data(fetch_this, where_is, where_val, db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    cur = await con.execute(f"SELECT %s FROM data where %s=%s" % (fetch_this, where_is, where_val))
    data = await cur.fetchall()
    new_data = []

    for elem in data:
        new_data.append(elem[0])

    data = new_data
    del new_data
    await cur.close()
    await con.close()
    del con, cur
    # Если данных не существует в БД, то возвращается None
    if len(data) <= 0:
        del data
        return None
    else:
        return data[0]


# Обновление каких-либо параметров в БД
async def update_data(update_this, update_to, where_is, where_val, db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    cur = await con.execute(f"UPDATE data SET %s=%s WHERE %s=%s" % (update_this, update_to, where_is, where_val))

    await con.commit()

    await cur.close()
    await con.close()
    del con, cur


# Добавление новых пользователей в БД
async def add_user_into_data(user_id, db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    called_at = int(time.time() - 300)
    cur = await con.execute("INSERT INTO data VALUES(%s, 0, %s)" % (user_id, called_at))

    await con.commit()
    await cur.close()
    await con.close()
    del con, cur


# Удаляет пользователя из БД
async def del_user_form_data(user_id, db=DEFAULT_DB_FILENAME):
    con = await connect_sqlite(db)

    cur = await con.execute("DELETE FROM data WHERE user=%s" % user_id)
    await con.commit()

    await cur.close()
    await con.close()
    del con, cur


# Функции для нестандартных .sqlite баз

# soon™
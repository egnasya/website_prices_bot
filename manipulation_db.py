import aiosqlite
from datetime import datetime


async def add_user_to_db(user_id, username):

    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()

        await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id	INTEGER PRIMARY KEY,
                            username	TEXT NOT NULL DEFAULT 'no_name')''')
        await cursor.execute('SELECT user_id, username FROM users WHERE user_id = ?', (user_id,))
        if await cursor.fetchone() is None:
            await cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
            await conn.commit()
            print('Пользователь добавлен.')
        else:
            print('Пользователь уже существует.')

        await conn.close()


async def add_or_update_product(user_id, URL, product_name, current_price):

    async with aiosqlite.connect('users_products.db') as conn:
        await conn.execute('BEGIN')
        cursor = await conn.cursor()

        await cursor.execute('''CREATE TABLE IF NOT EXISTS products_users (
                            user_id	INTEGER NOT NULL,
                            URL	TEXT NOT NULL,
                            product_name	TEXT NOT NULL,
                            current_price	REAL NOT NULL,
                            last_update	TEXT NOT NULL DEFAULT 'DATETIME(''now'')',
                            FOREIGN KEY("user_id") REFERENCES "users"("user_id"))''')

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        await cursor.execute('SELECT current_price FROM products_users WHERE user_id =? AND URL =?', (user_id, URL))
        result = await cursor.fetchone()

        if result is None:
            await cursor.execute('INSERT INTO products_users (user_id, URL, product_name, current_price, last_update) '
                                 'VALUES (?, ?, ?, ?, ?)', (user_id, URL, product_name, current_price, now))
            await conn.commit()
            print('Добавлена новая запись.')
        elif int(result[0]) != int(current_price):
            await cursor.execute('UPDATE products_users SET current_price = ?, last_update = ? WHERE user_id = ? AND URL = ?',
                                       (current_price, now, user_id, URL))
            await conn.commit()
            print('Цена продукта изменилась.', int(result[0]), current_price)
        else:
            print('Обновление или добовление новой записи не требуется.')

        await conn.commit()


async def tracking_products(user_id):
    products = []
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('SELECT product_name FROM products_users WHERE user_id = ?', (user_id,))
        results = await cursor.fetchall()

        for result in results:
            products.append(result[0])

        await conn.close()
    return products


async def remove_products(user_id, product_name):
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()
        await cursor.execute('''DELETE FROM products_users
                                WHERE user_id = ? AND product_name = ?''', (user_id, product_name))
        await conn.commit()
        await conn.close()
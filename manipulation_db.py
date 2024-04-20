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


async def add_or_update_product(user_id, URL, product_name, current_price, availability_new):
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        await cursor.execute('''
            SELECT current_price, product_availability FROM products_users
            WHERE user_id = ? AND URL = ?
        ''', (user_id, URL))
        result = await cursor.fetchone()

        if result is None:
            await cursor.execute('''
                INSERT INTO products_users (user_id, URL, product_name, current_price, last_update, product_availability)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, URL, product_name, current_price, now, availability_new))
            print('Добавлена новая запись.')
        else:
            current_price_db, availability_db = result
            if int(current_price_db) != int(current_price) or availability_new != availability_db:
                await cursor.execute('''
                    UPDATE products_users
                    SET current_price = ?, product_availability = ?, last_update = ?
                    WHERE user_id = ? AND URL = ?
                ''', (current_price, availability_new, now, user_id, URL))
                print('Данные продукта обновлены.')

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
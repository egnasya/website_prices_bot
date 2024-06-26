import asyncio
import aiosqlite
from datetime import datetime


async def create_tables():
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()

        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT, 
                start_date TEXT
            )
        ''')

        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS products_users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                URL TEXT,
                product_name TEXT,
                current_price INTEGER,
                last_update TEXT,
                product_availability INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        await conn.commit()


async def add_user_to_db(user_id, username):
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()

        await cursor.execute('SELECT user_id, username, start_date FROM users WHERE user_id = ?', (user_id,))
        existing_user = await cursor.fetchone()

        if existing_user is None:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            await cursor.execute('INSERT INTO users (user_id, username, start_date) VALUES (?, ?, ?)', (user_id, username, current_date))
            await conn.commit()
            print('Пользователь добавлен.')
        else:
            print('Пользователь уже существует.')
            if existing_user[2] is None:  # Если start_date еще не заполнена
                current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                await cursor.execute('UPDATE users SET start_date = ? WHERE user_id = ?', (current_date, user_id))
                await conn.commit()
                print('Дата начала использования ботом добавлена.')

        await cursor.close()


async def add_or_update_product(user_id, URL, product_name, current_price, availability_new):
    async with aiosqlite.connect('users_products.db') as conn:
        cursor = await conn.cursor()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        await cursor.execute('''
            SELECT current_price, product_availability FROM products_users
            WHERE user_id = ? AND URL = ?
        ''', (user_id, URL))
        result = await cursor.fetchone()

        if current_price is None or current_price == '':
            print('Ошибка: Цена не определена или пуста')
        else:
            try:
                current_price = int(current_price)
            except ValueError:
                print('Ошибка: текущая цена содержит недопустимые символы')
                return

        if result is None:
            await cursor.execute('''
                INSERT INTO products_users (user_id, URL, product_name, current_price, last_update, product_availability)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, URL, product_name, current_price, now, availability_new))
            print('Добавлена новая запись: ', product_name, ': ', current_price)
        else:
            current_price_db, availability_db = result
            if int(current_price_db) != int(current_price) or availability_new != availability_db:
                await cursor.execute('''
                    UPDATE products_users
                    SET current_price = ?, product_availability = ?, last_update = ?
                    WHERE user_id = ? AND URL = ?
                ''', (current_price, availability_new, now, user_id, URL))
                print(f'Данные продукта {product_name} обновлены:', URL, '\nСтарая цена:',
                      current_price_db, '\nНовая цена:', current_price, '\nНаличие:', availability_new)

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


asyncio.run(create_tables())
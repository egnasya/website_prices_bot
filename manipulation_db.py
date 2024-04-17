import sqlite3
import datetime


def add_user_to_db(user_id, username):
    conn = sqlite3.connect('users_products.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
	                  user_id	INTEGER PRIMARY KEY,
	                  username	TEXT NOT NULL DEFAULT 'no_name'
	               )''')

    cursor.execute('SELECT user_id, username FROM users WHERE user_id = ?', (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        print('Пользователь добавлен.')
    else:
        print('Пользователь уже существует.')

    conn.close()


def add_or_update_product(user_id, URL, product_name, current_price):
    conn = sqlite3.connect('users_products.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS products_users (
	                  user_id	INTEGER NOT NULL,
	                  URL	TEXT NOT NULL,
	                  product_name	TEXT NOT NULL,
	                  current_price	REAL NOT NULL,
	                  last_update	TEXT NOT NULL DEFAULT 'DATETIME(''now'')',
	                  FOREIGN KEY("user_id") REFERENCES "users"("user_id")
                   )''')

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('SELECT current_price FROM products_users WHERE user_id =? AND URL =?', (user_id, URL))
    result = cursor.fetchone()

    if result is None:
        cursor.execute('INSERT INTO products_users (user_id, URL, product_name, current_price, last_update) VALUES (?, ?, ?, ?, ?)',
                               (user_id, URL, product_name, current_price, now))
        conn.commit()
        print('Добавлена новая запись.')
    elif result[0] != current_price:
        cursor.execute('UPDATE products_users SET current_price = ?, last_update = ? WHERE user_id = ? AND URL = ?',
                                   (current_price, now, user_id, URL))

        conn.commit()
        print('Цена продукта изменилась.')
    else:
        print('Обновление или добовление новой записи не требуется.')

    conn.close()



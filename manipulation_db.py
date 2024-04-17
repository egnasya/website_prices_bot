import sqlite3


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
        print("Пользователь добавлен.")
    else:
        print("Пользователь уже существует.")

    conn.close()

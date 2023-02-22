import sqlite3

connection = sqlite3.connect('weather.db')
cursor = connection.cursor()


cursor.execute('''
    CREATE TABLE User (
        id INTEGER PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')


cursor.execute('''
    CREATE TABLE City (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User(id)
    )
''')


initial_cities = ['New York', 'London', 'Tokyo']
all_users_id = 1 
for city_name in initial_cities:
    cursor.execute('''
        INSERT INTO City (name, user_id)
        VALUES (?, ?)
    ''', (city_name, all_users_id))

connection.commit()
connection.close()


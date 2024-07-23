import sqlite3
import csv
import shutil
from datetime import datetime

def create_connection():
    return sqlite3.connect('anime_list.db')

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                episodes INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS genre (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anime_genre (
                anime_id INTEGER,
                genre_id INTEGER,
                FOREIGN KEY (anime_id) REFERENCES anime (id),
                FOREIGN KEY (genre_id) REFERENCES genre (id),
                PRIMARY KEY (anime_id, genre_id)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                user_id INTEGER,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                PRIMARY KEY (user_id, key)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                anime_id INTEGER,
                rating INTEGER CHECK (rating BETWEEN 1 AND 10),
                review TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (anime_id) REFERENCES anime (id)
            )
        ''')

def add_review(user_id, anime_id, rating, review):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO reviews (user_id, anime_id, rating, review)
            VALUES (?, ?, ?, ?)
        ''', (user_id, anime_id, rating, review))

def update_review(review_id, rating, review):
    conn = create_connection()
    with conn:
        conn.execute('''
            UPDATE reviews
            SET rating = ?, review = ?
            WHERE id = ?
        ''', (rating, review, review_id))

def delete_review(review_id):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM reviews WHERE id = ?', (review_id,))

def get_reviews_for_anime(anime_id):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT users.username, reviews.rating, reviews.review
            FROM reviews
            JOIN users ON reviews.user_id = users.id
            WHERE reviews.anime_id = ?
        ''', (anime_id,))
        return cursor.fetchall()

def get_user_reviews(user_id):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.title, reviews.rating, reviews.review
            FROM reviews
            JOIN anime ON reviews.anime_id = anime.id
            WHERE reviews.user_id = ?
        ''', (user_id,))
        return cursor.fetchall()

def add_anime(title, episodes, status):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO anime (title, episodes, status)
            VALUES (?, ?, ?)
        ''', (title, episodes, status))

def update_anime(anime_id, title, episodes, status):
    conn = create_connection()
    with conn:
        conn.execute('''
            UPDATE anime
            SET title = ?, episodes = ?, status = ?
            WHERE id = ?
        ''', (title, episodes, status, anime_id))

def delete_anime(anime_id):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM anime WHERE id = ?', (anime_id,))

def get_all_anime():
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM anime')
        return cursor.fetchall()

def get_anime_by_id(anime_id):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM anime WHERE id = ?', (anime_id,))
        return cursor.fetchone()

def search_anime_by_title(title):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM anime WHERE title LIKE ?', ('%' + title + '%',))
        return cursor.fetchall()

def filter_anime_by_genre(genre_id):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT anime.*
            FROM anime
            JOIN anime_genre ON anime.id = anime_genre.anime_id
            WHERE anime_genre.genre_id = ?
        ''', (genre_id,))
        return cursor.fetchall()

def filter_anime_by_status(status):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM anime WHERE status = ?', (status,))
        return cursor.fetchall()

def search_anime_by_genres(genre_ids):
    conn = create_connection()
    with conn:
        query = '''
            SELECT DISTINCT anime.*
            FROM anime
            JOIN anime_genre ON anime.id = anime_genre.anime_id
            WHERE anime_genre.genre_id IN ({})
        '''.format(','.join('?' * len(genre_ids)))
        cursor = conn.execute(query, genre_ids)
        return cursor.fetchall()

def filter_anime_by_statuses(statuses):
    conn = create_connection()
    with conn:
        query = 'SELECT * FROM anime WHERE status IN ({})'.format(','.join('?' * len(statuses)))
        cursor = conn.execute(query, statuses)
        return cursor.fetchall()

def export_to_csv(filename):
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM anime')
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cursor.description])
            writer.writerows(cursor)

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'anime_list_backup_{timestamp}.db'
    shutil.copy('anime_list.db', backup_file)
    print(f"Database backed up to {backup_file}.")

def add_preference(user_id, key, value):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO preferences (user_id, key, value)
            VALUES (?, ?, ?)
        ''', (user_id, key, value))

def update_preference(user_id, key, value):
    conn = create_connection()
    with conn:
        conn.execute('''
            UPDATE preferences
            SET value = ?
            WHERE user_id = ? AND key = ?
        ''', (value, user_id, key))

def delete_preference(user_id, key):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM preferences WHERE user_id = ? AND key = ?', (user_id, key))

def get_preferences(user_id):
    conn = create_connection()
    with conn:
        cursor = conn.execute('''
            SELECT key, value
            FROM preferences
            WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchall()
    
def add_genre(name):
    conn = create_connection()
    with conn:
        conn.execute('''
            INSERT INTO genre (name)
            VALUES (?)
        ''', (name,))

def update_genre(genre_id, new_name):
    conn = create_connection()
    with conn:
        conn.execute('''
            UPDATE genre
            SET name = ?
            WHERE id = ?
        ''', (new_name, genre_id))

def delete_genre(genre_id):
    conn = create_connection()
    with conn:
        conn.execute('DELETE FROM genre WHERE id = ?', (genre_id,))

def get_all_genres():
    conn = create_connection()
    with conn:
        cursor = conn.execute('SELECT * FROM genre')
        return cursor.fetchall()

create_table()

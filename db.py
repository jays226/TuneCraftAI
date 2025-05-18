import sqlite3

DATABASE = 'user_data.db'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        spotify_id TEXT UNIQUE,
                        access_token TEXT,
                        refresh_token TEXT,
                        expires_at INTEGER
                    )''')
    conn.commit()
    conn.close()

# Store user data
def store_user_data(spotify_id, access_token, refresh_token, expires_at):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''REPLACE INTO users (spotify_id, access_token, refresh_token, expires_at) 
                      VALUES (?, ?, ?, ?)''', (spotify_id, access_token, refresh_token, expires_at))
    conn.commit()
    conn.close()

# Get user data
def get_user_data(spotify_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE spotify_id = ?', (spotify_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

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
                        expires_at INTEGER,
                        playlists_created INTEGER DEFAULT 0
                    )''')
    conn.commit()
    conn.close()

# Store user data
def store_user_data(spotify_id, access_token, refresh_token, expires_at, playlists_created):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (spotify_id, access_token, refresh_token, expires_at, playlists_created)
                      VALUES (?, ?, ?, ?, ?)
                      ON CONFLICT(spotify_id) DO UPDATE SET
                      access_token = excluded.access_token,
                      refresh_token = excluded.refresh_token,
                      expires_at = excluded.expires_at''', (spotify_id, access_token, refresh_token, expires_at, playlists_created))
    conn.commit()
    conn.close()

# Increment playlist count
def increment_playlist_count(spotify_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET playlists_created = playlists_created + 1 WHERE spotify_id = ?''', (spotify_id,))
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

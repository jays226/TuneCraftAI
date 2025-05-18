from flask import Flask, request, redirect, make_response, url_for, session, render_template
import json
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import os

from db import init_db, store_user_data, get_user_data, increment_playlist_count
import ai


# Initialize the SQLite database
init_db()

#SPOTIPY CONSTANTS

BASE_URL = 'https://api.spotify.com/v1'

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = 'http://127.0.0.1:5000/redirect'

TOKEN_INFO = 'token_info'
PLAYLIST_LIST = []

app = Flask(__name__)

app.config["SESSION_COOKIE_NAME"] = "Spotify Cookie"
app.secret_key = os.urandom(24)

# Flask Routes

@app.route('/')
def main():
    return render_template('home.html')


@app.route('/spotify')
def login():
    print('Initiating Spotify login.')
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info

    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    expires_at = token_info['expires_at']

    sp = spotipy.Spotify(auth=access_token)
    user_data = sp.current_user()
    spotify_id = user_data['id']
    user_data_REAL = get_user_data(spotify_id)
    playlist_count = user_data_REAL[5]

    # Store user data in SQLite
    store_user_data(spotify_id, access_token, refresh_token, expires_at, playlist_count)

    session['spotify_id'] = spotify_id

    return redirect(url_for('home', external=True))


@app.route('/home')
def home():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_user = sp.current_user()

    disp_name = current_user['display_name']
    profile_img = current_user['images'][1]['url'] if len(current_user['images']) > 0 else ''

    return render_template('test.html', name=disp_name, image=profile_img)

@app.route('/logout')
def logout():
    # Clear all session data
    session.pop(TOKEN_INFO, None)
    session.clear()
    print('User logged out. Session cleared.')

    # Redirect directly to the home page
    return redirect(url_for('main'))


@app.route('/playlist', methods=['POST'])
def playlist():
    name = request.form.get('name')
    preferences = request.form.get('preferences')
    number = request.form.get('number')

    playlist_name = str(name)
    search_query = preferences 

    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/spotify')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']

    track_uris = search_tracks(sp, search_query, int(number))
    create_playlist(sp, user_id, playlist_name, track_uris)

    print(f"Playlist '{playlist_name}' created with {len(track_uris)} tracks.")


    return render_template(
        'playlist.html',
        name=playlist_name,
        preferences=preferences
        )
    

@app.route('/profile')
def profile():
    if 'spotify_id' not in session:
        return redirect(url_for('login'))

    spotify_id = session['spotify_id']
    user_data = get_user_data(spotify_id)

    if user_data:
        return render_template('profile.html', spotify_id=user_data[1], playlists_created=user_data[5])
    else:
        return 'User data not found', 404

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login',external = False))
    
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60

    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, 
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=url_for('redirect_page', _external = True),
        scope='user-library-read playlist-read-private user-read-recently-played user-top-read user-read-playback-position user-read-email user-read-private playlist-modify-public',
        show_dialog=True
        )


def parse_playlists(playlists):
    playlists = playlists['items']
    playlist_list = []

    for i in playlists:
        data = {} 
        data['name'] = i['name']
        if('image' in i.keys()):
            data['image'] = i['images'][1]['url']
        data['owner'] = i['owner']['display_name']
        data['id'] = i['id']
        data['tracks'] = i['tracks']['total']
        playlist_list.append(data)

    return playlist_list

    
def create_playlist(sp, user_id, playlist_name, track_uris):
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)
    increment_playlist_count(user_id)

def search_tracks(sp, query, limit):
    ai.save_playlist_to_data(query, limit)

    data_raw = open('data.txt').read().strip('\n')
    print(data_raw)
    playlist_data = json.loads(data_raw)

    results = []
    for song in playlist_data['songs']:
        name = song['song name']
        artist = song['artist']
        q = str(name + " " + artist)
        s = sp.search(q, limit=1, type='track', market=None)

        results.append(s)
    
    track_uris = []
    for track in results:
        t = track['tracks']['items'][0]['uri']
        track_uris.append(t)
    
    return track_uris


app.run(debug=True)

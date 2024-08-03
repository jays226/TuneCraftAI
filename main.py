from flask import Flask, request, redirect, make_response, url_for, session, render_template

import json

import time

import ai



import spotipy
from spotipy.oauth2 import SpotifyOAuth

#CONSTANTS

API_KEY = open("API_KEY", 'r').read()

BASE_URL = 'https://api.spotify.com/v1'

client_id = "c975a477d8ea413badf29f520594844e"
client_secret = "1c88d0b8f5ee4d56bd6daf7fd8b2127f"
redirect_uri = 'http://127.0.0.1:5000/redirect'


######## CHATGPT

# openai.api_key = API_KEY

# response = openai.ChatCompletion(
#     model='gpt-3.5-turbo',
#     message=[
#         {"role": "user", "content": "What is the difference between Celsius and Fahrenheit?"}
#     ]
# )

# print(response)



############





global sp




app = Flask(__name__)

app.config["SESSION COOKIE NAME"] = "Spotify Cookie"
app.secret_key = 'ufhewiuphgfuierhwfu&#3942'

TOKEN_INFO = 'token_info'
PLAYLIST_LIST = []

@app.route('/')
def main():
    return render_template('home.html')


@app.route('/spotify')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('home',external=True))

@app.route('/home')
def home():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect('/spotify')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    current_user = sp.current_user()

    disp_name = current_user['display_name']
    profile_img = current_user['images'][1]['url']
    profile_img_size = current_user['images'][1]['width']

    playlists = sp.current_user_playlists()


    return render_template(
        'test.html',
        name=disp_name, 
        image = profile_img
        )



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
        preferences=preferences
        )
    

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
        client_id=client_id, 
        client_secret=client_secret,
        redirect_uri=url_for('redirect_page', _external = True),
        scope='user-library-read playlist-read-private user-read-recently-played user-top-read user-read-playback-position user-read-email user-read-private playlist-modify-public'
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

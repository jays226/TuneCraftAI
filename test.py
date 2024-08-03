import json
data_raw = open('data.txt').read().strip('\n')

print(data_raw)

playlist_data = json.loads(data_raw)

for song in playlist_data['songs']:
    print(song)

from dotenv import load_dotenv
import os
import base64
from requests import post
import json

import requests

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token



def get_auth_header():
    return {
        "Authorization": "Bearer " + token
    }

def search_for_artist(artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header()
    data = {
        "q": artist_name,
        "type": "artist",
        "limit": "1"
    }
    result = requests.get(url, headers=headers, params=data)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No results found")
        return None
    return json_result[0]

def get_artist_top_tracks(artist_id):
    url = "https://api.spotify.com/v1/artists/" + artist_id + "/top-tracks"
    headers = get_auth_header()
    data = {
        "country": "US"
    }
    result = requests.get(url, headers=headers, params=data)
    json_result = json.loads(result.content)["tracks"]
    return json_result

token = get_token()
#print(token)
result = search_for_artist("The Beatles")
print(result["name"])
artist_id = result["id"]
top_tracks = get_artist_top_tracks(artist_id)
for track in top_tracks:
    print(track["name"])
    print(track["preview_url"])
    print(track["album"]["images"][0]["url"])
    print()


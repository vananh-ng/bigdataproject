import streamlit as st
import requests
import base64
import urllib
import os
import json
from dotenv import load_dotenv

# Your Spotify Developer Dashboard details
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8501/callback"

# Define the scope of access
scope = "user-read-private user-read-email"
auth_url = "https://accounts.spotify.com/authorize"

# Construct the authorization URL
params = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scope,
}
url = f"{auth_url}?{urllib.parse.urlencode(params)}"

st.write(f"Please [click here]({url}) to log in to Spotify")

code = st.text_input("Please enter the code from the URL here:")

if code:
    # Construct the URL for token request
    token_url = "https://accounts.spotify.com/api/token"

    # Construct the headers and body for the token request
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode('utf-8')).decode('utf-8')
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    body = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    # Make the token request
    response = requests.post(token_url, headers=headers, data=body)
    token_data = response.json()

    # Extract the tokens from the response
    access_token = token_data['access_token']
    refresh_token = token_data['refresh_token']

    # You can now use the access_token for making Spotify API requests
    st.write(f"Access Token: {access_token}")
    st.write(f"Refresh Token: {refresh_token}")

    # Get user data
    user_data = get_user_data(access_token)
    st.write(user_data)


def get_auth_header(token):
    return {
        "Authorization": "Bearer " + token
    }

def get_user_data(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = requests.get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def search_for_artist(artist_name, token):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
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

def get_artist_top_tracks(artist_id, token):
    url = "https://api.spotify.com/v1/artists/" + artist_id + "/top-tracks"
    headers = get_auth_header(token)
    data = {
        "country": "US"
    }
    result = requests.get(url, headers=headers, params=data)
    json_result = json.loads(result.content)["tracks"]
    return json_result

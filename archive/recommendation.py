import streamlit as st
import requests
import pandas as pd
import os
import base64
from dotenv import load_dotenv
from requests import post
import json

# Spotify Web API endpoint
SPOTIFY_API_URL = "https://api.spotify.com/v1/recommendations"

# Spotify Developer Dashboard details
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# We first request a token to the Spotify Accounts Service, which will be used later on to access the Spotify Web API
# To get our access token, we need to pass our client ID, client Secret and grant_type
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    # Spotify requests to encode the client ID and client secret using base64
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    # Make the request
    result = post(url,headers= headers, data= data)
    # Convert the result (json) into a python dictionary
    json_result = json.loads(result.content) 
    token = json_result["access_token"]
    return token

# Get the access token
ACCESS_TOKEN = get_token()

# Set up Streamlit
st.title('Spotify Song Recommender')

# User input
target_danceability = st.slider('Danceability', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
target_energy = st.slider('Energy', min_value=0.0, max_value=1.0, value=0.5, step=0.1)
target_tempo = st.slider('Tempo', min_value=0, max_value=200, value=100, step=10)

# Button to fetch recommendations
if st.button('Get Recommendations'):

    # Define headers for the API request
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    # Define the query parameters for the API request
    params = {
        "target_danceability": target_danceability,
        "target_energy": target_energy,
        "target_tempo": target_tempo,
        "limit": 10
    }

    # Make the API request
    response = requests.get(SPOTIFY_API_URL, headers=headers, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Convert the response to JSON
        data = response.json()

        # Create a dictionary to hold song details
        songs = {
            "Artist": [],
            "Song": [],
            "URL": []
        }

        # Loop over the tracks in the response
        for track in data['tracks']:
            # Add the artist, song name, and URL to the dictionary
            songs['Artist'].append(track['artists'][0]['name'])
            songs['Song'].append(track['name'])
            songs['URL'].append(track['external_urls']['spotify'])

        # Convert the dictionary to a pandas DataFrame and display it in Streamlit
        df = pd.DataFrame(songs)
        st.write(df)

    else:
        st.write(f"An error occurred: {response.status_code}")

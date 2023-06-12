import streamlit as st
import requests
from requests import post, get
import base64
import urllib
import os
import json
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px

# Spotify Developer Dashboard details
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print(type(client_secret))

# We first request a token to the Spotify Accounts Service, which will be used later on to access the Spotify Web API
# To get our access token, we need to pass our client ID, client Secret and grant_type
def get_token():
    auth_string = client_id + ':' + client_secret
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

# Function to construct the header to send a request
def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

# Search for an artist and grab the ID (necessary for the request)
def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    #query= {what I want to get}&type= artist, track, playlist, album, artist, playlist, track, show, episode, audiobook.&limit=1 (first artist that pops up, most popular artist)
    # market="ES" for Spain e.g.
    query= f"?q={artist_name}&type=artist&limit=1"
    # Combine query+url
    query_url = url + query
    result = get(query_url, headers= headers)
    # Convert the result (json) into a python dictionary
    json_result = json.loads(result.content)["artists"]["items"]
    
    if len(json_result) == 0:
        print("No artist with this name exists...")
        return None
    
    return json_result[0]
    

# Get the songs from the artist
def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

# Get new releases
def get_new_releases(country):
    url= f"https://api.spotify.com/v1/browse/new-releases?country={country}&limit=1"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['albums']['items'][0]['name']
    return json_result


token = get_token()
#result = search_for_artist(token, "ACDC" )
#artist_id = result["id"] # With this ID I can search for songs of the artist
#songs = get_songs_by_artist(token, artist_id)
#print(songs)
#for idx, song in enumerate(songs):
#    print(f"{idx +1}. {song['name']}")

new_releases= get_new_releases("AR")
#new_releases_name= new_releases['albums']['items'][0]['name']
#new_releases_artist= new_releases['albums']['items'][0]['artists']
#artist_names = [artist['name'] for artist in new_releases_artist]
#for name in artist_names:
 #   print(name)


#code = st.write()
# generate a df. Assign via the function a new column with the new releases. Based on that generate the map. Will it be updated when refresh?
# https://plotly.com/python/scatter-plots-on-maps/

# Read country data
df_countries= pd.read_excel(r'C:\Users\sofia\OneDrive\Documentos\GitHub\bigdataproject\app\data\country-available-final.xlsx')
df_countries.iloc[115,4]='NA' #Modify for Namibia: it detects NaN instead of NA country code

# Get new releases per country
df_countries['new_releases']= [get_new_releases(df_countries.loc[index,'country_code']) for index in range(len(df_countries))]

# Plot the map
fig = px.scatter_geo(df_countries, lat='cap_lat', lon= 'cap_lon',
                     hover_name='new_releases', color='country'
                     ) #text= 'country'
st.plotly_chart(fig, use_container_width=False)
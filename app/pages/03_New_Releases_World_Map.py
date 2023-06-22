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
import pickle

st.set_page_config(page_title="Spotify Big Data Project", 
                   #page_icon=":musical_note:", 
                   layout="wide"
                   )

# Spotify Developer Dashboard details
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print(type(client_secret))

# We first request a token to the Spotify Accounts Service, which will be used later on to access the Spotify Web API
# To get our access token, we need to pass our client ID, client Secret and grant_type

# Get Spotify token    
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

token = get_token()

# Function to construct the header to send a request
def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

#query= {what I want to get}&type= artist, track, playlist, album, artist, playlist, track, show, episode, audiobook.&limit=1 (first artist that pops up, most popular artist)

# Read country data
with open(r"./data/new_releases.pkl", 'rb') as file:
    df_countries = pickle.load(file)


# Plot the map
fig = px.scatter_geo(df_countries, lat='cap_lat', lon= 'cap_lon',
                     hover_name='new_releases', color='country',
                     hover_data={'cap_lat': False, # Don't show latitude and longitud
                                 'cap_lon': False,
                                 'artist': True,   # Show artist and country
                                 'country': True}
)
                     

# Update the layout with the desired colors

fig.update_layout(
    title= 'Hover over the map to see the new albumns worldwide',
    geo=dict(
        bgcolor='#262730',  # Set the background color to black
        showland=True,
        landcolor='white',  # Set the color of land areas to white
        showocean=True,
        oceancolor='#262730',  # Set the color of ocean areas to black
        showlakes=True,
        lakecolor='white'  # Set the color of lakes to white
    ),
    font=dict(
        color='white'  # Set the text color to white
    ),
    autosize= False,
    width=800,
    height= 600
)
st.title('New releases World Map')
st.plotly_chart(fig, use_container_width=True)



# Display the tracks of the album

# Get the new release ID, so that later we can search for the tracks
def get_new_releases_id(country):
    # Find the country code for the given country name
    row = df_countries[df_countries['country'] == country]
    country_code = row.iloc[0]['country_code']
    url= f"https://api.spotify.com/v1/browse/new-releases?country={country_code}&limit=1"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['albums']['items'][0]['id']
    return json_result

# With the ID, get the tracks of that album
def tracks_from_album(country):
    album_id= get_new_releases_id(country)
    url= f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit=15"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    tracks_data= []
    for item in json_result['items']:
        name=item['name']
        number= item['track_number']
        tracks_data.append({'Track Number': number, 'Track': name})
    tracks_df= pd.DataFrame(tracks_data)
    return tracks_df

# Use the sidebar method for the input and button
country= st.sidebar.selectbox(
    'Select a country to see the latest album and its tracks', (df_countries['country']))
selected_tracks= tracks_from_album(country)
selected_album= df_countries.loc[df_countries['country']== country,'new_releases'].values[0]
selected_artist= df_countries.loc[df_countries['country']== country,'artist'].values[0]

st.sidebar.write(f"The latest Album in **{country}** is **{selected_album}** by **{selected_artist}**")
st.sidebar.write('Are you curious about its tracks? Check them out!🎧')
st.sidebar.dataframe(selected_tracks, hide_index=True, use_container_width= True)
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from dotenv import load_dotenv
import os
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import pandas as pd

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

st.set_page_config(page_title="Song Recommendation", page_icon=":musical_note:", layout="wide")

@st.cache(allow_output_mutation=True)
def load_data():
    df =  pd.read_csv("app/data/SpotGentrack/Data_Sources/filtered_track_df.csv")
    df['genres'] = df['genres'].apply(lambda x: x.replace("'", "").replace("[", "").replace("]", "").split(", "))
    exploded_track_df = df.explode('genres')
    return exploded_track_df

genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Pop', 'Pop Dance', 'Pop Rap', 'Rap', 'Tropical House']
audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "valence"]

exploded_track_df = load_data()

# knn model
def n_neighbors_uri_audio(genre, start_year, end_year, test_feat):
    genre = genre.lower()
    genre_data = exploded_track_df[(exploded_track_df["genres"]==genre) & (exploded_track_df["release_year"]>=start_year) & (exploded_track_df["release_year"]<=end_year)]
    genre_data = genre_data.sort_values(by='popularity', ascending=False)[:500]
    neigh = NearestNeighbors()
    neigh.fit(genre_data[audio_feats].to_numpy())
    n_neighbors = neigh.kneighbors([test_feat],       n_neighbors=len(genre_data), return_distance=False)[0]
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

# app configuration
title = "Song Recommendation Engine"
st.title(title)
st.write("First of all, welcome! This is the place where you can customize what you want to listen to based on genre and several key audio features. Try playing around with different settings and listen to the songs recommended by our system!")
st.markdown("##")
with st.container():
    col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
    with col3:
        st.markdown("***Choose your genre:***")
        genre = st.radio(
            "",
            genre_names, index=genre_names.index("Pop"))
    with col1:
        st.markdown("***Choose features to customize:***")
        start_year, end_year = st.slider(
            'Select the year range',
            1990, 2019, (2015, 2019)
        )
        acousticness = st.slider(
            'Acousticness',
            0.0, 1.0, 0.5)
        danceability = st.slider(
            'Danceability',
            0.0, 1.0, 0.5)
        energy = st.slider(
            'Energy',
            0.0, 1.0, 0.5)
        instrumentalness = st.slider(
            'Instrumentalness',
            0.0, 1.0, 0.0)
        valence = st.slider(
            'Valence',
            0.0, 1.0, 0.45)
        tempo = st.slider(
            'Tempo',
            0.0, 244.0, 118.0)


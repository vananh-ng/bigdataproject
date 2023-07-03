import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import os
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import openai


# API Management
load_dotenv(find_dotenv(".env"))

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Spotify API Keys
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

# COLOURS
spotifyGreen = '#1dda63'
bg_color_cas = "#9bf0e1"
grey = "#979797"
lightgrey = "#bdbdbd"


# Set page config
st.set_page_config(page_title="Spotify Big Data Project", 
                #page_icon=":musical_note:", 
                layout="wide")
title = "Be your own DJ with MelodyMap!"
col1, col2 = st.columns([7, 1]) 
with col1:
    st.title(title)
with col2:
    st.image('app/images/logo3.png', width=100)

st.markdown("##")
st.subheader("💚 Create your own playlist based on your mood!")

# GPT-based recommendation engine
#@st.cache(suppress_st_warning=True, show_spinner=False)
def get_completion(messages, model="gpt-3.5-turbo", temperature=0.7):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    content = response['choices'][0]['message']['content']
    return content

def run_model(system_message, user_message):
    messages = [
        {'role': 'system',
            'content': system_message},
        {'role': 'user', 
            'content': user_message}
    ]
    response = get_completion(messages)
    return response

system_message = "As a Spotify playlist recommender, \
    your task is to provide song recommendations based on users' description of their current mood.\
    You should aim to suggest a maximum of 10 songs that align with their request.\
    Your tone is fun, compassion and friendly. Your goal is to make the user feel understood and happy.\
    Your response should end with a fun joke about music."

user_message = st.text_input("How's your mood today?")

if 'last_input' not in st.session_state:
    st.session_state['last_input'] = None
if 'response' not in st.session_state:
    st.session_state['response'] = None

if st.button("Send") or (st.session_state['last_input'] != user_message):
    st.session_state['last_input'] = user_message
    st.session_state['response'] = run_model(system_message, user_message)

if st.session_state['response'] is not None:
    st.write(st.session_state['response'])

#if st.button("Send"):
#    response = run_model(system_message, user_message)
    # Initialization
    #if 'key' not in st.session_state:
    #    st.session_state['key'] = response
    #st.write(st.session_state.key)
#    st.write(response)
#@st.cache(allow_output_mutation=True)
# Song recommendations based on genre and audio features
@st.cache_data()
def load_data():
    df = pd.read_csv('app/data/SpotGenTrack/filtered_track_df.csv')
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
    n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
    uris = genre_data.iloc[n_neighbors]["uri"].tolist()
    audios = genre_data.iloc[n_neighbors][audio_feats].to_numpy()
    return uris, audios

### Search for a song ###
def search_song(song_name):
    """
    Function to search for a song on Spotify
    """
    results = sp.search(q=song_name, limit=1) # limit set to 1 to return only top result
    if results['tracks']['items'] == []:
        return "Song not found."
    
    track = results['tracks']['items'][0]
    
    song_info = {
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'release_date': track['album']['release_date'],
        'popularity': track['popularity'],
        'uri': track['uri'].split(':')[2],
        'audio_features': sp.audio_features(track['uri'])[0]
    }
    
    return song_info

# Use the sidebar method for the input and button
song_name = st.sidebar.text_input("Enter a Song Name:", value='Nellie')

song_info = search_song(song_name)

if song_info == "Song not found.":
    st.sidebar.write(song_info)
else:
    st.sidebar.write("Song Name:", song_info['name'])
    st.sidebar.write("Artist:", song_info['artist'])
    st.sidebar.write("Release Date:", song_info['release_date'])

    # Create the Spotify embed in the sidebar
    st.sidebar.markdown(
        f'<iframe src="https://open.spotify.com/embed/track/{song_info["uri"]}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
        unsafe_allow_html=True,
    )

# Song Recommendation
st.markdown("##")
st.subheader("💚 Create your own playlist by choosing your favourite genre and features!")
with st.container():
    col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
    with col3:
        st.markdown("***Choose your genre:***")
        genre = st.radio(
            "Select your genre:",
            genre_names, index=genre_names.index("Pop"))
    with col1:
        st.markdown("***Choose features to customize:***")
        start_year, end_year = st.slider(
            'Select the year range',
            1990, 2023, (2015, 2023))
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
        liveness = st.slider(
            'Liveness', 0.0, 1.0, 0.5)
        loudness = st.slider(
            'Loudness', -60.0, 0.0, -12.0)  # Note: loudness is typically in the range from -60 to 0 dB
        speechiness = st.slider(
            'Speechiness', 0.0, 1.0, 0.5)

tracks_per_page = 6
test_feat = [acousticness, danceability, energy, instrumentalness, liveness, loudness, speechiness, valence, tempo]
uris, audios = n_neighbors_uri_audio(genre, start_year, end_year, test_feat)
tracks = []
for uri in uris:
    track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
    tracks.append(track)

if 'previous_inputs' not in st.session_state:
    st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat
current_inputs = [genre, start_year, end_year] + test_feat
if current_inputs != st.session_state['previous_inputs']:
    if 'start_track_i' in st.session_state:
        st.session_state['start_track_i'] = 0
    st.session_state['previous_inputs'] = current_inputs
if 'start_track_i' not in st.session_state:
    st.session_state['start_track_i'] = 0
    

with st.container():
    col1, col2, col3 = st.columns([2,1,2])
    if st.button("Recommend More Songs"):
        if st.session_state['start_track_i'] < len(tracks):
            st.session_state['start_track_i'] += tracks_per_page
    current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    if st.session_state['start_track_i'] < len(tracks):
        for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
            if i%2==0:
                with col1:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("See more details"):
                        df = pd.DataFrame(dict(
                        r=audio[:5],
                        theta=audio_feats[:5]))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=400, width=340)
                        st.plotly_chart(fig)
            else:
                with col3:
                    components.html(
                        track,
                        height=400,
                    )
                    with st.expander("See more details"):
                        df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_feats[:5]))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=400, width=340)
                        st.plotly_chart(fig)
    else:
        st.write("No songs left to recommend")
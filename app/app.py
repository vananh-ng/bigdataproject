import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from dotenv import load_dotenv
import os
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import pandas as pd

# COLOURS
spotifyGreen = '#1dda63'
bg_color_cas = "#9bf0e1"
grey = "#979797"
lightgrey = "#bdbdbd"


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

st.set_page_config(page_title="MelodyMap", page_icon=":musical_note:", layout="wide")

#@st.cache(allow_output_mutation=True)
@st.cache_data()
def load_data():
    df =  pd.read_csv("../app/data/SpotGentrack/Data_Sources/filtered_track_df.csv")
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
            1990, 2023, (2015, 2023)
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
        
# MOOD PLAYLIST GENERATOR

def get_rec_df(rec_songs_idx):
    top10_df = df[df.index.isin(rec_songs_idx)]
    uri_list = top10_df.URI.values
    album_art_list = []
    for uri in uri_list:
        song = sp.track(uri)
        album_art = song['album']['images'][0]['url']
        album_art_list.append(album_art)
        
    recs_df = top10_df.copy()
    recs_df['Album Cover Art'] = album_art_list
    
    return recs_df

def getMoodPlaylist(chosen_mood):
    
    if chosen_mood == "Trending songs":
        rec_songs_idx = list(df.sort_values(by = ['Popularity'], ascending = False).index)[0:10]
        
    elif chosen_mood == "Dance party":
        rec_songs_idx = list(df.sort_values(by = ['Danceability'], ascending = False).index)[0:10]
        
    elif chosen_mood == "Monday blues":
        rec_songs_idx = list(df.sort_values(by = ['Valence'], ascending = True).index)[0:10]
        
    elif chosen_mood == "Energizing":
        rec_songs_idx = list(df.sort_values(by = ['Energy'], ascending = False).index)[0:10]
        
    elif chosen_mood == "Positive vibes":
        rec_songs_idx = list(df.sort_values(by = ['Valence'], ascending = False).index)[0:10]
        
    mood_df = get_rec_df(rec_songs_idx = rec_songs_idx)
    
    return mood_df

# MOOD PLAYLIST DISPLAY IN STREAMLIT

moods = ["Trending songs", "Dance party", "Monday blues", "Energizing", "Positive vibes"]

st.markdown("##")
st.markdown("***Choose your mood:***")
chosen_mood = st.selectbox("", moods)

rec_df = getMoodPlaylist(chosen_mood)

# Here, we display the mood playlist
st.markdown("### Playlist for the mood: " + chosen_mood)
for idx, row in rec_df.iterrows():
    st.write("Song: ", row['Song Name'])
    st.write("Artist: ", row['Artist Name(s)'])
    st.image(row['Album Cover Art'])
    components.html("""<iframe src="https://open.spotify.com/embed/track/{}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(row['URI']), height=80)

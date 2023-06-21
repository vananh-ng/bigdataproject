import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import streamlit as st
from dotenv import load_dotenv
import os
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import base64
import json
import requests

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
def melody_map():
    def load_data():
        df =  pd.read_csv("app/data/SpotGenTrack/Data_Sources/filtered_track_df.csv")
        df['genres'] = df['genres'].apply(lambda x: x.replace("'", "").replace("[", "").replace("]", "").split(", "))
        exploded_track_df = df.explode('genres')
        return exploded_track_df

    genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Pop', 'Pop Dance', 'Pop Rap', 'Rap', 'Tropical House']
    audio_feats = ["acousticness", "danceability", "energy", "instrumentalness", "liveness", "loudness", "speechiness", "tempo", "valence"]

    exploded_track_df = load_data()

    # knn model
    def n_neighbors_uri_audio(genre, test_feat):
        genre = genre.lower()
        genre_data = exploded_track_df[(exploded_track_df["genres"]==genre)]
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
    song_name = st.sidebar.text_input("Enter a Song Name:", value='Viva La Vida')

    song_info = search_song(song_name)

    if song_info == "Song not found.":
        st.sidebar.write(song_info)
    else:
        st.sidebar.write("Song Name:", song_info['name'])
        st.sidebar.write("Artist:", song_info['artist'])
        st.sidebar.write("Album:", song_info['album'])
        st.sidebar.write("Release Date:", song_info['release_date'])
        st.sidebar.write("Popularity (0-100):", song_info['popularity'])

        # Create the Spotify embed in the sidebar
        st.sidebar.markdown(
            f'<iframe src="https://open.spotify.com/embed/track/{song_info["uri"]}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>',
            unsafe_allow_html=True,
        )

    # Song Recommendation
    title = "Be your own DJ with MelodyMap!"
    st.title(title)
    st.write("Create your own playlist by choosing your favourite genre and features!")
    st.markdown("##")
    with st.container():
        col1, col2,col3,col4 = st.columns((2,0.5,0.5,0.5))
        with col3:
            st.markdown("***Choose your genre:***")
            genre = st.radio(
                "Select your genre:",
                genre_names, index=genre_names.index("Pop"))
        with col1:
            st.markdown("***Choose features to customize:***")
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
    uris, audios = n_neighbors_uri_audio(genre, test_feat)
    tracks = []
    for uri in uris:
        track = """<iframe src="https://open.spotify.com/embed/track/{}" width="260" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>""".format(uri)
        tracks.append(track)

    if 'previous_inputs' not in st.session_state:
        st.session_state['previous_inputs'] = [genre] + test_feat
    current_inputs = [genre] + test_feat
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
    pass

def new_releases():
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

    #query= {what I want to get}&type= artist, track, playlist, album, artist, playlist, track, show, episode, audiobook.&limit=1 (first artist that pops up, most popular artist)

    # Get new releases
    def get_new_releases(country):
        # Find the country code for the given country name
        row = df_countries[df_countries['country'] == country]
        country_code = row.iloc[0]['country_code']
        url= f"https://api.spotify.com/v1/browse/new-releases?country={country_code}&limit=1"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)['albums']['items'][0]['name']
        return json_result
    token = get_token()

    # Get artist new releases
    def get_artist_new_releases(country):
        # Find the country code for the given country name
        row = df_countries[df_countries['country'] == country]
        country_code = row.iloc[0]['country_code']
        url= f"https://api.spotify.com/v1/browse/new-releases?country={country_code}&limit=1"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)['albums']['items'][0]['artists'][0]['name']
        return json_result


    # Read country data
    df_countries= pd.read_excel('app/data/country-available-final.xlsx')
    df_countries.iloc[115,4]='NA' #Modify for Namibia: it detects NaN instead of NA country code

    # Get new releases per country
    df_countries['new_releases']= [get_new_releases(df_countries.loc[index,'country']) for index in range(len(df_countries))]

    # Get new release artist
    df_countries['artist']= [get_artist_new_releases(df_countries.loc[index,'country']) for index in range(len(df_countries))]

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
        )
    )

    st.title('New releases')
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

    country= st.selectbox(
        'Select a country to see the latest album and its tracks', (df_countries['country']))
    selected_tracks= tracks_from_album(country)
    selected_album= get_new_releases(country)
    selected_artist= get_artist_new_releases(country)
    st.write(f"The latest Album in {country} is {selected_album} by {selected_artist}")
    st.write('Are you curious about its tracks? Check them out!🎧')
    st.dataframe(selected_tracks, hide_index=True)      

# Add a radio button in the sidebar for navigation
pages = st.sidebar.radio('App Navigation', ['Melody Map', 'New Releases'])

# Display the selected page with the radio button
if pages == 'Melody Map':
    melody_map()
elif pages == 'New Releases':
    new_releases()
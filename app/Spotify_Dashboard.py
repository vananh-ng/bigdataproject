# use logging for debugging, error logging, etc.
# could pass the use_container_width=True to st.plotly_chart to make it get the size of the column containing the plot.
import pandas as pd
import pprint as pp
import numpy as np
import requests
from requests import post, get
import base64
import urllib
import os
import json
from dotenv import load_dotenv
import pickle
import streamlit as st
import plotly.express as px
import ast
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Spotify Big Data Project",
    #page_icon="✅",
    layout="wide",
)

df = pd.read_pickle('app/data/album_and_artists.pkl')


load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# API Access
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

token= get_token()

# Function to construct the header to send a request
def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)
    return(json_result)



def main():
    col1, col2 = st.columns([7, 1])  # This will unpack the columns into col1 and col2
    with col1:
        st.image('app/images/melodymap.png', use_column_width=True)
    st.header("Current Top Artists Worldwide")
    top_artists = df.groupby('artists_name')['followers'].sum().sort_values(ascending=False).head(10)

    # Convert top_artists to dictionary and sort it
    top_artists_dict = dict(top_artists)
    top_artists_dict = dict(sorted(top_artists_dict.items(), key=lambda item: item[1], reverse=True))

    # Create two rows of columns
    row1 = st.columns(5)
    row2 = st.columns(5)

    i = 0
    for artist_name, followers_count in top_artists_dict.items():
        result = search_for_artist(token, artist_name)

        # Get the artist data from the API result
        artist_data = result['artists']['items'][0]

        # Get the URL of the second image)
        image_url = artist_data['images'][1]['url']

        # Display the artist's name, follower count, and image
        # In the first five columns (i.e., the first row)
        if i < 5:
            with row1[i]:
                st.subheader(artist_name)
                st.image(image_url)
                formatted_count = "{:,.0f}".format(followers_count)
                st.write(f"Followers: {formatted_count}")
        # In the second five columns (i.e., the second row)
        else:
            with row2[i-5]:
                st.subheader(artist_name)
                st.image(image_url)
                formatted_count = "{:,.0f}".format(followers_count)
                st.write(f"Followers: {formatted_count}")
        i += 1

    # Convert 'genres' from string representation of list to actual list
    df['genres'] = df['genres'].apply(ast.literal_eval)

    # Explode 'genres' list into separate rows
    genres_popularity_df = df.explode('genres')

   # Create a color mapping
    unique_genres = pd.unique(genres_popularity_df['genres'])
    num_genres = len(unique_genres)

    # Generate a color palette
    color_palette = sns.husl_palette(num_genres)

    # Map each genre to a color
    genre_to_color = {genre: matplotlib.colors.rgb2hex(color) for genre, color in zip(unique_genres, color_palette)}
    
    # Create two columns
    col3, col4 = st.columns(2)

    with col3:
        st.header('Genres Popularity')
        # Count the number of albums for each genre and select top 10
        genre_popularity = genres_popularity_df['genres'].value_counts().head(10).reset_index()
        genre_popularity.columns = ['genres', 'count']
        genre_popularity['color'] = genre_popularity['genres'].map(genre_to_color)
        fig = px.bar(genre_popularity, x='genres', y='count', color='genres',
                    labels={'genres':'', 'count':'Album Count'}, title='Top 10 Genres by Album Count',
                    color_discrete_sequence=genre_popularity['color'])
        fig.update_xaxes(visible=False, showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.header('Top Albums')
        # remove 'Spotify Singles' from df column 'album_name'
        df_tmp = df[df['name'] != 'Spotify Singles']
        top_albums = df_tmp.groupby('name')['followers'].sum().nlargest(10)
        fig = px.bar(top_albums, x=top_albums.index, y=top_albums.values, labels={'x':'Albums', 'y':'Followers'}, title='Top 10 Albums by Followers')
        st.plotly_chart(fig, use_container_width=True)  

    # Create two more columns for the next section
    col5, col6 = st.columns(2)

    with col5:
        st.header('Artists per Genre')
        # Count the number of unique artists for each genre and select top 10
        artists_per_genre = genres_popularity_df.groupby('genres')['artists_name'].nunique().sort_values(ascending=False).head(10).reset_index()
        artists_per_genre.columns = ['genres', 'count']
        artists_per_genre['color'] = artists_per_genre['genres'].map(genre_to_color)
        fig = px.bar(artists_per_genre, x='genres', y='count', color='genres',
                    labels={'genres':'', 'count':'Artist Count'}, title='Top 10 Genres by Artist Count',
                    color_discrete_sequence=artists_per_genre['color'])
        fig.update_xaxes(visible=False, showticklabels=False)
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.header('Distribution of Album Types')
        fig = px.pie(df, names='album_type', title='Distribution of Album Types')
        st.plotly_chart(fig, use_container_width=True)

    #with col6:
    #    st.header('Correlation Matrix')
    #    corr_matrix = df[['total_tracks', 'followers', 'release_year']].corr()
    #    fig = px.imshow(corr_matrix, labels={'x':'New X Label', 'y':'New Y Label', 'color':'New Color Label'}, title='Correlation Matrix')
    #    st.plotly_chart(fig)

    #st.header('Artists Word Cloud')
    #all_artists = ' '.join(df['artists_name'].values)
    #wordcloud = WordCloud(width = 800, height = 800, 
    #                      background_color ='white', 
    #                      stopwords = None, 
    #                      min_font_size = 10).generate(all_artists) 
    #plt.figure(figsize = (8, 8), facecolor = None) 
    #plt.imshow(wordcloud) 
    #plt.axis("off") 
    #plt.tight_layout(pad = 0) 
    #st.pyplot(plt.gcf())

if __name__ == "__main__":
    main()
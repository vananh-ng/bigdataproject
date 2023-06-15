import pandas as pd
import pickle
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_pickle('app/data/album_and_artists.pkl')

# Create a function to make the genre graph
def top_genres(df):
    genres = df['genres'].value_counts().head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=genres.values, y=genres.index, palette='viridis')
    plt.title('Top Genres')
    plt.xlabel('Count')
    plt.ylabel('Genre')
    st.pyplot(plt.clf())

# Create a function to make the popular artists graph
def popular_artists(df):
    popular_artists = df.sort_values('followers', ascending=False)['artists_name'].head(10)
    plt.figure(figsize=(10,6))
    sns.barplot(x=popular_artists.values, y=popular_artists.index, palette='viridis')
    plt.title('Popular Artists')
    plt.xlabel('Followers')
    plt.ylabel('Artist')
    st.pyplot(plt.clf())

# Create a function to make the artist popularity over time graph
def popularity_over_time(df, artist_name):
    artist_df = df[df['artists_name'] == artist_name]
    plt.figure(figsize=(10,6))
    sns.lineplot(x=artist_df['release_year'], y=artist_df['artist_popularity'], palette='viridis')
    plt.title(f'{artist_name} Popularity Over Time')
    plt.xlabel('Year')
    plt.ylabel('Popularity')
    st.pyplot(plt.clf())

# Create a function to make the album types graph
def album_types(df):
    album_types = df['album_type'].value_counts()
    plt.figure(figsize=(10,6))
    plt.pie(album_types.values, labels=album_types.index, autopct='%1.1f%%', startangle=140)
    plt.title('Album Types')
    st.pyplot(plt.clf())

# Layout of Streamlit app
st.title('Spotify Dashboard')
if st.checkbox('Show Top Genres'):
    top_genres(df)

if st.checkbox('Show Popular Artists'):
    popular_artists(df)

artist_name = st.text_input('Enter an artist name to see their popularity over time:')
if artist_name:
    popularity_over_time(df, artist_name)

if st.checkbox('Show Album Types'):
    album_types(df)
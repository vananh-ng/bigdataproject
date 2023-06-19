# use logging for debugging, error logging, etc.
# could pass the use_container_width=True to st.plotly_chart to make it get the size of the column containing the plot.

import streamlit as st
import pandas as pd
import plotly.express as px
import pickle


df = pd.read_pickle('data/album_and_artists.pkl')


def main():
    st.title("Spotify Data Dashboard")

    # Create two columns
    col1, col2 = st.columns(2)

    # Top Genres
    with col1:
        st.header("Top Genres")
        top_genres = df['genres'].value_counts().head(10)
        fig1 = px.bar(top_genres, x=top_genres.index, y=top_genres.values, labels={'x':'Genre', 'y':'Count'}, title="Top Genres")
        st.plotly_chart(fig1, use_container_width=True)

    # Popular Artists
    with col1:
        st.header("Popular Artists")
        top_artists = df.groupby('artists_name')['followers'].sum().sort_values(ascending=False).head(10)
        fig2 = px.bar(top_artists, x=top_artists.index, y=top_artists.values, labels={'x':'Artist', 'y':'Followers'}, title="Popular Artists")
        st.plotly_chart(fig2, use_container_width=True)

    # Popularity Over Time
    with col2:
        st.header("Popularity Over Time")
        artist_name = st.text_input('Enter the name of an artist:', 'Becky G')
        artist_data = df[df['artists_name'] == artist_name]
        if not artist_data.empty:
            fig3 = px.line(artist_data, x='release_year', y='artist_popularity', title=f"Popularity of {artist_name} Over Time")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write(f"No data for artist: {artist_name}")

    # Album Types
    with col2:
        st.header("Album Types")
        album_types = df['album_type'].value_counts()
        fig4 = px.pie(album_types, names=album_types.index, values=album_types.values, title="Album Types Distribution")
        st.plotly_chart(fig4, use_container_width=True)

if __name__ == "__main__":
    main()
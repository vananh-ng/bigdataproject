# use logging for debugging, error logging, etc.
# could pass the use_container_width=True to st.plotly_chart to make it get the size of the column containing the plot.

import streamlit as st
import pandas as pd
import plotly.express as px
import pickle

st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    #page_icon="✅",
    layout="wide",
)

df = pd.read_pickle('data/album_and_artists.pkl')


def main():
    st.title('Spotify Dashboard')

    # Create three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header("Popular Artists")
        top_artists = df.groupby('artists_name')['followers'].sum().sort_values(ascending=False).head(10)
        fig2 = px.bar(top_artists, x=top_artists.index, y=top_artists.values, labels={'x':'Artists', 'y':'Followers'}, title="Popular Artists")
        st.plotly_chart(fig2)

    with col2:
        st.header('Genres Popularity')
        # Explode 'genres' list into separate rows
        genres_popularity_df = df.explode('genres')
        # Count the number of albums for each genre and select top 10
        genre_popularity = genres_popularity_df['genres'].value_counts().head(10)
        fig = px.bar(genre_popularity, x=genre_popularity.index, y=genre_popularity.values, labels={'x':'Genres', 'y':'Album Count'}, title='Top 10 Genres by Album Count')
        st.plotly_chart(fig)

    with col3:
        st.header('Artists per Genre')
        # Count the number of unique artists for each genre and select top 10
        artists_per_genre = genres_popularity_df.groupby('genres')['artists_name'].nunique().sort_values(ascending=False).head(10)
        fig = px.bar(artists_per_genre, x=artists_per_genre.index, y='artists_name', labels={'x':'Genres', 'y':'Artist Count'}, title='Top 10 Genres by Artist Count')
        st.plotly_chart(fig)

    # Create three more columns for the next section
    col4, col5, col6 = st.columns(3)

    with col4:
        st.header('Top Albums by Followers')
        top_albums = df.groupby('name')['followers'].sum().nlargest(10)
        fig = px.bar(top_albums, x=top_albums.index, y=top_albums.values, labels={'x':'Albums', 'y':'Followers'}, title='Top Albums by Followers')
        st.plotly_chart(fig)

    with col5:
        st.header('Distribution of Album Types')
        fig = px.histogram(df, x='album_type', labels={'x':'Album Type', 'y':'Count'}, title='Distribution of Album Types')
        st.plotly_chart(fig)

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

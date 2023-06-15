import pandas as pd
import ast

# Read the CSV files into a DataFrame
df_album = pd.read_csv('app/data/albums_data.csv')
df_artist = pd.read_csv('app/data/artist_data.csv')
print(df_album.shape)
print(df_artist.shape)

# cleaning the data
df_album = df_album.drop_duplicates()
df_artist = df_artist.drop_duplicates()
df_album = df_album.dropna()
df_artist = df_artist.dropna()

# drop the rows where the genres column is an empty list
#df_artist = df_artist[df_artist['genres'].apply(lambda x: x != [])]
df_artist = df_artist.dropna(subset=['genres'])
df_artist = df_artist[df_artist['genres'].apply(lambda x: ast.literal_eval(x) != [])]

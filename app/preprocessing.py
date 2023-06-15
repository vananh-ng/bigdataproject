import pandas as pd
import ast
import pickle

# Read the CSV files into a DataFrame
df_album = pd.read_csv('app/data/albums_data.csv')
df_artist = pd.read_csv('app/data/artist_data.csv')
#print(df_album.shape)
#print(df_artist.shape)

# cleaning the data
df_album = df_album.drop_duplicates()
df_artist = df_artist.drop_duplicates()
df_album = df_album.dropna()
df_artist = df_artist.dropna()

# drop the rows where the genres and followers column is an empty list
df_artist = df_artist.dropna(subset=['genres'])
df_artist = df_artist[df_artist['genres'].apply(lambda x: ast.literal_eval(x) != [])]
df_artist = df_artist.dropna(subset=['followers'])

def extract_year(date_str):
    if "/" in date_str:
        return date_str.split("/")[2] # if format is "12/1/1981", year is the 3rd part
    elif "-" in date_str:
        return date_str.split("-")[0] # if format is "1981-08", year is the 1st part
    else:
        return date_str # return as is

# convert the release_date column to year only
df_album['release_date'] = df_album['release_date'].apply(extract_year)
df_album['release_date'] = df_album['release_date'].astype(int)

# drop unusable columns
df_album = df_album.drop(['Unnamed: 0', 'available_markets', 'type', 'uri', 'external_urls', 'href', 'images', 'track_name_prev', 'track_id', 'release_date_precision'], axis=1)
df_artist = df_artist.drop(['Unnamed: 0', 'type', 'track_name_prev', 'track_id'], axis=1)

# merge the two dataframes
df_merge = pd.merge(df_album, df_artist, left_on='artist_id', right_on='artists_id', how='inner')
df_merge = df_merge.drop(['artists_id'], axis=1)
df_merge = df_merge.rename(columns={'id': 'album_id', 'release_date': 'release_year'})

# save the merged dataframe
with open('app/data/album_and_artists.pkl', 'wb') as file:
    pickle.dump(df_merge, file)
    print("Dataframe saved to pickle file.")
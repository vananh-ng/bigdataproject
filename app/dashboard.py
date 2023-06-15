import pandas as pd
import pickle

df = pd.read_pickle('app/data/album_and_artists.pkl')
print(df.shape)
import requests
from requests import post, get
import base64
import urllib
import os
import json
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px
import pickle
import schedule
import time

'''This code is to update the new_releases dataframe with the data from the API:
    It's scheudled to run every 3 days at 00:00 and replace the existing dataframe'''

# Spotify Developer Dashboard details
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print(type(client_secret))

# We first request a token to the Spotify Accounts Service, which will be used later on to access the Spotify Web API
# To get our access token, we need to pass our client ID, client Secret and grant_type

# Get Spotify token   
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

token = get_token()

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
df_countries= pd.read_excel(r'C:\Users\sofia\OneDrive\Documentos\GitHub\bigdataproject\app\data\country-available-final.xlsx')
df_countries.iloc[115,4]='NA' #Modify for Namibia: it detects NaN instead of NA country code

# Get the new releases per country
#df_countries['new_releases'] = [get_new_releases(df_countries.loc[index, 'country']) for index in range(len(df_countries))]

# Get the new release artist
#df_countries['artist'] = [get_artist_new_releases(df_countries.loc[index, 'country']) for index in range(len(df_countries))]


# Function to update new releases in the dataframe
def update_new_releases(pickle_file_path):
    # Load the new_releases
    with open(pickle_file_path, 'rb') as file:
        df_countries = pickle.load(file)

    #Modify for Namibia: it detects NaN instead of NA country code
    df_countries.iloc[115,4]='NA' 
        
    # Get the new releases per country
    df_countries['new_releases'] = [get_new_releases(df_countries.loc[index, 'country']) for index in range(len(df_countries))]

    # Get the new release artist
    df_countries['artist'] = [get_artist_new_releases(df_countries.loc[index, 'country']) for index in range(len(df_countries))]

     # Save the updated dataframe to a temporary pickle file
    temp_pickle_file_path = os.path.splitext(pickle_file_path)[0] + '_temp.pkl'
    with open(temp_pickle_file_path, 'wb') as file:
        pickle.dump(df_countries, file)

    # Replace the original pickle file with the updated one
    os.replace(temp_pickle_file_path, pickle_file_path)
    print("New releases updated successfully!")

pickle_file_path= r"/data/new_releases.pkl"
schedule.every(3).days.at("00:00").do(update_new_releases, pickle_file_path)

while True: # This starts an infinite loop.
    schedule.run_pending() # This line checks if there are any scheduled tasks that are due to run and executes them. If there are no pending tasks, it does nothing.
    time.sleep(1) #After checking for pending tasks, the program pauses for 1 second using the time.sleep() function. This ensures that the loop doesn't consume excessive resources and provides a delay between iterations.
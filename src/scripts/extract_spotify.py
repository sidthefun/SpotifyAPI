import os
import json
import spotipy
import base64
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
import logging
from datetime import datetime
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret():
    

    secret_name = "Test/spotify"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    
    return secret

def lambda_handler(event, context):
   
    ##Extract playlist data
    client_id = None
    client_secret = None
    
    
    credentials = json.loads(get_secret())
    
    cilent_id =credentials['cilent_id']
    client_secret =credentials['client_secret']
    
    
    client_credentials_manager = SpotifyClientCredentials(client_id=cilent_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
     
    

    playlists = sp.user_playlists('spotify')
    playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXcDYGt49X0ozW"
    playlist_URI = playlist_link.split("/")[-1].split("?")[0]
    
    spotify_data = sp.playlist_tracks(playlist_URI)   
    cilent = boto3.client('s3')
    filename = "spotify_raw_" + str(datetime.now()) + ".json"
    
    ## Save data into this folder
    cilent.put_object(
        Bucket="spotifyapidata1",
        Key="Discover_weeklie/raw_data/to_process/" + filename,
        Body=json.dumps(spotify_data)
        )
    
 
    
    
  
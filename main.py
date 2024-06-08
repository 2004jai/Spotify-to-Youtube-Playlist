import requests
import youtubesearchpython
import googleapiclient.discovery as google_api
import google_auth_oauthlib.flow as google_flow

# ----------------------------------------------------------------------------------------------------#

client_id = "e7629aa81dbd4d6492229ea08237e13f"
client_sec = "08fcaddd22bc493ab6ca542265696768"
token = ""

# YOUTUBE API KEY
api_key = "AIzaSyB-VWwgk79AHXWCawom73-zrfP7bvEOTMQ"

# OAuth 2.0 credentials File Path
credentials_file = "6th_sem_Project/client_secret_892118349357-58nv1b84kq3fsk52n86u7if0a6kochbc.apps.googleusercontent.com.json"

# OAuth 2.0 flow
flow = google_flow.InstalledAppFlow.from_client_secrets_file(
    credentials_file, scopes=["https://www.googleapis.com/auth/youtube"]
)
credentials = flow.run_local_server()

# YouTube Data API service
youtube = google_api.build(
    "youtube", "v3", developerKey=api_key, credentials=credentials
)

# ----------------------------------------------------------------------------------------------------#


# retrieves the access token required for authorization to access the Spotify API
def get_token():
    url = "https://accounts.spotify.com/api/token"
    payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_sec}"
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, headers=head, data=payload)

    return response.json()["access_token"]


# retrives music from playlist using Spotify API
def get_music(playlist, token):
    url = f"https://api.spotify.com/v1/playlists/{playlist}"
    headers = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=headers)

    return response.json()["tracks"]["items"]


# search the songs in youtube
def Youtube_video(songs):
    try:
        search = youtubesearchpython.VideosSearch(songs, limit=1)
        results = search.result()["result"]
        if results:
            return "https://www.youtube.com/watch?v=" + results[0]["id"]
        else:
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# creating YOUTUBE playlist
def create_youtube_playlist(title, description):

    playlist_request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
            },
            "status": {"privacyStatus": "private"},
        },
    )
    response = playlist_request.execute()

    return response["id"]


# Adding the video to playlist
def add(youtube, playlist, video_url):
    id = video_url.split("v=")[1]
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist,
                "position": 0,
                "resourceId": {"kind": "youtube#video", "videoId": id},
            }
        },
    )
    response = request.execute()
    print("Video added to the playlist:", response)


def Main():
    token = get_token()
    input_value = input("Enter playlist URL: ")
    playlist_id = input_value.split("playlist/")[1]
    playlist = get_music(playlist_id, token)

    spotify_playlist_info = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}",headers={"Authorization": "Bearer " + token},).json()
    
    youtube_playlist_id = create_youtube_playlist(spotify_playlist_info["name"], spotify_playlist_info["description"])

    for music in playlist:
        query = music["track"]["name"]+music["track"]["artists"][0]["name"]
        video_url = Youtube_video(query)
        if video_url:
            add(youtube, youtube_playlist_id, video_url)
            print(f"{query}: {video_url}")

        else:
            print(f"No video found for {query}")


Main()

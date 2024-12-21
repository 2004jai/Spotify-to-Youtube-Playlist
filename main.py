import os
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ----------------------------------------------------------------------------------------------------#

# Spotify API credentials
client_id = "e7629aa81dbd4d6492229ea08237e13f"
client_sec = "08fcaddd22bc493ab6ca542265696768"

# YouTube API credentials
api_key = "AIzaSyB-VWwgk79AHXWCawom73-zrfP7bvEOTMQ"
credentials_file = "Spotify_to_youtube/client_secret_892118349357-58nv1b84kq3fsk52n86u7if0a6kochbc.apps.googleusercontent.com.json"

# OAuth 2.0 flow
flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file, scopes=["https://www.googleapis.com/auth/youtube"]
)
credentials = flow.run_local_server()
youtube = build("youtube", "v3", credentials=credentials)

# ----------------------------------------------------------------------------------------------------#


# Retrieves the access token for Spotify API
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_sec,
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]


# Retrieves tracks from a Spotify playlist
def get_spotify_tracks(playlist_id, token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tracks = response.json().get("tracks", {}).get("items", [])
    return [
        f"{track['track']['name']} {track['track']['artists'][0]['name']}"
        for track in tracks
    ]


# Searches for a video on YouTube using the official API
def youtube_search_video(query):
    try:
        search_response = youtube.search().list(
            q=query, part="snippet", type="video", maxResults=1
        ).execute()

        items = search_response.get("items", [])
        if items:
            video_id = items[0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
        return None
    except Exception as e:
        print(f"An error occurred while searching YouTube: {e}")
        return None


# Creates a new playlist on YouTube
def create_youtube_playlist(title, description):
    try:
        playlist_request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": "private"},
            },
        )
        response = playlist_request.execute()
        return response["id"]
    except Exception as e:
        print(f"An error occurred while creating the playlist: {e}")
        return None


# Adds a video to a YouTube playlist
def add_video_to_playlist(playlist_id, video_url):
    try:
        video_id = video_url.split("v=")[1]
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        )
        request.execute()
        print(f"Added video {video_url} to playlist {playlist_id}")
    except Exception as e:
        print(f"An error occurred while adding the video to the playlist: {e}")


# Main Function
def main():
    spotify_token = get_spotify_token()
    input_url = input("Enter Spotify playlist URL: ")
    playlist_id = input_url.split("playlist/")[1]

    spotify_tracks = get_spotify_tracks(playlist_id, spotify_token)

    playlist_info = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {spotify_token}"},
    ).json()

    youtube_playlist_id = create_youtube_playlist(
        playlist_info["name"], playlist_info["description"]
    )

    if youtube_playlist_id:
        for track in spotify_tracks:
            video_url = youtube_search_video(track)
            if video_url:
                add_video_to_playlist(youtube_playlist_id, video_url)
            else:
                print(f"Video not found for: {track}")
    else:
        print("Failed to create YouTube playlist.")


if __name__ == "__main__":
    main()

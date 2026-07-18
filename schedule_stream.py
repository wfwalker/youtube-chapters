import os
import sys
import argparse
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes required to manage YouTube Live events
SCOPES = ['https://www.googleapis.com/auth/youtube']

def get_authenticated_service(credentials_path="client_secrets.json", token_path="token.json"):
    """Authenticates the user and returns an authorized YouTube API service client."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired Google OAuth credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"\nError: Missing credentials file '{credentials_path}'.", file=sys.stderr)
                print("To run this script, please follow the GCP Console setup in the design document:", file=sys.stderr)
                print("1. Enable YouTube Data API v3 in Google Cloud Console.", file=sys.stderr)
                print("2. Create OAuth Client ID credentials (Desktop App type).", file=sys.stderr)
                print(f"3. Download the JSON client secret, rename it to '{credentials_path}' and save it in this directory.", file=sys.stderr)
                sys.exit(1)
            print("Opening browser for Google Authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def get_or_create_stream(youtube):
    """Finds your default live stream key, or creates one if none exists."""
    response = youtube.liveStreams().list(
        part="id,snippet,cdn",
        mine=True
    ).execute()
    
    streams = response.get("items", [])
    if streams:
        # Re-use the first available stream configuration
        print(f"Found active stream configuration: {streams[0]['id']}")
        return streams[0]["id"]
        
    # If no stream keys exist, create one (1080p RTMP ingestion)
    print("No stream configuration found. Creating new ingestion stream...")
    body = {
        "snippet": {
            "title": "FJHH Default Stream Ingest"
        },
        "cdn": {
            "frameRate": "30fps",
            "ingestionType": "rtmp",
            "resolution": "1080p"
        }
    }
    new_stream = youtube.liveStreams().insert(
        part="snippet,cdn",
        body=body
    ).execute()
    return new_stream["id"]

def schedule_broadcast(youtube, title, description, start_time_iso, privacy="unlisted"):
    """Inserts a scheduled YouTube Live Broadcast event."""
    print(f"Scheduling live broadcast: '{title}' for {start_time_iso} ({privacy})...")
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "scheduledStartTime": start_time_iso
        },
        "status": {
            "privacyStatus": privacy
        },
        "contentDetails": {
            "enableAutoStart": True, # Automatically go live when stream ingestion starts
            "enableAutoStop": True,  # Automatically end when stream ingestion stops
            "monitorStream": {
                "enableMonitorStream": False # Minimizes latency
            }
        }
    }
    broadcast = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body=body
    ).execute()
    return broadcast["id"]

def upload_thumbnail(youtube, video_id, thumbnail_path):
    """Uploads the JPEG cover slide to the scheduled YouTube video page."""
    if not os.path.exists(thumbnail_path):
        print(f"Warning: Thumbnail file not found: {thumbnail_path}. Skipping upload.")
        return
        
    print(f"Uploading cover slide '{thumbnail_path}' to broadcast ID {video_id}...")
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(thumbnail_path, mimetype='image/jpeg')
    ).execute()

def main():
    parser = argparse.ArgumentParser(description="Schedule a YouTube Live Stream and upload its cover slide.")
    parser.add_argument("--show", required=True, help="Episode number (e.g. 305).")
    parser.add_argument("--date", required=True, help="Date of show in YYYY-MM-DD format (e.g. 2026-07-24).")
    parser.add_argument("--thumbnail", required=True, help="Path to the cover slide JPEG image.")
    parser.add_argument("--description", default="", help="Description text for the stream.")
    parser.add_argument("--headline", help="Custom headline text to prepend to the stream description.")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted", help="Privacy status (default: unlisted).")
    
    args = parser.parse_args()
    
    # Target 5:00 PM Pacific Time on the show date
    # Format ISO 8601 offset representation: 'YYYY-MM-DDT17:00:00-07:00' (or -08:00 depending on DST)
    start_time_iso = f"{args.date}T17:00:00-07:00"
    
    title = f"Friday Jazz Happy Hour #{args.show}"
    
    # Build description body
    body_text = args.description or f"Welcome to Friday Jazz Happy Hour #{args.show}!\nLive streaming every Friday at 5:00 PM Pacific."
    if args.headline:
        description_text = f"{args.headline}\n\n{body_text}"
    else:
        description_text = body_text
        
    # Append the three standard footer links
    footer = (
        "\n\n"
        "▶ subscribe to our mailing list: https://fridayjazzhappyhour.com/mailinglist\n"
        "▶ how i make the show: https://fridayjazzhappyhour.com/about\n"
        "▶ original music: https://billwalker.bandcamp.com/"
    )
    description_text += footer
    
    # 1. Auth with credentials
    youtube = get_authenticated_service()
    
    # 2. Schedule Event Page
    broadcast_id = schedule_broadcast(youtube, title, description_text, start_time_iso, args.privacy)
    
    # 3. Get RTMP Stream configuration
    stream_id = get_or_create_stream(youtube)
    
    # 4. Bind Broadcast to Ingestion Stream
    print("Binding broadcast to ingestion settings...")
    youtube.liveBroadcasts().bind(
        id=broadcast_id,
        part="id,contentDetails",
        streamId=stream_id
    ).execute()
    
    # 5. Upload Custom Slide
    upload_thumbnail(youtube, broadcast_id, args.thumbnail)
    
    watch_url = f"https://youtu.be/{broadcast_id}"
    print("\n" + "="*40)
    print(" STREAM SUCCESSFULLY SCHEDULED!")
    print("="*40)
    print(f"Watch URL: {watch_url}")
    print("="*40)

if __name__ == "__main__":
    main()

import os
import instaloader
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Step 1: Install required libraries
# pip install instaloader google-auth google-auth-oauthlib google-api-python-client

# Step 2: Authenticate with YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret.json"

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build("youtube", "v3", credentials=credentials)

# Step 3: Download Instagram Video
def download_instagram_video(url):
    loader = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
    target_dir = "downloads"
    filename = f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S_UTC')}.mp4"
    loader.download_post(post, target=target_dir)
    return os.path.join(target_dir, f"{post.date_utc.strftime('%Y-%m-%d_%H-%M-%S_UTC')}.mp4")

# Step 4: Upload Video to YouTube
def upload_video_to_youtube(video_file, title, description, category="22", tags=None):
    youtube = get_authenticated_service()
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()
    return response

if __name__ == "__main__":
    instagram_url = input("Enter Instagram URL: ")
    video_file = download_instagram_video(instagram_url)
    text_file = video_file.replace(".mp4", ".txt")
    title = "Your Video Title"
    with open(text_file, "r") as file:
        description = file.read()
        tags = [tag.strip("#") for tag in description.split() if tag.startswith("#")]

    response = upload_video_to_youtube(video_file, title, description, tags=tags)
    print(f"Video uploaded: https://www.youtube.com/watch?v={response['id']}")

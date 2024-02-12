from utils.upload_video import upload_video
from utils.RedditBot import RedditBot
def youtube(title2,description2,tags2,privacy2):
    redditbot = RedditBot()
    video_data = {
                "file": "static/video.mp4",
                "title": title2,
                "description": description2,
                "keywords":tags2,
                "privacyStatus":privacy2
        }

    print(f"Uploading the video, {video_data["title"]}")
    print("Posting Video now...")
    try:
        upload_video(video_data)
    except Exception as err:
        print(err,"\n\n\n\n\n\n\n\nComputational power error")

    print("done!")
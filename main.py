from RedditDownloader import RedditBot
from utils import SocialMedias, get_credentials

reddit = RedditBot(get_credentials(), log=True)
data = reddit.save_images_from_subreddit(amount=1)
video_path = reddit.create_video(data)

ytb_data = {
    "file": video_path,
    "title": "#shorts r/cursedcomments",
    "description": "why tho",
    "keywords": "meme,memes,laugh,internet,short,reddit",
    "privacyStatus": "unlisted"
}

reddit.publish_on(SocialMedias.YouTube, ytb_data)

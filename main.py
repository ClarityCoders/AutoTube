from utils.CreateMovie import CreateMovie, GetDaySuffix
from utils.RedditBot import RedditBot
from utils.upload_video import update_video
from datetime import date
import time

#Create Reddit Data Bot
redditbot = RedditBot()

# Leave if you want to run it 24/7
while True:

    # Gets our new posts pass if image related subs. Default is memes
    posts = redditbot.get_posts("gifs")

    # Create folder if it doesn't exist
    redditbot.create_data_folder()

    for post in posts:
        redditbot.save_image(post)

    day = date.today().strftime("%d")
    day = str(int(day)) + GetDaySuffix(int(day))

    CreateMovie.CreateMP4(redditbot.post_data)
    dt_string = date.today().strftime("%A %B") + f" {day}"

    video_data = {
            "file": "video.mp4",
            "title": f"{redditbot.post_data[0]['title']} - Dankest memes and comments {dt_string}!",
            "description": "#shorts\nGiving you the hottest memes of the day with funny comments!",
            "keywords":"meme,reddit,Dankestmemes",
            "privacyStatus":"public"
    }
    print(video_data["title"])
    print("Posting Video in 5 minutes...")
    time.sleep(60 * 5)
    #update_video(video_data)

    # Sleep until ready to post another video!
    time.sleep(60 * 60 * 24 - 1)
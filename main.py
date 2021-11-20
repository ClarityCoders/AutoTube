from CreateMovie import CreateMovie
from RedditBot import RedditBot
from upload_video import update_video
from datetime import date
import time

def GetDaySuffix(day):
    if day == 1 or day == 21 or day == 31:
        return "st"
    elif day == 2 or day == 22:
        return "nd"
    elif day == 3 or day == 23:
        return "rd"
    else:
        return "th"

#Create data
redditbot = RedditBot()

while True:
    # Make sure to do just this inside loop.
    posts = redditbot.get_posts()

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
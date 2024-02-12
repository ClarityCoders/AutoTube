"""
This is the main loop file for our AutoTube Bot!

Quick notes!
- Currently it's set to try and post a video then sleep for a day.
- You can change the size of the video currently it's set to post shorts.
    * Do this by adding a parameter of scale to the image_save function.
    * scale=(width,height)
"""

from datetime import date
import time
from utils.CreateMovie import CreateMovie
from utils.RedditBot import RedditBot
from p import youtube

def stuff(title,description,tags,privacy,subreddit):
#Create Reddit Data Bot
    redditbot = RedditBot()
   
    # Gets our new posts pass if image related subs. Default is memes
    try:
        posts = redditbot.get_posts(subreddit)
    except:
        post = redditbot.get_posts("woosh")
    # Create folder if it doesn't exist
    redditbot.create_data_folder()

    # Go through posts and find 5 that will work for us.
    for post in posts:
        redditbot.save_image(post)

    """# Wanted a date in my titles so added this helper
    DAY = date.today().strftime("%d")
    DAY = str(int(DAY)) + GetDaySuffix(int(DAY))
    dt_string = date.today().strftime("%A %B") + f" {DAY}" """

    # Create the movie itself!
    CreateMovie.CreateMP4(redditbot.post_data)

    youtube(title,description,tags,privacy)


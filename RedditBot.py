import os
import praw
from dotenv import load_dotenv
from datetime import date
import requests
import json 
from Scalegif import scale_gif

load_dotenv()

class RedditBot():
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv('client_id'),
            client_secret=os.getenv('client_secret'),
            user_agent=os.getenv('user_agent'),
        )
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(dir_path, "data/")
        self.post_data = []
        self.already_posted = []
        if os.path.isfile("posted_already.json"):
            with open("posted_already.json", "r") as file:
                self.already_posted = json.load(file)
                #print(self.already_posted)

    def get_posts(self):
        self.post_data = []
        subreddit = self.reddit.subreddit("memes")
        posts = []
        for submission in subreddit.top("day", limit=20):
            if submission.stickied:
                print("Mod Post")
            else:
                posts.append(submission)

        return posts

    def create_data_folder(self):
        today = date.today()
        dt_string = today.strftime("%m%d%Y")
        data_folder_path = os.path.join(self.data_path, f"{dt_string}/")
        CHECK_FOLDER = os.path.isdir(data_folder_path)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(data_folder_path)

    def save_image(self, submission):
        if "jpg" in submission.url.lower() or "png" in submission.url.lower() or "gif" in submission.url.lower():
            #try:

                # Get all images to ignore
                dt_string = date.today().strftime("%m%d%Y")
                data_folder_path = os.path.join(self.data_path, f"{dt_string}/")
                CHECK_FOLDER = os.path.isdir(data_folder_path)
                if CHECK_FOLDER and len(self.post_data) < 5 and not submission.over_18 and submission.id not in self.already_posted:
                    image_path = f"{data_folder_path}Post-{submission.id}{submission.url.lower()[-4:]}"

                    # Get the image and write the path
                    r = requests.get(submission.url.lower())  
                    with open(image_path, 'wb') as f:
                        f.write(r.content)

                    # Could do transforms on images like resize!
                    #image = cv2.resize(image,(720,1280))
                    scale_gif(image_path, (720,1280))
                    
                    #cv2.imwrite(f"{image_path}", image)
                    submission.comment_sort = 'best'

                    # Get best comment.
                    for top_level_comment in submission.comments:
                        # Here you can fetch data off the comment.
                        # For the sake of example, we're just printing the comment body.
                        best_comment = top_level_comment
                        if len(best_comment.body) <= 140 and "http" not in best_comment.body:
                            break

                    best_comment.reply_sort = "top"
                    best_comment.refresh()
                    replies = best_comment.replies

                    for top_level_comment in replies:
                        # Here you can fetch data off the comment.
                        # For the sake of example, we're just printing the comment body.
                        best_reply = top_level_comment
                        if len(best_reply.body) <= 140 and "http" not in best_reply.body:
                            break

                    data_file = {
                        "image_path": image_path,
                        'id':submission.id,
                        "title": submission.title,
                        "score": submission.score,
                        "18": submission.over_18,
                        "Best_comment": best_comment.body,
                        "best_reply": best_reply.body
                    }
                    
                    self.post_data.append(data_file)
                    self.already_posted.append(submission.id)
                    with open(f"{data_folder_path}{submission.id}.json", "w") as outfile:
                        json.dump(data_file, outfile) 
                    with open("posted_already.json", "w") as outfile:
                        json.dump(self.already_posted, outfile) 
                else:
                    return None
                    
            #except Exception as e:
            #    print(f"Image failed. {submission.url.lower()}")
            #    print(e)

if __name__ == "__main__":
    redditbot = RedditBot()
    posts = redditbot.get_posts()

    # Create folder if it doesn't exist
    redditbot.create_data_folder()

    for post in posts:
        #print(post.title, post.url, post.permalink)
        redditbot.save_image(post)
    
    #redditbot.create_movie()
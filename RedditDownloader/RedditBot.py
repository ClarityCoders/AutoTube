import json
import os
from datetime import date
from typing import List, Tuple

import praw
import requests
from environs import Env

from MovieMaker import CreateMovie
from Publishers import YtbPublisher
from RedditDownloaderExceptions import MissingCredentialsException, IncorrectCredentialsException
from .ScaleImages import Scale
from prawcore import ResponseException


class RedditBot(Scale, CreateMovie, YtbPublisher):
    def __init__(self, env: Env, base_path=os.getcwd(), log: bool = False) -> None:
        """Reddit downloader class

        :param env: environs.Env object that already has been initialized. You can use utils.get_credentials() for that.
        :param log: True to log operations in console, by default to False.
        :param base_path: A string or pathlike to a folder where images and data will be downloaded (cwd by default).
        """

        # init parent classes
        Scale.__init__(self)
        CreateMovie.__init__(self, env, base_path)
        YtbPublisher.__init__(self, env)

        self._log = log

        # Check if credentials exists
        if not env("REDDIT_CLIENT_ID"):
            raise MissingCredentialsException("REDDIT_CLIENT_ID")
        if not env("REDDIT_CLIENT_SECRET"):
            raise MissingCredentialsException("REDDIT_CLIENT_SECRET")
        if not env("REDDIT_USER_AGENT"):
            raise MissingCredentialsException("REDDIT_USER_AGENT")

        # connect to reddit
        self.__reddit = praw.Reddit(
            client_id=env("REDDIT_CLIENT_ID"),
            client_secret=env("REDDIT_CLIENT_SECRET"),
            user_agent=env("REDDIT_USER_AGENT")
        )

        try:
            self.__reddit.user.me()
        except ResponseException:
            raise IncorrectCredentialsException()


        # define image format that we want to query
        self.__accepted_format = ["jpg", "png", "gif"]

        # define a path with folder that has today's date
        self.__today_data_path = os.path.join(base_path, f"data\\{date.today().strftime('%m%d%Y')}\\")

        # define path to utility file like already_downloaded.json
        self.__already_downloaded_path = os.path.join(base_path, f"data/utils/")

        # define file name for already downloaded images
        self.__already_downloaded_json = "already_downloaded.json"

        # store downloaded data in a single list
        self.__submission_data = []

        # create already_downloaded.json if not exists
        if not os.path.isdir(self.__already_downloaded_path):
            os.makedirs(self.__already_downloaded_path, exist_ok=True)
            with open(file=f"{self.__already_downloaded_path}{self.__already_downloaded_json}", mode="w"):
                pass

        # load json file to class
        with open(file=f"{self.__already_downloaded_path}{self.__already_downloaded_json}", mode="r",
                  encoding="utf-8-sig") as f:
            try:
                self.__already_downloaded = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                self.__already_downloaded = []

    def __create_subreddit_folder(self, subreddit: str) -> str:

        sub_path = os.path.join(self.__today_data_path, f"{subreddit}")
        if not os.path.isdir(sub_path):
            os.makedirs(sub_path, exist_ok=True)
            os.mkdir(os.path.join(sub_path, "images"))
            os.mkdir(os.path.join(sub_path, "data"))
        return sub_path

    def __get_posts_from_subreddit(self, subreddit: str, over_18: bool, amount: int, accepted_format: Tuple[str]) -> \
            List[praw.reddit.models.Submission]:

        submissions = []
        for submission in self.__reddit.subreddit(subreddit).top("day", limit=1000):
            if not submission.stickied and submission.url.lower()[-3:] in accepted_format and \
                    submission.over_18 == over_18 and submission.id not in self.__already_downloaded:
                submissions.append(submission)
            if len(submissions) >= amount:
                break
        return submissions

    def __save_submission_image(self, save_path: str, submission: praw.reddit.models.Submission, scale: tuple,
                                replace_resized: bool) -> None:

        img = requests.get(submission.url.lower())
        with open(save_path, "wb") as f:
            f.write(img.content)
        if self._log:
            print("Image downloaded.")
        if scale:
            if self._log:
                print("Resizing image...")
            self._scale_image(save_path, scale, replace_resized)

    def __save_submission_data(self, save_path: str, image_path: str,
                               submission: praw.reddit.models.Submission) -> None:
        submission.comment_sort = "best"
        best_comment = None
        best_comment_2 = None
        best_reply = None

        for comment in submission.comments:
            if len(comment.body) <= 140 and "http" not in comment.body:
                if not best_comment:
                    best_comment = comment
                else:
                    best_comment_2 = comment.body
                    break

        if best_comment:
            best_comment.reply_sort = "top"
            best_comment.refresh()

            for reply in best_comment.replies:
                if len(reply.body) >= 140 or "http" in reply.body:
                    continue
                best_reply = reply.body
                break

            best_comment = best_comment.body

        submission_data = {
            "image_path": image_path,
            'id': submission.id,
            "title": submission.title,
            "score": submission.score,
            "18": submission.over_18,
            "Best_comment": best_comment,
            "Best_comment_2": best_comment_2,
            "best_reply": best_reply
        }

        self.__already_downloaded.append(submission.id)
        self.__submission_data.append(submission_data)
        with open(f"{self.__already_downloaded_path}{self.__already_downloaded_json}", mode="w",
                  encoding="utf-8-sig") as f:
            json.dump(self.__already_downloaded, f)
        with open(f"{save_path}", mode="w", encoding="utf-8-sig") as f:
            json.dump(submission_data, f)

    def save_images_from_subreddit(self, subreddits: Tuple[str] = ("memes",), amount: int = 5,
                                   filetypes: tuple = ("jpg", "png"), nsfw: bool = False,
                                   scale: tuple = None, replace_resized: bool = True) -> List[dict]:
        """Save images from multiple subreddits.

        :param subreddits: Tuple of strings that contain subreddit names (by default, will search for the /r/memes
                subreddit)
        :param amount: amount of posts to query by subreddit. 5 by default.
        :param filetypes: a tuple of accepted file types. By default, : ("jpg", "png"). Warning ! Using other file
                types than those 2 may cause exceptions. That functionality hasn't been tested. Its use is mainly to
                restrain queries to one or two of the default types.
        :param nsfw: True for NSFW posts only, False for SFW posts only. False by default
        :param scale: a tuple (width: int, height: int) you can pass with the new width/height (in pixel) for each image
                downloaded. None by default
        :param replace_resized: used if a scale is passed. If True it replaces the images, if False it will create a
                new directory with resized images. True by default
        :return: data queried
        """
        self.__submission_data = []
        for subreddit in subreddits:
            save_path = self.__create_subreddit_folder(subreddit)
            if self._log:
                print(f"Search for images on the {subreddit} subreddit...")
            submissions = self.__get_posts_from_subreddit(subreddit, nsfw, amount, filetypes)
            if self._log:
                print("Images found ! start downloading them...")
            for submission in submissions:
                image_path = f"{save_path}\\images\\{submission.id}{submission.url.lower()[-4:]}"
                self.__save_submission_image(image_path, submission, scale, replace_resized)
                self.__save_submission_data(f"{save_path}\\data\\{submission.id}.json", image_path, submission)
            if self._log:
                print(f"{len(submissions)} images from /r/{subreddit} have been downloaded.")
        if self._log:
            print(f"Download finished for the following subreddit(s) : {', '.join(subreddits)}.")

        return self.__submission_data

    def create_video(self, video_data: List[dict] = None):
        """Create a video with the images previously saved from reddit.

        :param video_data: Optional Video data returned by .save_images_from_subreddit. If nothing passed it will
                use the last posts queried from reddit.
        :return: the path to the created video
        """
        return self._create_video(video_data if video_data else self.__submission_data)

    def get_path_images(self, data: List[dict] = None):
        """Return a list oh paths for the data passed

        :param data: optional data queried with .save_images_from_subreddit()
        :return: a list of path
        """
        if not data:
            data = self.__submission_data
        return [i["image_path"] for i in data]

    def publish_on(self, social_media: int, media_data: dict) -> None:
        """Publish a video or an image on a social media

        :param social_media: use utils.SocialMedias.TheSocialMediaYouWant
        :param media_data: dict that contains data about an image. It can be found in "{base_path}/data/{today}/{subreddit}/data/"
        :return: None
        """
        if social_media == 0:
            self._youtube(media_data)
            return

        if social_media == 1:
            # TODO: implement TikTok
            print("Not implemented yet")
            return

        if social_media == 2:
            # TODO: implement Instagram
            print("Not implemented yet")
            return

        print("Not implemented yet")
        # TODO: implement Snapchat

import os
from pprint import pprint

from environs import Env

from RedditDownloader import RedditBot


class Scales:
    """Some known format are already defined here. You can use them by importing Scales from utils.

    """
    Default = None

    # youtube format
    YoutubeShortsFullscreen = (1080, 1920)
    YoutubeShortsSquare = (1080, 1080)
    YoutubeVideo = (1920, 1080)

    # tiktok format
    TikTok = YoutubeShortsFullscreen

    # instagram format
    InstagramPhotoSquare = YoutubeShortsSquare
    InstagramPhotoLandscape = (1080, 608)
    InstagramPhotoPortrait = (1080, 1350)
    InstagramStories = YoutubeShortsFullscreen
    InstagramReels = InstagramStories
    InstagramIGTVCoverPhoto = (420, 654)
    InstagramVideoSquare = InstagramPhotoSquare
    InstagramVideoLandscape = (1080, 608)
    InstagramVideoPortrait = InstagramPhotoPortrait

    # snapchat format
    Snapchat = YoutubeShortsFullscreen

    @staticmethod
    def show_attributes():
        pprint([i for i in dir(Scales) if not i.startswith("__") and i != "show_attributes"])


class SocialMedias:
    YouTube = 0
    TikTok = 1
    Instagram = 2
    Snapchat = 3

    @staticmethod
    def show_attributes():
        pprint([i for i in dir(SocialMedias) if not i.startswith("__") and i != "show_attributes"])


def get_credentials():
    env = Env()
    env.read_env()
    return env


def initialize(base_path: str = os.getcwd()):
    RedditBot(get_credentials(), base_path)
    print("Application initialized !")
    exit()

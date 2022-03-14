import json
import os
import random
import sys
import time
from secrets import token_hex

import httplib2
from environs import Env
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


class YtbPublisher(object):
    httplib2.RETRIES = 1
    __MAX_RETRIES = 10
    __RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
    __RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
    __YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
    __YOUTUBE_API_SERVICE_NAME = "youtube"
    __YOUTUBE_API_VERSION = "v3"
    __MISSING_CLIENT_SECRETS_MESSAGE = "WRONG CREDENTIALS FOR THE YOUTUBE API"
    __VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

    def __init__(self, env: Env):
        self.__env = env
        self.__json_secret = ""
        if not env("GOOGLE_CLIENT_ID") or not env("GOOGLE_CLIENT_SECRET"):
            print("WARNING : Google credentials not added to .env . If you use "
                  ".publish_on(SocialMedias.YouTube) it will raise an error !")

    def __get_authenticated_service(self):
        flow = flow_from_clientsecrets(self.__json_secret,
                                       scope=self.__YOUTUBE_UPLOAD_SCOPE,
                                       message=self.__MISSING_CLIENT_SECRETS_MESSAGE)

        storage = Storage("%s-oauth2.json" % sys.argv[0])
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = run_flow(flow, storage)

        return build(self.__YOUTUBE_API_SERVICE_NAME, self.__YOUTUBE_API_VERSION,
                     http=credentials.authorize(httplib2.Http()))

    def __initialize_upload(self, youtube, options):
        tags = None
        #   if options.keywords:
        #     tags = options.keywords.split(",")

        body = dict(
            snippet=dict(
                title=options['title'],
                description=options['description'],
                tags=tags,
                # categoryId=options['category']
            ),
            status=dict(
                privacyStatus=options['privacyStatus']
            )
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
        )

        self.__resumable_upload(insert_request)

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def __resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print("Video id '%s' was successfully uploaded." % response['id'])
                    else:
                        exit("The upload failed with an unexpected response: %s" % response)
            except HttpError as e:
                if e.resp.status in self.__RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                         e.content)
                else:
                    raise
            except self.__RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                print(error)
                retry += 1
                if retry > self.__MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print("Sleeping %f seconds and then retrying..." % sleep_seconds)
                time.sleep(sleep_seconds)

    def _youtube(self, video_data):
        if not os.path.exists(video_data['file']):
            exit("Please specify a valid file using the file= parameter in the data passed to .publish_on().")

        client_json = {
            "web": {
                "client_id": self.__env("GOOGLE_CLIENT_ID"),
                "client_secret": self.__env("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        }
        self.__json_secret = f"{token_hex(4)}.json"
        with open(self.__json_secret, encoding="utf-8", mode="w") as f:
            json.dump(client_json, f)

        youtube = self.__get_authenticated_service()
        try:
            self.__initialize_upload(youtube, video_data)

        except HttpError as e:
            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        if os.path.isfile(self.__json_secret):
            os.remove(self.__json_secret)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    ytb = YtbPublisher(env)
    data = {
        "file": "C:\\Users\\julien.gunther\\PycharmProjects\\RedditDownloader\\videos\\67f2c04d.mp4",
        "title": "#shorts \n Memes but this time you laugh for real",
        "description": "why tho",
        "keywords": "meme,memes,laugh,internet,short",
        "privacyStatus": "private"
    }
    ytb._youtube(data)

# Reddit Image Downloader and publisher

## A follow up to [ClarityCoders' AutoTube](https://github.com/ClarityCoders/AutoTube)

### Requirements

You need a reddit application for that. You can create one to the following link :https://www.reddit.com/prefs/apps

You can follow this tutorial to create your application : https://youtu.be/bMT9ZC9sBzI?t=228

### Installation steps

1. Clone this repository
2. Install [ImageMagick](https://www.imagemagick.org/script/index.php)
3. Rename the [.env_sample](.env_sample) file to .env
4. Edit your .env file :
    - REDDIT_CLIENT_SECRET="YourClientSecret"
    - REDDIT_CLIENT_ID="YourClientId"
    - REDDIT_USER_AGENT="<AppName-AppVersion>"
    - IMAGEMAGICK_BINARIES="C:\Program Files\ImageMagick-7.1.0-Q16-HDRI\magick.exe" (Change the path to your
      installation to the magick.exe file. Check [moviepy on pypi](https://pypi.org/project/moviepy/) for more
      information)

The `IMAGEMAGICK_BINARIES` environment variable is only needed if you're on Windows or on Ubuntu 16.04LTS

An example for the reddit user agent : "<MemeAcquisition-v1.0>"

4. open a console (bash, cmd, etc...) where you cloned the repo and enter the following command :

`pip install -r requirements.txt`

If it returns an error, try the following command :

`pip3 install -r requirements.txt`

Is it still doesn't work, make sure you that python and pip are properly installed.

## How to use

Some code will be more explicit :

````python
from RedditDownloader import RedditBot
from utils import SocialMedias, get_credentials, Scales

reddit = RedditBot(get_credentials())
data = reddit.save_images_from_subreddit(
    amount=5,
    subreddits=("dankmemes",),
    scale=Scales.InstagramPhotoSquare
)
video_path = reddit.create_video(data)

ytb_data = {
    "file": video_path,
    "title": "#shorts \n Memes but this time you laugh for real",
    "description": "why tho",
    "keywords": "meme,memes,laugh,internet,shorts",
    "privacyStatus": "public"
}

reddit.publish_on(SocialMedias.YouTube, ytb_data)

````

## RedditBot

This class takes 2 arguments :

- required : `env` - `environs.Env` instance that has been initialized. There's a utility function for that :
  `utils.get_credentials()`
- optional : `log` - `True` to log to console operation, `False` by default

You then have a single method described below :

## RedditBot.save_images_from_subreddit()

All 6 keyword arguments are optional.

- `subreddits` - a tuple of strings that contains the subreddit names. By default, it will query the
  [memes](https://www.reddit.com/r/memes/) subreddit. Check out what's after the r/ to known what is the exact string to
  add to the tuple.


- `amount` - how many images (posts) do you want to download (int). By default, 5.


- `filetypes` - A tuple that contains all the file extensions that you want to download. By default,
  ("jpg", "png", "gif"). It may be used to download only jps and png or only gif. It may raise errors with other file
  extensions.


- `nsfw` - bool. If set to True it will only download NSFW posts (marked NSFW by the community or mods). If set to False
  it will only download SFW posts. By default, set to False.


- `scale` - tuple of ints. If passed, it will resize the downloaded images with the size passed as argument
  (width, height). By default, None is passed so no resize occurs. Some sizes are already defined for TikTok, YouTube or
  Instagram. -> see [Scales](#scales)


- `replace_resized` - bool. Only works when a new scale is passed. If set to False the resized image will be placed in
  a "resized" folder along with the original images. If set to True it will replace the original images.

This method will return a `list of dict` with the data queried that you can use later on.

## RedditBot.create_video()

This method will create a video with the data previously queried. it takes an optional argument :

- video_data : that correspond to the data queried. If no argument are passed, it will take the last data queried if
  still in memory. If no argument are passed and there is no data left in memory, it will raise an exception.

It returns the path to the created video.

## RedditBot.get_path_images()

This method will return the path of the queried images. it takes one optional argument :

- data : that correspond to the data queried. If no argument are passed, it will take the last data queried if still in
  memory. If no argument are passed and there is no data left in memory, it will raise an exception.

## RedditBot.publish_on()

Publish photo or video on a social media.

Takes 2 required arguments :

- social_media - see [SocialMedias](#SocialMedias)
- data - a dict that contains all the data needed for the post. See [Data format](#data-format) for more information
  about the data formatting.

## Scales

There's some scales already defined. To access them, import `Scales` from `utils` :

````python
from utils import Scales

Scales.show_attributes()
````

````text
['Default',
 'InstagramIGTVCoverPhoto',
 'InstagramPhotoLandscape',
 'InstagramPhotoPortrait',
 'InstagramPhotoSquare',
 'InstagramReels',
 'InstagramStories',
 'InstagramVideoLandscape',
 'InstagramVideoPortrait',
 'InstagramVideoSquare',
 'Snapchat',
 'TikTok',
 'YoutubeShortsFullscreen',
 'YoutubeShortsSquare',
 'YoutubeVideo']
````

## SocialMedias

Use this class to choose a social media to posts your video/photo

````python
from utils import SocialMedias

SocialMedias.show_attributes()
````

````text
['Instagram', 'Snapchat', 'TikTok', 'YouTube']
````

usage :

````python
from RedditDownloader import RedditBot
from utils import SocialMedias, get_credentials, Scales

reddit = RedditBot(get_credentials())
data = reddit.save_images_from_subreddit(
    amount=5,
    subreddits=("dankmemes",),
    scale=Scales.InstagramPhotoSquare
)
video_path = reddit.create_video(data)

ytb_data = {
    "file": video_path,
    "title": "#short \n Memes but this time you laugh for real",
    "description": "why tho",
    "keywords": "meme,memes,laugh,internet,short",
    "privacyStatus": "public"
}

reddit.publish_on(SocialMedias.YouTube, ytb_data)

````

## Data format

### for create_video()

````json
[
  {
    "image_path": "absolute path to image",
    "Best_comment": "best comment on this image",
    "best_reply": "best reply of the best comment"
  },
  {
    "image_path": "absolute path to image",
    "Best_comment": "best comment on this image",
    "best_reply": "best reply of the best comment"
  },
  ...
]
````

### for publish_on(SocialMedias.YouTube)
````json

{
  "file": "absolute path to video",
  "title": "video title",
  "description": "video description",
  "keywords": "tag1,tag2,tag3...",
  "privacyStatus": "private|public|unlisted"
}
````

### for publish_on(SocialMedias.Instagram)
#### still not implemented
````json
{
  "files": ["absolute path to video/photo1", "absolute path to video/photo2", ...],
  "description": "post description",
  "type": "igtv|reels|post"
}
````

### for publish_on(SocialMedias.TikTok)
#### still not implemented
````json
{
  "file": "absolute path to video",
  "description": "post description"
}
````

### for publish_on(SocialMedias.Snapchat)
#### still not implemented
````json
{
  "file": "absolute path to video",
  "description": "post description"
}
````
import os.path
import platform
import random
from pathlib import Path
from secrets import token_hex
from typing import List

from environs import Env
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.editor import ImageSequenceClip, VideoFileClip, concatenate_videoclips, TextClip, AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

from RedditDownloaderExceptions import MissingImageMagickBinariesException, MissingMP3FilesInMusicsDir
from .utils import Utils


class CreateMovie(Utils):
    def __init__(self, env: Env, base_path: str):
        Utils.__init__(self)
        self.__env = env
        self.__path = base_path
        self.__music_path = os.path.join(self.__path, "musics\\")
        self.__video_path = os.path.join(self.__path, "videos\\")
        if not os.path.isdir(self.__video_path):
            os.mkdir(self.__video_path)

        if not os.path.isdir(self.__music_path):
            os.mkdir(self.__music_path)

    def _create_video(self, submission_data: List[dict]) -> str:

        # check if magick binaries exists if on windows
        if platform.system() == "Windows" and (
                not self.__env("IMAGEMAGICK_BINARY") or not os.path.isfile(self.__env("IMAGEMAGICK_BINARY"))):
            raise MissingImageMagickBinariesException(self.__env("IMAGEMAGICK_BINARY"))

        # check if there's music inside the musics dir
        if not list(Path(self.__music_path).rglob(".mp3")):
            raise MissingMP3FilesInMusicsDir(self.__music_path)

        clips = []
        for submission in submission_data:
            if "gif" not in submission["image_path"][-3:]:
                clip = ImageSequenceClip([submission["image_path"]], durations=[12])
                clips.append(clip)
                continue
            clip_lengthener = [VideoFileClip(submission["image_path"])] * 60
            clip = concatenate_videoclips(clip_lengthener).subclip(0, 12)
            clips.append(clip)

        clip = concatenate_videoclips(clips).subclip(0, 60)
        colors = ['yellow', 'LightGreen', 'LightSkyBlue', 'LightPink4', 'SkyBlue2', 'MintCream', 'LimeGreen',
                  'WhiteSmoke', 'HotPink4', 'PeachPuff3', 'OrangeRed3', 'silver']
        random.shuffle(colors)

        text_clips = []
        notification_sounds = []

        for i, post in enumerate(submission_data):
            return_comment, return_count = self._add_return_comment(post['Best_comment'])

            txt = TextClip(return_comment, font='Courier',
                           fontsize=38, color=colors.pop(), bg_color='black')
            txt = txt.on_color(col_opacity=.3)
            txt = txt.set_position((5, 500))
            txt = txt.set_start((0, 3 + (i * 12)))  # (min, s)
            txt = txt.set_duration(7)
            txt = txt.crossfadein(0.5)
            txt = txt.crossfadeout(0.5)
            text_clips.append(txt)

            return_comment, _ = self._add_return_comment(post['best_reply'])

            txt = TextClip(return_comment, font='Courier',
                           fontsize=38, color=colors.pop(), bg_color='black')
            txt = txt.on_color(col_opacity=.3)
            txt = txt.set_position((15, 585 + (return_count * 50)))
            txt = txt.set_start((0, 5 + (i * 12)))  # (min, s)
            txt = txt.set_duration(7)
            txt = txt.crossfadein(0.5)
            txt = txt.crossfadeout(0.5)
            text_clips.append(txt)

            notification = AudioFileClip(os.path.join(self.__music_path, f"notification.mp3"))
            notification = notification.set_start((0, 3 + (i * 12)))
            notification_sounds.append(notification)
            notification = AudioFileClip(os.path.join(self.__music_path, f"notification.mp3"))
            notification = notification.set_start((0, 5 + (i * 12)))
            notification_sounds.append(notification)

        music_file = os.path.join(self.__music_path, f"music{random.randint(0, 4)}.mp3")
        music = AudioFileClip(music_file)
        music = music.set_start((0, 0))
        music = music.volumex(.4)
        music = music.set_duration(59)

        new_audioclip = CompositeAudioClip([music] + notification_sounds)
        filename = token_hex(4)
        filename_clips = filename + "_clips.mp4"
        filename += ".mp4"
        clip.write_videofile(f"{self.__video_path}{filename_clips}", fps=24)

        clip = VideoFileClip(f"{self.__video_path}{filename_clips}", audio=False)
        clip = CompositeVideoClip([clip] + text_clips)
        clip.audio = new_audioclip
        clip.write_videofile(f"{self.__video_path}{filename}", fps=24)

        if os.path.exists(os.path.join(self.__video_path, f"{filename_clips}")):
            os.remove(os.path.join(self.__video_path, f"{filename_clips}"))

        return self.__video_path + filename

import os

from PIL import Image


class Scale(object):
    def __init__(self):
        pass

    def _scale_image(self, path: str, scale: tuple, replace_resized: bool):
        img = Image.open(path)
        filename = path.split("\\")[-1]

        if not replace_resized:
            path = path.replace(filename, "resized\\")
            if not os.path.isdir(path):
                os.mkdir(path)
            path += filename

        if path[-3:] != "gif":
            img = img.resize(scale)
            img.save(path)
            return

        old_infos = {
            "version": img.info.get("version", b"GIF01a"),
            "loop": bool(img.info.get("loop", 1)),
            "duration": img.info.get("duration", 40),
            "background": img.info.get("background", 223),
            'extension': img.info.get('extension', b'NETSCAPE2.0'),
            'transparency': img.info.get('transparency', 223)
        }

        new_frames = self.__get_new_frames(img, scale)
        self.__save_new_gif(new_frames, old_infos, path)

    @staticmethod
    def __get_new_frames(gif: Image, scale: tuple) -> list:
        new_frames = []
        actual_frames = gif.n_frames
        for frame in range(actual_frames):
            gif.seek(frame)
            new_frame = Image.new('RGBA', gif.size)
            new_frame.paste(gif)
            new_frame = new_frame.resize(scale, Image.ANTIALIAS)
            new_frames.append(new_frame)
        return new_frames

    @staticmethod
    def __save_new_gif(frames: list, old_infos: dict, path: str):
        frames[0].save(
            path,
            version=old_infos["version"],
            append_images=frames[1:],
            duration=old_infos['duration'],
            loop=old_infos['loop'],
            background=old_infos['background'],
            extension=old_infos['extension'],
            transparency=old_infos['transparency']
        )

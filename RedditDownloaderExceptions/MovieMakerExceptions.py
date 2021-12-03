class MovieMakerException(Exception):
    """Base exception for the RedditBot class
    """

    def __init__(self, *args):
        Exception.__init__(self, *args)


class MissingImageMagickBinariesException(MovieMakerException):
    """Raised when missing magick binaries
    """

    def __init__(self, path: str,
                 message: str = "Missing ImageMagick binaries or path not valid. Please complete your .env file."):
        self.__path = path
        self.__message = message
        MovieMakerException.__init__(self, message)

    def __str__(self):
        return f"{self.__message} : \"{self.__path}\""


class MissingMP3FilesInMusicsDir(MovieMakerException):
    """Raised if the musics dir doesn't contain any mp3 file
    """

    def __init__(self, path, message: str = "Missing MP3 files in"):
        self.__message = message
        self.__path = path
        MovieMakerException.__init__(self, message)

    def __str__(self):
        return f"{self.__message} {self.__path}"

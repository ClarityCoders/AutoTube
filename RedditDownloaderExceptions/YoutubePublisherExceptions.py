class YoutubePublisherException(Exception):
    """Base exception for the RedditBot class
    """

    def __init__(self, *args):
        Exception.__init__(self, *args)


class MissingCredentialsException(YoutubePublisherException):
    """Raised when credentials for YouTube are missing
    """

    def __init__(self, credential, message="Missing youtube credentials. Please complete your .env file."):
        self.__credential = credential
        self.__message = message
        YoutubePublisherException.__init__(self, message)

    def __str__(self):
        return f"{self.__message} : \"{self.__credential}\""

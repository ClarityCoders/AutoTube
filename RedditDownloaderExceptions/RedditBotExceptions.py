class RedditBotException(Exception):
    """Base exception for the RedditBot class
    """

    def __init__(self, *args):
        Exception.__init__(self, *args)


class MissingCredentialsException(RedditBotException):
    """Raised when credentials for Reddit are missing
    """

    def __init__(self, credential, message="Missing reddit credentials. Please complete your .env file."):
        self.__credential = credential
        self.__message = message
        RedditBotException.__init__(self, message)

    def __str__(self):
        return f"{self.__message} : \"{self.__credential}\""


class IncorrectCredentialsException(RedditBotException):
    """Raised when reddit credentials are not correct
    """

    def __init__(self,
                 message: str = "Can't connect to reddit with current credentials. Please enter valid credentials in your .env file."):
        RedditBotException.__init__(self, message)

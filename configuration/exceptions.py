""" Custom exceptions used to control the execution flow throughout the app. """


class NoAuthenticationFoundError(Exception):
    """ Raised when no authentication was found. """

    def __init__(self):
        super(NoAuthenticationFoundError, self).__init__()


class NoConfigFileFoundError(Exception):
    """ Raised when no config file was found. """

    def __init__(self):
        super(NoConfigFileFoundError, self).__init__()


class AlreadyDownloadedError(Exception):
    """ Raised when trying to download a file that is already present. """

    def __init__(self, filename):
        super(AlreadyDownloadedError, self).__init__()
        self.filename = filename

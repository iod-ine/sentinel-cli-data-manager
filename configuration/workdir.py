""" Manage the working directory. """

import pathlib

import configuration.paths as paths


def initialize_working_directory():
    """ Set up the directory structure for the project. """

    pathlib.Path('Data').mkdir(exist_ok=True)
    paths.raw_file_storage.mkdir(exist_ok=True)
    paths.processed_file_storage.mkdir(exist_ok=True)
    paths.quicklook_storage.mkdir(exist_ok=True)

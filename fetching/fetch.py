""" `sdm fetch` command group initiates the download of requested things. """

import click

from fetching import metadata


@click.group()
def fetch():
    """ Download products, quicklooks, and metadata. """

    return


fetch.add_command(metadata)

""" CLI Sentinel Data Manager. Automating parts of Remote Sensing workflows. """

import click

from meta import init
from meta import database
from fetching import fetch
from searching import search
from searching import generate_query


@click.group()
def sdm():
    """ Sentinel Data Manager: manage Copernicus remote sensing data from the command line. """

    return


sdm.add_command(init)
sdm.add_command(fetch)
sdm.add_command(search)
sdm.add_command(database)
sdm.add_command(generate_query)

if __name__ == '__main__':
    sdm()

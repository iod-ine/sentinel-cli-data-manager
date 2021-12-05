""" CLI Sentinel Data Manager. Automating parts of Remote Sensing workflows. """

import click

from configuration import init
from searching import generate_query


@click.group()
def sdm():
    """ Sentinel Data Manager: manage Copernicus remote sensing data from the command line. """

    return


sdm.add_command(init)
sdm.add_command(generate_query)

# sdm generate-query
# sdm copy-last-query

if __name__ == '__main__':
    sdm()

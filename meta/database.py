""" `sdm database` command interacts with the database. """

import sqlite3

import click

import configuration.paths as paths


@click.group()
def database():
    """ Manage the metadata database. """

    return


@click.command()
def prune():
    """ Delete metadata for not downloaded files. """

    return


@click.command()
def purge():
    """ Delete all metadata from the database. """

    if click.confirm('Are you sure?'):
        with sqlite3.connect(paths.database) as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM metadata WHERE TRUE;')

        # carriage return, clear line
        click.secho('\r\033[0J⚙ ', fg='green', nl=False)
        click.echo(f'Metadata database purged.')

    return


database.add_command(purge)

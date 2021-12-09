""" `sdm fetch metadata ` command downloads metadata for all products in the database. """

import sqlite3

import click

import fetching.data_api as api
import configuration.paths as paths
import configuration.exceptions as exceptions


@click.command()
@click.option('--eumetsat', is_flag=True, help='Send the request to EUMETSAT (for Sentinel-3 ocean data).')
def metadata(eumetsat):
    """ Fetch metadata for all found products. """

    with sqlite3.connect(paths.database) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM metadata WHERE status = "found" AND eumetsat = ?;', (int(eumetsat),))
        search_results = cursor.fetchall()

    if not search_results:
        # carriage return, clear line
        click.secho('\r\033[0J⚙ ', fg='yellow', nl=False)
        click.echo('No new search results to fetch metadata for.')
        return

    ids = [result[0] for result in search_results]

    try:
        # carriage return, clear line
        click.echo(f'\r\033[0J⏳ Fetching metadata [0/{len(ids)}]', nl=False)

        for items_fetched in api.fetch_metadata_by_ids(ids, eumetsat=eumetsat):
            # carriage return, clear line
            click.echo(f'\r\033[0J⏳ Fetching metadata [{items_fetched}/{len(ids)}]', nl=False)

        # carriage return, clear line
        click.secho('\r\033[0J✓ ', fg='green', nl=False)
        click.echo('Fetched all available metadata.')
    except exceptions.FailedRequestError as e:
        # carriage return, clear line
        click.secho('\r\033[0J⚙ ', fg='red', nl=False)
        click.echo(f'Get request status code: {e.request.status_code} [{e.request.reason}]. Terminating.')
        return

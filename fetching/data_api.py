""" Manage the Copernicus / EUMETSAT OData API. """

import re
import time
import shutil
import pathlib
import sqlite3

import click
import requests
import feedparser

import configuration.urls as urls
import configuration.paths as paths
import configuration.exceptions as exceptions
import configuration.authentication as authentication


def fetch_metadata_by_id(id_, eumetsat=False):
    """ Fetch metadata for the product with the given ID.

    Args:
        id_ (str): ID to fetch metadata for.
        eumetsat (bool): Use Eumetsat instead of Copernicus OA Hub (for Sentinel-3 ocean data).

    Returns:
       id_, title, wkt, file_size, eumetsat, status: values for columns of the database.

    Notes:
        The function does not check if the metadata is already in the database by design.

    """

    auth = authentication.get_authentication(eumetsat=eumetsat)

    if auth is None:
        raise exceptions.NoAuthenticationFoundError()

    query = 'INSERT INTO metadata(product_id, title, footprint_wkt, file_size, eumetsat, status) VALUES ' \
            '(?, ?, ?, ?, ?, ?) ON CONFLICT(product_id) DO UPDATE SET footprint_wkt = ?, file_size = ?, status = ?;'

    coordinates_regex = re.compile(r'<gml:coordinates>(.+)</gml:coordinates>')

    url = urls.get_product_url(id_, eumetsat=eumetsat)
    request = requests.get(url, auth=auth)

    if request.status_code != 200:
        raise exceptions.FailedRequestError(request)

    entry = feedparser.parse(request.content)['entries'][0]

    title = entry['d_name']

    extracted_coordinates = coordinates_regex.findall(entry['d_contentgeometry'])[0]
    extracted_coordinates = extracted_coordinates.split(' ')
    extracted_coordinates = ','.join([' '.join(s.split(',')[::-1]) for s in extracted_coordinates])

    wkt = f'Polygon(({extracted_coordinates}))'
    file_size = int(entry['d_contentlength'])

    # EUMETSAT has no offline products, so their feeds don't have the 'd_online' property.
    status = 'online' if entry.get('d_online', 'true') == 'true' else 'offline'

    with sqlite3.connect(paths.database) as connection:
        cursor = connection.cursor()
        cursor.execute(query, (id_, title, wkt, file_size, eumetsat, status, wkt, file_size, status))

    return id_, title, wkt, file_size, eumetsat, status


def fetch_metadata_by_ids(ids, eumetsat=False):
    """ Fetch metadata for the product with the given ID.

    Args:
        ids (list of str): List of IDs to fetch metadata for.
        eumetsat (bool): Use Eumetsat instead of Copernicus OA Hub (for Sentinel-3 ocean data).

    Notes:
        The function works like a generator, yielding the number of processed products.
        That is a way to keep progress when fetching multiple results.

    """

    for i, id_ in enumerate(ids, 1):
        fetch_metadata_by_id(id_, eumetsat=eumetsat)
        yield i


def download_product(url, auth, file):
    """ Download a product from the given url to the specified file. """

    with requests.get(url, stream=True, auth=auth) as request:
        if request.status_code != 200:
            raise exceptions.FailedRequestError(request)

        with open(file, 'bw') as f:
            shutil.copyfileobj(request.raw, f)


def monitor_download_process(process, file, target_size):
    """ Report the progress of a running download process. """

    file = pathlib.Path(file)
    start_time = time.time()
    target_size_mb = round(target_size / 1024 / 1024, 1)

    while process.is_alive():
        try:
            current_size = file.stat().st_size
        except FileNotFoundError:
            current_size = 0

        current_size_mb = round(current_size / 1024 / 1024, 1)
        percent_done = current_size / target_size * 100

        elapsed_time = time.gmtime(time.time() - start_time)
        elapsed_time = time.strftime("%H:%M:%S", elapsed_time)

        click.echo(f'\r\033[0J    Downloading: {current_size_mb} / {target_size_mb} MB', nl=False)
        click.echo(f' [{percent_done:.2f}%] {elapsed_time}', nl=False)
        time.sleep(0.2)

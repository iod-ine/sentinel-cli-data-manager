""" Manage the Copernicus / EUMETSAT OData API. """

import re
import sqlite3
import requests
import feedparser

import configuration.urls as urls
import configuration.paths as paths
import configuration.exceptions as exceptions
import configuration.authentication as authentication


def fetch_metadata_by_ids(ids, eumetsat=False):
    """ Fetch metadata for the product with the given ID.

    Args:
        ids (list of str): List of product IDs to fetch metadata for.
        eumetsat (bool): Use Eumetsat instead of Copernicus OA Hub (for Sentinel-3 ocean data).

    Notes:
        The function works like a generator, yielding the number of processed products. I want to keep track
        of the fetching progress within the command, to display some sort of progress. This is a way to do that.

    """

    auth = authentication.get_authentication(eumetsat=eumetsat)

    if auth is None:
        raise exceptions.NoAuthenticationFoundError()

    query = 'UPDATE metadata SET footprint_wkt = ?, file_size = ?, status = ? WHERE product_id = ?;'
    coordinates_regex = re.compile(r'<gml:coordinates>(.+)</gml:coordinates>')

    for i, id_ in enumerate(ids, 1):
        url = urls.get_product_url(id_, eumetsat=eumetsat)
        request = requests.get(url, auth=auth)

        if request.status_code != 200:
            raise exceptions.FailedRequestError(request)

        entry = feedparser.parse(request.content)['entries'][0]

        extracted_coordinates = coordinates_regex.findall(entry['d_contentgeometry'])[0]
        extracted_coordinates = extracted_coordinates.split(' ')
        extracted_coordinates = ','.join([' '.join(s.split(',')[::-1]) for s in extracted_coordinates])

        wkt = f'Polygon(({extracted_coordinates}))'
        file_size = int(entry['d_contentlength'])

        # EUMETSAT has no offline products, so their feeds don't have the 'd_online' property.
        status = 'online' if entry.get('d_online', 'true') == 'true' else 'offline'

        with sqlite3.connect(paths.database) as connection:
            cursor = connection.cursor()
            cursor.execute(query, (wkt, file_size, status, id_))

        yield i

""" Manage the Copernicus / EUMETSAT OpenSearch API. """

import time
import sqlite3

import click
import requests
import feedparser

import configuration.urls as urls
import configuration.paths as paths
import configuration.config as config
import configuration.exceptions as exceptions
import configuration.authentication as authentication


def execute_search_query(query, start, eumetsat=False):
    """ Send a GET request with the query to Copernicus/EUMETSAT Open Search API.

    Args:
        query (str): A query to use.
        start (int): Controls paging of Open Search. It returns 100 rows max, this will set the starting row.
        eumetsat (bool): Use Eumetsat instead of Copernicus OA Hub (for Sentinel-3 ocean data).

    Returns:
        request: A resulting GET request.

    """

    url = urls.get_search_url(eumetsat=eumetsat)
    auth = authentication.get_authentication(eumetsat=eumetsat)

    if auth is None:
        raise exceptions.NoAuthenticationFoundError()

    request = requests.get(url, params={'q': query, 'start': start, 'rows': 100}, auth=auth)

    return request


def process_search_request(request, eumetsat=False):
    """ Extract product metadata from a search request and save it to the database.

     Returns:
         new_count, total_count: The number of new products found and the total number of products that match.

    """

    feed = feedparser.parse(request.content)
    entries = feed['entries']

    if entries:
        lookup_query = 'SELECT count(*) FROM metadata WHERE product_id = ?;'
        insert_query = 'INSERT INTO metadata(product_id, title, summary, eumetsat, status) VALUES (?, ?, ?, ?, ?);'
        new_count, old_count = 0, 0

        with sqlite3.connect(paths.database) as connection:
            cursor = connection.cursor()

            for entry in entries:
                # we don't need to do anything if the product is already in the database
                cursor.execute(lookup_query, (entry['id'],))
                if cursor.fetchone()[0] == 1:
                    old_count += 1
                    continue

                # everything else is not yet in the database
                cursor.execute(
                    insert_query,
                    (entry['id'], entry['title'], entry['summary'], int(eumetsat), 'found')
                )
                new_count += 1

        return new_count, new_count + old_count
    else:
        return 0, 0


def generate_query(s1, s2, s3):
    """ Generate a query based on the configuration.

    Args:
        s1 (bool): Include Sentinel-1 into the query.
        s2 (bool): Include Sentinel-2 into the query.
        s3 (bool): Include Sentinel-3 into the query.

    """

    queries = []

    if s1:
        queries.append(generate_sentinel1_search_query())

    if s2:
        queries.append(generate_sentinel2_search_query())

    if s3:
        queries.append(generate_sentinel3_search_query())

    if len(queries) == 0:
        return
    elif len(queries) == 1:
        query = queries[0]
    else:
        queries = [f'({q})' for q in queries]
        query = ' OR '.join(queries)

    return query


def generate_sentinel1_search_query():
    """ Generate a search query for Sentinel-1 based on the configuration. """

    roi = config.get_roi()
    start_date, end_date = config.get_dates()

    params = config.get_config().get('Search').get('Sentinel-1')

    if params is None:
        return ""

    query = 'platformname:Sentinel-1 '
    query += f'AND {params["Sensor mode"]} '
    query += f'AND {params["Product type"]} AND beginposition:'
    query += f'[{start_date}T00:00:00.000Z TO {end_date}T23:59:59.999Z] '
    query += f'AND footprint:"Intersects({roi})"'

    return query


def generate_sentinel2_search_query():
    """ Generate a search query for Sentinel-2 based on the configuration. """

    roi = config.get_roi()
    start_date, end_date = config.get_dates()

    params = config.get_config().get('Search').get('Sentinel-2')

    if params is None:
        return ""

    query = 'platformname:Sentinel-2 '
    query += f'AND producttype:{params["Product type"]} AND beginposition:'
    query += f'[{start_date}T00:00:00.000Z TO {end_date}T23:59:59.999Z] '

    if params.get('Max cloud cover %') is not None:
        query += f'cloudcoverpercentage:[0 TO {params.get("Max cloud cover %")}] '

    if params.get('Tiles') is not None:
        if len(params.get('Tiles')) == 1:
            query += f'AND filename:*{params.get("Tiles")[0]}* '
        else:
            terms = [f'filename:*{tile}*' for tile in params.get('Tiles')]
            query += f'AND ({" OR ".join(terms)})'
    else:
        query += f'AND footprint:"Intersects({roi})"'

    return query


def generate_sentinel3_search_query():
    """ Generate a search query for Sentinel-3 based on the configuration. """

    roi = config.get_roi()
    start_date, end_date = config.get_dates()

    params = config.get_config().get('Search').get('Sentinel-3')

    if params is None:
        return ""

    query = 'platformname:Sentinel-3 AND beginposition:'
    query += f'[{start_date}T00:00:00.000Z TO {end_date}T23:59:59.999Z] '

    if len(params.get('Instruments')) == 1:
        query += f'AND instrumentshortname:{params.get("Instruments")[0]} '
    else:
        terms = [f'instrumentshortname:{instrument}' for instrument in params.get('Instruments')]
        query += f'AND ({" OR ".join(terms)}) '

    query += f'AND productlevel:{params["Product level"]} '
    query += f'AND footprint:"Intersects({roi})"'

    return query


def wait_for_search_thread(search_thread):
    """ Display the loading animation while waiting for the searching thread to finish. """

    symbols = list('|/-\\')
    index = 0

    while search_thread.running():
        click.echo(f'\r{symbols[index]} Searching for matching products...', nl=False)
        time.sleep(0.1)
        index = index + 1 if index < 3 else 0

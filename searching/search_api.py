""" Manage the Copernicus / EUMETSAT OpenSearch API. """

import configuration.config as config


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

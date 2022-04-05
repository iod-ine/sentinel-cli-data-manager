""" `sdm fetch product` command downloads individual products. """

import shutil
import concurrent.futures

import click
import requests

import fetching.data_api as data_api
import searching.search_api as search_api
import configuration.urls as urls
import configuration.paths as paths
import configuration.exceptions as exceptions
import configuration.authentication as authentication


@click.command()
@click.option('--id', 'id_', help='Fetch product with the given ID.')
@click.option('--name', help='Fetch product with the given name.')
@click.option('--eumetsat', is_flag=True, help='Send the request to EUMETSAT (for Sentinel-3 ocean data).')
def product(id_, name, eumetsat):
    """ Fetch individual products. """

    if name is not None:
        result = search_api.find_product_by_name(name, eumetsat=eumetsat)

        if result is None:
            # carriage return, clear line
            click.secho('\r\033[0J✗ ', fg='red', nl=False)
            click.echo(f'Cannot find a product with that name.')
            return

        id_ = result[0]

    if id_ is None:
        # carriage return, clear line
        click.secho('\r\033[0J✗ ', fg='red', nl=False)
        click.echo(f'Not enough information to fetch a product.')
        return

    result = data_api.fetch_metadata_by_id(id_, eumetsat=eumetsat)
    id_, title, wkt, file_size, eumetsat, status = result

    product_file = paths.raw_file_storage / f'{title}.zip'

    if product_file.exists() and product_file.stat().st_size == file_size:
        # carriage return, clear line
        click.secho(f'\r\033[0J✓ ', fg='green', nl=False)
        click.echo(f'{title}')
        return

    if status in ['offline', 'requested']:
        # carriage return, clear line
        click.secho('\r\033[0J✗ ', fg='red', nl=False)
        click.echo(f'The product is not online. Use the watcher instead.')
        return

    url = urls.get_product_url(id_, eumetsat=eumetsat) + '$value'
    auth = authentication.get_authentication(eumetsat=eumetsat)

    if auth is None:
        raise exceptions.NoAuthenticationFoundError()

    with requests.get(url, stream=True, auth=auth) as request:
        if request.status_code != 200:
            # carriage return, clear line
            click.secho('\r\033[0J⚙ ', fg='red', nl=False)
            click.echo(f'Get request status code: {request.status_code} [{request.reason}]. Terminating.')
            return

        # carriage return, clear line
        click.echo(f'\r\033[0J⏳ ', nl=False)
        click.secho(f'{title}', bold=True)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            download_thread = executor.submit(data_api.write_request_content_to_file, request, product_file)
            executor.submit(data_api.wait_for_download_thread, download_thread, product_file, file_size)

    # go to the beginning of previous line, clear line
    click.secho(f'\033[1F\033[0J✓ ', fg='green', nl=False)
    click.echo(f'{title}')

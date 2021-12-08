""" `sdm search` command generates and executes a query using configuration files. """

import concurrent.futures

import click

import searching.search_api as api
import configuration.config as config


@click.command()
@click.option('--eumetsat', is_flag=True, help='Send the request to EUMETSAT (for Sentinel-3 ocean data).')
def search(eumetsat):
    """ Execute a search request based on the configuration. """

    try:
        params = config.get_config()
    except FileNotFoundError:
        # carriage return, clear line
        click.secho('\r\033[0J⚙ ', fg='red', nl=False)
        click.echo('Cannot load the configuration file. Terminating.')
        return

    search_params = params.get('Search')

    if eumetsat:
        if 'Sentinel-3' not in search_params:
            # carriage return, clear line
            click.secho('\r\033[0J⚙ ', fg='red', nl=False)
            click.echo('Search is not configured for Sentinel-3. Terminating.')
            return

        query = api.generate_query(s1=False, s2=False, s3=True)
    else:
        s1 = 'Sentinel-1' in search_params
        s2 = 'Sentinel-2' in search_params
        s3 = 'Sentinel-3' in search_params
        query = api.generate_query(s1=s1, s2=s2, s3=s3)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        search_thread = executor.submit(lambda: api.execute_search_query(query))
        executor.submit(lambda: api.wait_for_search_thread(search_thread))

    search_request = search_thread.result()

    if search_request.status_code != 200:
        # carriage return, clear line
        click.secho('\r\033[0J⚙ ', fg='red', nl=False)
        click.echo(f'Search request status code: {search_request.status_code} [{search_request.reason}]. Terminating.')
        return

    new_count, total_count = api.process_search_request(search_request, eumetsat=eumetsat)

    if (new_count, total_count) == (0, 0):
        # carriage return, clear line
        click.secho('\r\033[0J✗ ', fg='red', nl=False)
        click.echo(f'Found no matching products.')
        return

    # carriage return, clear line
    click.secho('\r\033[0J✓ ', fg='green', nl=False)
    if new_count == 0:
        click.echo(f'Found 0 new products ({total_count} total).')
    elif new_count == 1:
        click.echo(f'Found 1 new product ({total_count} total).')
    else:
        click.echo(f'Found {new_count} new products ({total_count} total).')

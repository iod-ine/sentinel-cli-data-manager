""" `sdm generate-query` command generates and executes a query using configuration files. """

import click
import pyperclip

import searching.search_api as api
import configuration.config as config


@click.command(name='generate-query')
@click.option('--s1', is_flag=True, help='Include Sentinel-1.')
@click.option('--s2', is_flag=True, help='Include Sentinel-2.')
@click.option('--s3', is_flag=True, help='Include Sentinel-3.')
@click.option('--product-list', 'product_list', help='File with a list of products separated by newlines.')
@click.option('--print', 'print_', is_flag=True, help='Print the query instead of copying it to clipboard.')
def generate_query(s1, s2, s3, product_list, print_):
    """ Generate a query based on the configuration. """

    if product_list is not None:
        try:
            with open(product_list, 'r') as f:
                products = [p.strip() for p in f.readlines() if p != '\n']
        except FileNotFoundError:
            click.secho('✗ ', fg='red', nl=False)
            click.echo(f'Cannot open {product_list} file. Terminating.')
            return

        query = ' OR '.join(products)

    else:
        if not (s1 or s2 or s3):
            params = config.get_config().get('Search')
            s1 = params.get('Sentinel-1') is not None
            s2 = params.get('Sentinel-2') is not None
            s3 = params.get('Sentinel-3') is not None

        try:
            query = api.generate_query(s1, s2, s3)
        except FileNotFoundError:
            click.secho('⚙ ', fg='red', nl=False)
            click.echo('Cannot load the configuration file. Terminating.')
            return

    if print_:
        click.echo(query)
        return
    else:
        pyperclip.copy(query)
        click.secho('✓ ', fg='green', nl=False)
        click.echo('Query copied to the clipboard.')

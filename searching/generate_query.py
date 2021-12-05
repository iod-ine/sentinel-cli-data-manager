""" `sdm generate-query` command generates and executes a query using configuration files. """

import click
import pyperclip

import searching.search_api as api


@click.command(name='generate-query')
@click.option('--s1', is_flag=True, help='Generate a query for Sentinel-1 products.')
@click.option('--s2', is_flag=True, help='Generate a query for Sentinel-2 products.')
@click.option('--s3', is_flag=True, help='Generate a query for Sentinel-3 products.')
@click.option('--print', 'print_', is_flag=True, help='Print the query instead of copying it to clipboard.')
def generate_query(s1, s2, s3, print_):
    """ Generate a query based on the configuration. """

    if not (s1 or s2 or s3):
        click.secho('✗ ', fg='red', nl=False)
        click.echo('No satellite flag specified for the query.')
        return

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

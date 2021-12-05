""" `sdm init` command manages the initialization of projects and configuration files. """

import click

import configuration.paths as paths
import configuration.database as db
import configuration.config as config
import configuration.workdir as workdir


@click.command()
@click.option('--generate-config', is_flag=True, help='Generate a new template configuration file.')
@click.option('--generate-database', is_flag=True, help='Generate a new metadata database.')
@click.option('--generate-geopackage', is_flag=True, help='Generate the metadata geopackage.')
@click.option('--clean', is_flag=True, help='Delete the configuration files and the metadata database.')
def init(generate_config, generate_database, generate_geopackage, clean):
    """ Initialize the current directory as an SDM project. """

    if clean:
        paths.config.unlink(missing_ok=True)
        paths.database.unlink(missing_ok=True)
        paths.geopackage.unlink(missing_ok=True)
        click.secho('⚙ ', fg='green', nl=False)
        click.echo('Cleaning up complete.')
        return

    workdir.initialize_working_directory()

    if generate_config or not paths.config.exists():
        config.generate_template_config()
        click.secho('⚙ ', fg='green', nl=False)
        click.echo('Generated a template configuration file.')
    else:
        click.secho('⚙ ', fg='yellow', nl=False)
        click.echo('Configuration file already exists.')

    if generate_geopackage or not paths.geopackage.exists():
        config.generate_metadata_geopackage()

        click.secho('⚙ ', fg='green', nl=False)
        click.echo('Generated a template metadata geopackage.')
    else:
        click.secho('⚙ ', fg='yellow', nl=False)
        click.echo('Metadata geopackage already exists.')

    if generate_database or not paths.database.exists():
        db.generate_metadata_database()

        click.secho('⚙ ', fg='green', nl=False)
        click.echo('Created the metadata database.')
    else:
        click.secho('⚙ ', fg='yellow', nl=False)
        click.echo('Metadata database already exists.')

    click.secho('⚙ ', fg='green', nl=False)
    click.echo('Ensured the working tree structure.')

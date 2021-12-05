""" Manage paths used throughout the app. """

import pathlib

working_directory = pathlib.Path().absolute()
name = working_directory.name.replace(' ', '_')

config = pathlib.Path('sdm-config.yaml')
database = pathlib.Path(f'sdm-metadata.sqlite3')
geopackage = working_directory / 'Data' / f'{name}-sdm.gpkg'
template_config = pathlib.Path('configuration/sdm-config-template.yaml')

raw_file_storage = pathlib.Path('Data/raw')
processed_file_storage = pathlib.Path('Data/proc')
quicklook_storage = pathlib.Path('Data/quicklooks')

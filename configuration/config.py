""" Handle the config file. """

import importlib.resources

import yaml
import geopandas as gpd

import configuration.paths as paths


def get_config():
    """ Get the configuration dictionary from the configuration file. """

    with open(paths.config, 'r') as f:
        config = yaml.full_load(f)

    return config


def generate_template_config():
    """ Generate a template configuration file. """

    template = importlib.resources.read_text(package='configuration', resource='sdm-config-template.yaml')

    with open(paths.config, 'w') as f:
        f.write(template)


def generate_metadata_geopackage():
    """ Generate a metadata geopackage. """

    roi = 'Polygon ((30.440 59.993, 30.023 59.993, 30.023 59.825, 30.440 59.825, 30.440 59.993))'
    d = {'geometry': gpd.GeoSeries.from_wkt([roi])}  # from_wkt() expects an array-like object
    gdf = gpd.GeoDataFrame(d, crs='EPSG:4326')

    gdf.to_file(paths.geopackage, driver='GPKG', layer='roi')

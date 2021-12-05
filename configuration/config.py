""" Handle the config file. """

import datetime
import importlib.resources

import yaml
import geopandas as gpd

import configuration.paths as paths


def get_config():
    """ Get the configuration dictionary from the configuration file. """

    with open(paths.config, 'r') as f:
        config = yaml.full_load(f)

    return config


def get_roi():
    """ Get the ROI WKT string to use in a query. """

    params = get_config().get('Search').get('ROI')

    if params.get('WKT') is not None:
        return params.get('WKT')

    if params.get('File') is not None:
        with open(params.get('File'), 'r') as f:
            return f.read().strip()

    if params.get('Geopackage') is not None:
        layer = params.get('Geopackage').get('Layer')
        gdf = gpd.read_file(paths.geopackage, layer=layer)
        return gdf.loc[0, 'geometry'].wkt

    raise ValueError


def get_dates():
    """ Get start and end dates to use in a query. """

    params = get_config().get('Search')

    start_date = params.get('Start date')
    end_date = params.get('End date')

    if end_date == 'today':
        end_date = datetime.datetime.now().date()

    return start_date, end_date


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

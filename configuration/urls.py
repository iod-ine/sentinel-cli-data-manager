""" Manage URLs. """


def get_search_url(eumetsat=False):
    """ Get the root OpenSearch URL. """

    return 'https://coda.eumetsat.int/search' if eumetsat else 'https://scihub.copernicus.eu/dhus/search'


def get_product_url(eumetsat=False):
    """ Get the generic URL for products.

     Notes:
         Use `url.format(id=id_)` to make the URL point to the specific product.
         Append $value to download the product instead of getting the metadata.

    """

    base_url = 'https://coda.eumetsat.int/odata/v1/' if eumetsat else 'https://scihub.copernicus.eu/dhus/odata/v1/'
    url = base_url + "Products('{id}')/"

    return url


def get_quicklook_url(eumetsat=False):
    """ Get the generic URL for quicklooks.

     Notes:
         Use `url.format(id=id_)` to make the URL point to the specific product.
         Append $value to download the quicklook instead of getting the metadata.

    """

    base_url = 'https://coda.eumetsat.int/odata/v1/' if eumetsat else 'https://scihub.copernicus.eu/dhus/odata/v1/'
    url = base_url + "Products('{id}')/Products('Quicklook')/"

    return url

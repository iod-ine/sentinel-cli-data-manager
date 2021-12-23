""" Handle API authentication. """

import os

import requests.auth

import configuration.config as config


def get_authentication(eumetsat=False):
    """ Get the authentication object to use in a request.

     Args:
         eumetsat (bool):

    Returns:
        An authentication object for a request; or
        None if couldn't get the authentication information.

     """

    conf = config.get_config()
    auth = conf.get('Authentication')

    if auth is None:
        return None

    if eumetsat:
        if auth.get('Environment') is not None:
            environment_var = auth.get('Environment').get('EUMETSAT environment variable')
            auth_str = os.environ.get(environment_var)
            if auth_str is None:
                return None
            else:
                user, password = auth_str.split(':')
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        if auth.get('Copernicus Open Data Access') is not None:
            coda = auth.get('Copernicus Open Data Access')
            user = coda.get('User')
            password = coda.get('Password')

            if user != '<your-eumetsat-username>' and password != '<your-eumetsat-password>':
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        if auth.get('File') is not None:
            file = auth.get('File').get('EUMETSAT file')

            if file != '<file-with-eumetsat-authentication>':
                try:
                    with open(file, 'r') as f:
                        auth_str = f.read()
                except FileNotFoundError:
                    return None
                user, password = auth_str.strip().split(':')
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        # at this point all options are exhausted
        return None
    else:
        if auth.get('Environment') is not None:
            environment_var = auth.get('Environment').get('Scihub environment variable')
            auth_str = os.environ.get(environment_var)
            if auth_str is None:
                return None
            else:
                user, password = auth_str.split(':')
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        if auth.get('Copernicus Open Access Hub') is not None:
            coah = auth.get('Copernicus Open Access Hub')
            user = coah.get('User')
            password = coah.get('Password')

            if user != '<your-scihub-username>' and password != '<your-scihub-password>':
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        if auth.get('File') is not None:
            file = auth.get('File').get('Scihub file')

            if file != '<file-with-scihub-authentication>':
                try:
                    with open(file, 'r') as f:
                        auth_str = f.read()
                except FileNotFoundError:
                    return None
                user, password = auth_str.strip().split(':')
                authentication = requests.auth.HTTPBasicAuth(user, password)
                return authentication

        # at this point all options are exhausted
        return None

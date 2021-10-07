#!/usr/bin/env python
"""
`htrc.volumes`

Contains the configuration parser object.
"""
from future import standard_library
standard_library.install_aliases()
from typing import Optional
from configparser import RawConfigParser as ConfigParser, NoSectionError
from codecs import open
import logging
import os.path
import shutil
import time

DEFAULT_PATH = os.path.expanduser('~')
DEFAULT_PATH = os.path.join(DEFAULT_PATH, '.htrc')
if not os.path.exists(DEFAULT_PATH):
    DEFAULT_FILE = os.path.dirname(__file__)
    DEFAULT_FILE = os.path.join(DEFAULT_FILE, '.htrc.default')
    logging.info("Copying default config file to home directory.")
    shutil.copyfile(DEFAULT_FILE, DEFAULT_PATH)


class HtrcDataApiConfig:
    def __init__(self,
                 token: Optional[str] = None,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 epr: Optional[str] = None,
                 cert: Optional[str] = None,
                 key: Optional[str] = None) -> None:
        super().__init__()

        self.token = token or get_jwt_token()
        self.host = host or get_dataapi_host()
        self.port = port or get_dataapi_port()
        self.epr = epr or get_dataapi_epr()
        self.cert = cert or get_dataapi_cert()
        self.key = key or get_dataapi_key()


def _get_value(section, key, path=None):
    if path is None:
        path = DEFAULT_PATH

    config = ConfigParser(allow_no_value=True)
    with open(path, encoding='utf8') as configfile:
        config.readfp(configfile)
    try:
        return config.get(section, key)
    except NoSectionError:
        raise EnvironmentError("Config not set for {} {} in {}".format(
            section, key, path))


def get_dataapi_port(path=None):
    port = int(_get_value('data', 'port', path))
    return (port)


def get_dataapi_host(path=None):
    host = _get_value('data', 'host', path)
    return (host)


def get_dataapi_epr(path=None):
    return _get_value('data', 'url', path)


def get_dataapi_cert(path=None):
    return _get_value('data', 'cert', path)


def get_dataapi_key(path=None):
    return _get_value('data', 'key', path)


def get_dataapi_access(path=None):
    return _get_value('data', 'pd_only', path)


def get_idp_host_port(path=None):
    host = _get_value('idp', 'host', path)
    port = _get_value('idp', 'port', path)

    return (host, port)


def get_idp_path(path=None):
    return _get_value('idp', 'url')


def get_idp_url(path=None):
    host, port = get_idp_host_port(path)
    path = get_idp_path(path)
    if port == 443:
        # On HTTPS Default Path
        return "https://{}{}".format(host, path)
    else:
        return "https://{}:{}{}".format(host, port, path)


# Add jwt credential access methods
def get_jwt_token(path=None):

    import htrc.auth
    token = htrc.auth.get_jwt_token()

    return token

def save_jwt_token(token, path=None):
    """
    Saves JWT token in the config file.
    """
    # Default to ~/.htrc
    if path is None:
        path = DEFAULT_PATH

    # Default to expiration of now - force a new token on next request
    #if expiration is None:
        #expiration = time.time()

    # Open and modify existing config file, if it exists.
    config = ConfigParser(allow_no_value=True)
    if os.path.exists(path):
        config.read(path)
    if not config.has_section('jwt'):
        config.add_section('jwt')

    # set token and expiration
    config.set('jwt', 'token', token)
    #config.set('jwt', 'expiration', expiration)

    with open(path, 'w') as credential_file:
        config.write(credential_file)

    return token


def remove_jwt_token(path=None):
    """
    Removes JWT token from the config file.
    """
    # Default to ~/.htrc
    if path is None:
        path = DEFAULT_PATH

    # Open and modify existing config file, if it exists.
    config = ConfigParser(allow_no_value=True)
    if os.path.exists(path):
        config.read(path)
    if not config.has_section('jwt'):
        config.add_section('jwt')
    # set token and expiration
    config.set('jwt', 'token', " ")
    #config.set('jwt', 'expiration', " ")

    with open(path, 'w') as credential_file:
        config.write(credential_file)


def get_credentials(path=None):
    """
    Retrieves the username and password from a config file for the Data API.
    Raises an EnvironmentError if not specified.
    See also: credential_prompt
    """
    client_id = _get_value('idp', 'client_id', path)
    client_secret = _get_value('idp', 'client_secret', path)

    if not client_id and not client_secret:
        logging.error("Config path: {}".format(path))
        raise EnvironmentError("No client_id and client_secret stored in config file.")

    return (client_id, client_secret)


def populate_parser(parser):
    return parser


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser = populate_parser(parser)
    parser.parse_args()


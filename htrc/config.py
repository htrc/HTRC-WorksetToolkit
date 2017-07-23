#!/usr/bin/env python
"""
`htrc.volumes`

Contains the configuration parser object.
"""
from future import standard_library
standard_library.install_aliases()
from builtins import input

from configparser import RawConfigParser as ConfigParser
import os.path

from htrc.lib.cli import bool_prompt

DEFAULT_PATH = os.path.expanduser('~')
DEFAULT_PATH = os.path.join(path, '.htrc')

def _get_value(section, key, path=None):
    if path is None:
        path = DEFAULT_PATH
    
    config = ConfigParser(allow_no_value=True)
    
def get_host_port(path=None):
    host = _get_value('data', 'host', path)
    port = _get_value('data', 'port', path)
    return (host, port)

def get_oauth2_url(path=None):
    return _get_value('oauth', 'token_url', path)

def get_oauth2_port(path=None):
    return _get_value('oauth', 'path', path)

def get_dataapi_epr(path=None):
    return _get_value('data', 'apiEPR', path)

def get_credentials(path=None):
    """
    Either retrieves credentials from existing config file or prompts user.
    Very convenient function for CLI applications.
    """
    if path is None:
        path = DEFAULT_PATH

    try:
        username, password = credentials_from_config(path)
    except EnvironmentError:
        username, password = credential_prompt(path)

    return username, password
    

def credential_prompt(save_path=None):
    """
    A prompt for entering HathiTrust credentials.
    """
    print("Please enter your HathiTrust credentials.")
    username = input("Token: ")
    password = input("Password: ")
    save = bool_prompt("Save credentials?", default=True)

    if save:
        save_credentials(username, password, save_path)

    return (username, password)

def save_credentials(username, password, save_path=None):
    """
    Saves credentials in the config file.
    """
    # Default to ~/.htrc
    if path is None:
        path = DEFAULT_PATH

    # Open and modify existing config file, if it exists.
    config = ConfigParser(allow_no_value=True)
    if os.path.exists(save_path):
        config.read(save_path)
    if not config.has_section('main'):
        config.add_section('main')
    config.set('main', 'username', username)
    config.set('main', 'password', password)
    with open(save_path, 'w') as credential_file:
        config.write(credential_file)

    return (username, password)

def credentials_from_config(path):
    """
    Retrieves the username and password from a config file for the Data API.
    Raises an EnvironmentError if not specified.
    See also: credential_prompt
    """
    username = None
    password = None

    config = ConfigParser(allow_no_value=True)
    if os.path.exists(path):
        config.read(path)
        if config.has_section('main'):
            username = config.get("main", "username")
            password = config.get("main", "password")

    if not username and not password:
        logging.error("Config path: {}".format(path))
        raise EnvironmentError("No username and password stored in config file.")

    return (username, password)

def populate_parser(parser):
    return parser

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser = populate_parser(parser)
    parser.parse_args()


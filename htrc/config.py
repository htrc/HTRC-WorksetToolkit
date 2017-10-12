#!/usr/bin/env python
"""
`htrc.volumes`

Contains the configuration parser object.
"""
from future import standard_library
standard_library.install_aliases()
from builtins import input

from configparser import RawConfigParser as ConfigParser, NoSectionError
from codecs import open
from getpass import getpass
import logging
import os.path
import shutil

from htrc.lib.cli import bool_prompt

DEFAULT_PATH = os.path.expanduser('~')
DEFAULT_PATH = os.path.join(DEFAULT_PATH, '.htrc')
if not os.path.exists(DEFAULT_PATH):
    DEFAULT_FILE = os.path.dirname(__file__)
    DEFAULT_FILE = os.path.join(DEFAULT_FILE, '.htrc.default')
    logging.info("Copying default config file to home directory.")
    shutil.copyfile(DEFAULT_FILE, DEFAULT_PATH)

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
    
def get_host_port(path=None):
    host = _get_value('data', 'host', path)
    port = int(_get_value('data', 'port', path))
    return (host, port)


def get_dataapi_epr(path=None):
    return _get_value('data', 'url', path)


def get_oauth2_url(path=None):
    return _get_value('oauth', 'url', path)


def get_oauth2_port(path=None):
    return _get_value('oauth', 'port', path)


def get_oauth2_host_port(path=None):
    host = _get_value('oauth', 'host', path)
    port = _get_value('oauth', 'port', path)
    return (host, port)


# Add jwt credential access methods
def get_jwt_token(path=None):
    if path is None:
        path = DEFAULT_PATH

    try:
        token = _get_value('jwt', 'token', path)
    except EnvironmentError:
        token = jwt_prompt(path)

    return token

def jwt_prompt(path=None):
    """
    A prompt for entering HathiTrust JWT tokens.
    """
    print("Please enter your HathiTrust JWT Token.")
    token = input("Token: ")
    save = bool_prompt("Save credentials?", default=True)

    if save:
        save_jwt_token(token, path)

    return token


def save_jwt_token(token, path=None):
    """
    Saves JWT token in the config file.
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
    config.set('jwt', 'token', token)
    with open(path, 'w') as credential_file:
        config.write(credential_file)

    return token


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
    

def credential_prompt(path=None):
    """
    A prompt for entering HathiTrust credentials.
    """
    print("Please enter your HathiTrust credentials.")
    username = input("Username: ")
    password = getpass("Password: ")
    save = bool_prompt("Save credentials?", default=True)

    if save:
        save_credentials(username, password, path)

    return (username, password)

def save_credentials(username, password, path=None):
    """
    Saves credentials in the config file.
    """
    # Default to ~/.htrc
    if path is None:
        path = DEFAULT_PATH

    # Open and modify existing config file, if it exists.
    config = ConfigParser(allow_no_value=True)
    if os.path.exists(path):
        config.read(path)
    if not config.has_section('main'):
        config.add_section('main')
    config.set('main', 'username', username)
    config.set('main', 'password', password)
    with open(path, 'w') as credential_file:
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


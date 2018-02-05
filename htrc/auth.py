from base64 import b64encode
from getpass import getpass
import http.client
import ssl
import time

import requests
import requests.auth

import htrc.config

def get_jwt_token():
    # Currently we just store one common jwt token locally at .htrc file for simplicity
    # Expect to add POST method to query unique jwt token with the combo of username and password
    username, password = credential_prompt()

    client_id, client_secret = htrc.config.get_credentials()

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = { "grant_type": "password",
             "username": username,
             "password": password,
             "scope" : "openid"}

    url = htrc.config.get_idp_url()
    r = requests.post(url, data=data, auth=auth)

    data = r.json()
    if 'error' not in data:
        expiration = int(time.time()) + data['expires_in']
        return data['id_token'], expiration
    elif data['error'] == 'invalid_grant':
        print("Invalid username or password. Please try again.\n")
        return get_jwt_token()
    else:
        raise RuntimeError("JWT token retrieval failed: {}".format(data['error']))

def credential_prompt():
    """
    A prompt for entering HathiTrust Research Center credentials.
    """
    print("Please enter your HathiTrust Research Center credentials.")
    username = input("HTRC Username: ")
    password = getpass("HTRC Password: ")

    if not username or not password:
        print("Invalid username or password. Please try again.\n")
        return credential_prompt()
    else:
        return (username, password)


if __name__ == '__main__':
    token, expiration = get_jwt_token()
    htrc.config.save_jwt_token(token, expiration)

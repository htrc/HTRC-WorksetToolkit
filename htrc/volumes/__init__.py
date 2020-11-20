#!/usr/bin/env python
"""
`htrc.volumes`

Contains functions to retrieve volumes from the HTRC Data API. 

The functions in this package will not operate unless they are 
executed from an HTRC Data Capsule in Secure Mode. The module 
`htrc.mock.volumes` contains Patch objects for testing workflows.
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from builtins import input

import http.client
from io import BytesIO  # used to stream http response into zipfile.
import json
import logging
import os.path
import progressbar
import re
import socket
import ssl
import sys
from time import sleep
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
import xml.etree.ElementTree as ET
from zipfile import ZipFile  # used to decompress requested zip archives.
from htrc.runningheaders import parse_page_structure
from htrc.hf_vol_load import load_vol
import pandas as pd
import fnmatch
import glob
from tqdm import tqdm
import shutil
from htrc.lib.cli import bool_prompt
from htrc.util import split_items
import htrc.config

import logging
from logging import NullHandler
logging.getLogger(__name__).addHandler(NullHandler())

def get_volumes(token, volume_ids, host, port, cert, key, epr, concat=False, mets=False):
    """
    Returns volumes from the Data API as a raw zip stream.

    Parameters:
    :token: An OAuth2 token for the app.
    :volume_ids: A list of volume_ids
    :concat: If True, return a single file per volume. If False, return a single
    file per page (default).
    :host: Data API host
    :port: Data API port
    """
    if not volume_ids:
        raise ValueError("volume_ids is empty.")

    url = epr + "volumes"

    for id in volume_ids:
        if ("." not in id
            or " " in id):
            print("Invalid volume id " + id + ". Please correct this volume id and try again.")

    data = {'volumeIDs': '|'.join(
        [id.replace('+', ':').replace('=', '/') for id in volume_ids])}
      
    if concat:
        data['concat'] = 'true'

    if mets:
        data['mets'] = 'true'

    # Authorization
    headers = {"Authorization": "Bearer " + token,
               "Content-type": "application/x-www-form-urlencoded"}

    # Create SSL lookup
    # TODO: Fix SSL cert verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Retrieve the volumes
    httpsConnection = http.client.HTTPSConnection(host, port, context=ctx, key_file=key, cert_file=cert)


    httpsConnection.request("POST", url, urlencode(data), headers)

    response = httpsConnection.getresponse()

    if response.status is 200:
        body = True
        data = BytesIO()
        bytes_downloaded = 0
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength,
            widgets=[progressbar.AnimatedMarker(), '    ',
                     progressbar.DataSize(),
                     ' (', progressbar.FileTransferSpeed(), ')'])

        while body:
            body = response.read(128)
            data.write(body)
            bytes_downloaded += len(body)
            bar.update(bytes_downloaded)

        data = data.getvalue()
    else:
        logging.debug("Unable to get volumes")
        logging.debug("Response Code: {}".format(response.status))
        logging.debug("Response: {}".format(response.reason))
        raise EnvironmentError("Unable to get volumes.")

    if httpsConnection is not None:
        httpsConnection.close()

    return data


def get_pages(token, page_ids, host, port, cert, key, epr, concat=False, mets=False):
    """
    Returns a ZIP file containing specfic pages.

    Parameters:
    :token: An OAuth2 token for the app.
    :volume_ids: A list of volume_ids
    :concat: If True, return a single file per volume. If False, return a single
    file per page (default).
    """
    if not page_ids:
        raise ValueError("page_ids is empty.")

    url = epr + "pages"

    for id in page_ids:
        if ("." not in id
            or " " in id):
            print("Invalid volume id " + id + ". Please correct this volume id and try again.")

    data = {'pageIDs': '|'.join(
        [id.replace('+', ':').replace('=', '/') for id in page_ids])}

    if concat and mets:
        print("Cannot set both concat and mets with pages.")
    elif concat:
        data['concat'] = 'true'
    elif mets:
        data['mets'] = 'true'

    # Authorization
    headers = {"Authorization": "Bearer " + token,
               "Content-type": "application/x-www-form-urlencoded"}


    # Create SSL lookup
    # TODO: Fix SSL cert verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Retrieve the volumes
    httpsConnection = http.client.HTTPSConnection(host, port, context=ctx, key_file=key, cert_file=cert)


    httpsConnection.request("POST", url, urlencode(data), headers)

    response = httpsConnection.getresponse()

    if response.status is 200:
        body = True
        data = BytesIO()
        bytes_downloaded = 0
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength,
              widgets=[progressbar.AnimatedMarker(), '    ',
                                               progressbar.DataSize(),
                                               ' (', progressbar.FileTransferSpeed(), ')'])

        while body:
            body = response.read(128)
            data.write(body)
            bytes_downloaded += len(body)
            bar.update(bytes_downloaded)

        data = data.getvalue()
    else:
        logging.debug("Unable to get pages")
        logging.debug("Response Code: ".format(response.status))
        logging.debug("Response: ".format(response.reason))
        raise EnvironmentError("Unable to get pages.")

    if httpsConnection is not None:
        httpsConnection.close()

    return data

def get_oauth2_token(username, password):
    # make sure to set the request content-type as application/x-www-form-urlencoded
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    data = { "grant_type": "client_credentials",
             "client_secret": password,
             "client_id": username }
    data = urlencode(data)

    # create an SSL context
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # make sure the request method is POST
    host, port = htrc.config.get_oauth2_host_port()
    oauth2port = htrc.config.get_oauth2_port()
    oauth2EPRurl = htrc.config.get_oauth2_url()
    httpsConnection = http.client.HTTPSConnection(host, oauth2port, context=ctx)
    httpsConnection.request("POST", oauth2EPRurl + "?" + data, "", headers)

    response = httpsConnection.getresponse()

    # if response status is OK
    if response.status == 200:
        data = response.read().decode('utf8')

        jsonData = json.loads(data)
        logging.info("*** JSON: {}".format(jsonData))

        token = jsonData["access_token"]
        logging.info("*** parsed token: {}".format(token))

    else:
        logging.debug("Unable to get token")
        logging.debug("Response Code: {}".format(response.status))
        logging.debug("Response: {}".format(response.reason))
        logging.debug(response.read())
        raise EnvironmentError("Unable to get token.")

    if httpsConnection is not None:
        httpsConnection.close()

    return token

def grep(file_name, output_dir, pattern):
    na_volume = []
    for line in open(file_name):
        if pattern in line:
            na_volume.append(line.split()[-1])
    if len(na_volume) < 100:
        print("\nFollowing volume ids are not available.")
        print("\n".join(str(item) for item in na_volume))
        with open(os.path.join(output_dir, "volume_not_available.txt"), "w") as volume_na:
            volume_na.write("\n".join(str(item) for item in na_volume))
    else:
        if len(na_volume) == 100:
            print("\nThere are 100 or more unavailable volumes.\nTo check the validity of volumes in your workset or volume id file go to:\n https://analytics.hathitrust.org/validateworkset \n or email us at htrc-help@hathitrust.org for assistance.")

def check_error_file(output_dir):
    file_name = "ERROR.err"

    if output_dir.endswith("/"):
        file_path = output_dir+ file_name
    else:
        file_path = output_dir+"/"+file_name

    if os.path.isfile(file_path):
        grep(file_path, output_dir, "KeyNotFoundException")

def remove_hf(output_dir):
    os.makedirs(os.path.join(output_dir, "removed_hf_files"), exist_ok = True)
    removed_hf = os.path.join(output_dir, "removed_hf_files")
    vol_paths = glob.glob(os.path.join(output_dir,'**'))
    df = pd.DataFrame()
    

    for path in tqdm(vol_paths):
        if os.path.isdir(path):
            page_paths = sorted(glob.glob(os.path.join(path, '**', '*.txt'), recursive=True))
            n = len(page_paths)
            num = 1
    
            while num <= n:
                for pg in page_paths:
                    parsed_path = str(path).split('/')
                    clean_path_root = '/'.join(parsed_path)
                    page_num = str(num).zfill(8)
                    new_filename = page_num+'.txt'
                    os.rename(pg, clean_path_root+'/'+new_filename)
                    num += 1
    
            folder = os.path.basename(path)
            n_pgs = len(fnmatch.filter(os.listdir(path), "*.txt"))
            pages = parse_page_structure(load_vol(path, num_pages=n_pgs))
    
            body = []
            for n, page in enumerate(pages):
                s = "\nPage {} (has_header: {}, has_body: {}, has_footer: {})".format(n+1, page.has_header, page.has_body, page.has_footer)
    
                pg_boolean = s + "\n" + "-"*len(s)
                pg_header = "Header:\n{}".format(page.header if page.has_header else "N/A")
                #pg_body = page.body if page.has_body else ""
                pg_footer = "Footer:\n{}".format(page.footer if page.has_footer else "N/A")
                
                body.append(page.body)
                
                df = df.append({"Volume":folder, "Page Info":pg_boolean, "Header":pg_header, "Footer":pg_footer}, ignore_index = True)
                df.sort_values("Volume")
                for i, g in df.groupby("Volume"):
                    g.to_csv(os.path.join(removed_hf, "removed_hf_data_{}.csv".format(i)))
            
                count = 1
                for item in body:
                    pg_n = str(count).zfill(8)
                    filename = '{}.txt'.format(pg_n)
                    count += 1
                    with open(os.path.join(clean_path_root, filename), "w") as f_out:
                        f_out.write('{}\n'.format(item))

def remove_hf_concat(output_dir):
    os.makedirs(os.path.join(output_dir, "removed_hf_files"), exist_ok = True)
    removed_hf = os.path.join(output_dir, "removed_hf_files")
    vol_paths = glob.glob(os.path.join(output_dir,'**'))
    df = pd.DataFrame()
    retain = ["removed_hf_files"]
    

    for path in tqdm(vol_paths):
        if os.path.isdir(path):
            page_paths = sorted(glob.glob(os.path.join(path, '**', '*.txt'), recursive=True))
            n = len(page_paths)
            num = 1
    
            while num <= n:
                for pg in page_paths:
                    parsed_path = str(path).split('/')
                    clean_path_root = '/'.join(parsed_path)
                    page_num = str(num).zfill(8)
                    new_filename = page_num+'.txt'
                    os.rename(pg, clean_path_root+'/'+new_filename)
                    num += 1
    
            folder = os.path.basename(path)
            n_pgs = len(fnmatch.filter(os.listdir(path), "*.txt"))
            pages = parse_page_structure(load_vol(path, num_pages=n_pgs))
                
            filename = '{}.txt'.format(folder)
            body = []
            for n, page in enumerate(pages):
                s = "\nPage {} (has_header: {}, has_body: {}, has_footer: {})".format(n+1, page.has_header, page.has_body, page.has_footer)
    
                pg_boolean = s + "\n" + "-"*len(s)
                pg_header = "Header:\n{}".format(page.header if page.has_header else "N/A")
                #pg_body = page.body if page.has_body else ""
                pg_footer = "Footer:\n{}".format(page.footer if page.has_footer else "N/A")
                
                body.append(page.body)
                
                df = df.append({"Volume":folder, "Page Info":pg_boolean, "Header":pg_header, "Footer":pg_footer}, ignore_index = True)
                df.sort_values("Volume")
                for i, g in df.groupby("Volume"):
                    g.to_csv(os.path.join(removed_hf, "removed_hf_data_{}.csv".format(i)))
            
                    
            with open(os.path.join(output_dir, filename), "w") as f_out:
                f_out.write('\n'.join([str(item) + '\n' for item in body]) + '\n')
            if folder not in retain:
                shutil.rmtree(os.path.join(output_dir, folder))

def download_volumes(volume_ids, output_dir, username=None, password=None,
                     config_path=None, token=None, headfootcon=False, headfoot=False, concat=False, mets=False, pages=False, host=None, port=None, cert=None, key=None, epr=None):
    # create output_dir folder, if nonexistant
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # get token if not specified
    if not token:
        token = htrc.config.get_jwt_token()
        htrc.config.remove_jwt_token()

    if not host:
        host= htrc.config.get_dataapi_host()

    if not port:
        port = htrc.config.get_dataapi_port()

    if not epr:
        epr = htrc.config.get_dataapi_epr()

    if not cert:
        cert = htrc.config.get_dataapi_cert()

    if not key:
        key = htrc.config.get_dataapi_key()

    if any((token, host, port)) is not None:
        logging.info("obtained token: %s\n" % token)

        try:
            for ids in split_items(volume_ids, 250):
                if pages:
                    if concat & mets:
                        raise ValueError("Cannot set both concat and mets with pages.")
                    else:
                        data = get_pages(token, ids, host, port, cert, key, epr, concat, mets)
                else:
                    data = get_volumes(token, ids, host, port, cert, key, epr, concat, mets)

                myzip = ZipFile(BytesIO(data))
                myzip.extractall(output_dir)
                myzip.close()

                check_error_file(output_dir)
                d = os.listdir(output_dir)
                if headfoot:
                    if len(d) == 0:
                        print("This directory is empty")
                        sys.exit(1)
                    else:
                        remove_hf(output_dir)
                if headfootcon:
                    if len(d) == 0:
                        print("This directory is empty")
                        sys.exit(1)
                    else:
                        remove_hf_concat(output_dir)
                
        except socket.error:
            raise RuntimeError("Data API request timeout. Is your Data Capsule in Secure Mode?")

    else:
        raise RuntimeError("Failed to obtain jwt token.")


def download(args):
    # extract files
    with open(args.file) as IDfile:
        volumeIDs = [line.strip() for line in IDfile]

    return download_volumes(volumeIDs, args.output,
        username=args.username, password=args.password,
        token=args.token, headfoot=args.headfoot, headfootcon=args.headfootcon, concat=args.concat, mets=args.mets, pages=args.pages, host=args.datahost,
        port=args.dataport, cert=args.datacert, key=args.datakey,
        epr=args.dataepr)


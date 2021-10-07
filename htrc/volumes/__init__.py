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

#from builtins import input
from htrc.models import HtrcPage

import http.client
from io import BytesIO, TextIOWrapper
import json
import logging
import os.path
import progressbar
#import re
import socket
import ssl
#import sys
#from time import sleep
#from urllib.request import urlopen
#from urllib.error import HTTPError
from urllib.parse import urlencode
#import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from zipfile import ZipFile  # used to decompress requested zip archives.
from tqdm import tqdm
from htrc.runningheaders import parse_page_structure
from functools import partial
import pandas as pd

#from htrc.lib.cli import bool_prompt
from htrc.util import split_items
import htrc.config
import multiprocessing

import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())


def get_volumes(data_api_config: htrc.config.HtrcDataApiConfig, volume_ids, concat=False, mets=False, buffer_size=128):
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

    url = data_api_config.epr + "volumes"

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
    headers = {"Authorization": "Bearer " + data_api_config.token,
               "Content-type": "application/x-www-form-urlencoded"}

    # Create SSL lookup
    # TODO: Fix SSL cert verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE

    # Retrieve the volumes
    httpsConnection = http.client.HTTPSConnection(
        data_api_config.host,
        data_api_config.port,
        context=ctx,
        key_file=data_api_config.key,
        cert_file=data_api_config.cert)

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
            body = response.read(buffer_size)
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


def get_pages(data_api_config: htrc.config.HtrcDataApiConfig, page_ids, concat=False, mets=False, buffer_size=128):
    """
    Returns a ZIP file containing specfic pages.

    Parameters:
    :data_api_config: The configuration data of the DataAPI endpoint.
    :volume_ids: A list of volume_ids
    :concat: If True, return a single file per volume. If False, return a single
    file per page (default).
    """
    if not page_ids:
        raise ValueError("page_ids is empty.")

    url = data_api_config.epr + "pages"

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
    headers = {"Authorization": "Bearer " + data_api_config.token,
               "Content-type": "application/x-www-form-urlencoded"}

    # Create SSL lookup
    # TODO: Fix SSL cert verification
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE

    # Retrieve the volumes
    httpsConnection = http.client.HTTPSConnection(
        data_api_config.host,
        data_api_config.port,
        context=ctx,
        key_file=data_api_config.key,
        cert_file=data_api_config.cert
    )

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
            body = response.read(buffer_size)
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

#def get_oauth2_token(username, password):
    # make sure to set the request content-type as application/x-www-form-urlencoded
    #headers = {"Content-type": "application/x-www-form-urlencoded"}
    #data = { "grant_type": "client_credentials",
             #"client_secret": password,
             #"client_id": username }
    #data = urlencode(data)

    # create an SSL context
    #ctx = ssl.create_default_context()
    #ctx.check_hostname = False
    #ctx.verify_mode = ssl.CERT_NONE

    # make sure the request method is POST
    #host, port = htrc.config.get_oauth2_host_port()
    #oauth2port = htrc.config.get_oauth2_port()
    #oauth2EPRurl = htrc.config.get_oauth2_url()
    #httpsConnection = http.client.HTTPSConnection(host, oauth2port, context=ctx)
    #httpsConnection.request("POST", oauth2EPRurl + "?" + data, "", headers)

    #response = httpsConnection.getresponse()

    # if response status is OK
    #if response.status == 200:
        #data = response.read().decode('utf8')

        #jsonData = json.loads(data)
        #logging.info("*** JSON: {}".format(jsonData))

        #token = jsonData["access_token"]
        #logging.info("*** parsed token: {}".format(token))

    #else:
        #logging.debug("Unable to get token")
        #logging.debug("Response Code: {}".format(response.status))
        #logging.debug("Response: {}".format(response.reason))
        #logging.debug(response.read())
        #raise EnvironmentError("Unable to get token.")

    #if httpsConnection is not None:
        #httpsConnection.close()

    #return token


def grep_error(file_name, output_dir, pattern, txt_index):
    na_volume = []
    if output_dir.endswith("/"):
        file_path = output_dir + file_name
    else:
        file_path = output_dir + "/" + file_name

    if os.path.isfile(file_path):
        for line in open(file_path):
            if pattern in line:
                na_volume.append(line.split()[txt_index])

    return na_volume


def _to_htrc_page(page_file, zip):
    with TextIOWrapper(BytesIO(zip.read(page_file)), encoding='utf-8') as page:
        return HtrcPage([line.rstrip() for line in page.readlines()])


def download_volumes(volume_ids, output_dir, concat=False, mets=False, pages=False,
                     remove_headers_footers=False, hf_window_size=6, hf_min_similarity=0.7, skip_removed_hf=False,
                     parallelism=multiprocessing.cpu_count(), batch_size=250, data_api_config=None):
    if not 0 < parallelism <= multiprocessing.cpu_count():
        raise ValueError("Invalid parallelism level specified")

    remove_hf_fun = partial(
        _remove_headers_footers_and_save,
        concat=concat,
        hf_min_similarity=hf_min_similarity,
        hf_window_size=hf_window_size,
        skip_removed_hf=skip_removed_hf,
        output_dir=output_dir
    )

    volume_ids = list(set(volume_ids))  # ensure unique volume ids
    num_vols = len(volume_ids)

    data_api_config = data_api_config or htrc.config.HtrcDataApiConfig()

    os.makedirs(output_dir, exist_ok=True)

    if any((data_api_config.token, data_api_config.host, data_api_config.port)) is not None:
        logging.info("obtained token: %s\n" % data_api_config.token)

        try:
            errors = []
            rights = []

            with tqdm(total=num_vols) as progress, multiprocessing.Pool(processes=parallelism) as pool:
                for ids in split_items(volume_ids, batch_size):
                    if pages:
                        if concat and mets:
                            raise ValueError("Cannot set both concat and mets with pages.")
                        else:
                            data = get_pages(data_api_config, ids, concat and not remove_headers_footers, mets)
                    else:
                        data = get_volumes(data_api_config, ids, concat and not remove_headers_footers, mets)

                    volumes = []

                    with ZipFile(BytesIO(data)) as vols_zip:
                        zip_list = vols_zip.namelist()
                        if 'ERROR.err' in zip_list:
                            errors.append(vols_zip.read('ERROR.err').decode('utf-8'))
                            zip_list.remove('ERROR.err')
                        if 'volume-rights.txt' in zip_list:
                            rights_data = vols_zip.read('volume-rights.txt').decode('utf-8')
                            zip_list.remove('volume-rights.txt')
                            if not rights:
                                rights.append(rights_data)
                            else:
                                # due to the format in which 'volume-rights.txt' is created, we have to skip
                                # the first 4 lines which make up the header of the file, to extract only the
                                # actual volume rights data for accumulation
                                rights.append(''.join(rights_data.splitlines(keepends=True)[4:]))

                        zip_volume_paths = [zip_vol_path for zip_vol_path in zip_list if zip_vol_path.endswith('/')]
                        num_vols_in_zip = len(zip_volume_paths)

                        if not remove_headers_footers:
                            vols_zip.extractall(output_dir, members=zip_list)
                            progress.update(num_vols_in_zip)
                        else:
                            for zip_vol_path in zip_volume_paths:
                                sorted_vol_zip_page_paths = sorted(zip_page_path for zip_page_path in zip_list if zip_page_path.startswith(zip_vol_path) and not zip_page_path.endswith('/'))
                                vol_pages = [_to_htrc_page(page_path, vols_zip) for page_path in sorted_vol_zip_page_paths]
                                volumes.append((zip_vol_path, sorted_vol_zip_page_paths, vol_pages))

                    del data, vols_zip

                    num_missing = batch_size - num_vols_in_zip if num_vols >= batch_size else num_vols - num_vols_in_zip
                    progress.update(num_missing)  # update progress bar state to include the missing volumes also

                    # `volumes` will be empty if `remove_headers_footers=False` since the ZIP was extracted
                    # without further processing
                    if volumes:
                        for _ in pool.imap_unordered(remove_hf_fun, volumes):
                            progress.update()

            na_volumes_all = []

            if errors:
                with open(os.path.join(output_dir, 'ERROR.err'), 'w') as err_file:
                    err_file.write(''.join(errors))

                na_volumes_error = grep_error('ERROR.err', output_dir, 'KeyNotFoundException', -1)
                na_volumes_all.extend(na_volumes_error)

            if rights:
                with open(os.path.join(output_dir, 'volume-rights.txt'), 'w') as rights_file:
                    rights_file.write(''.join(rights))

                if htrc.config.get_dataapi_access() == "true":
                    na_volumes_rights = grep_error('volume-rights.txt', output_dir, ' 3', 0)
                    na_volumes_all.extend(na_volumes_rights)

            num_na = len(na_volumes_all)

            if num_na > 0:
                with open(os.path.join(output_dir, 'volumes_not_available.txt'), 'w') as volumes_na:
                    volumes_na.write("\n".join(str(item) for item in na_volumes_all))

                if num_na < 100:
                    print("\nThe following volume ids are not available. \n Please check volumes_not_available.txt "
                          "for the complete list. ")
                    print('\n'.join(str(item) for item in na_volumes_all))
                else:
                    print("\nThere are {:,} unavailable volumes.\n Please check volumes_not_available.txt "
                          "for the "
                          "complete list. \nTo check the validity of volumes in your workset or volume id file go "
                          "to:\n "
                          "https://analytics.hathitrust.org/validateworkset \n or email us at "
                          "htrc-help@hathitrust.org "
                          "for assistance.".format(num_na))

        except socket.error:
            raise RuntimeError("HTRC Data API time out. Check your inode usage if downloading a large workset. "
                               "Contact HTRC for further help.")

    else:
        raise RuntimeError("Failed to obtain the JWT token.")


def _remove_headers_footers_and_save(vol_data, concat, hf_min_similarity, hf_window_size, skip_removed_hf, output_dir):
    zip_vol_path, sorted_vol_zip_page_paths, vol_pages = vol_data
    clean_volid = zip_vol_path[:-1]

    vol_pages = parse_page_structure(vol_pages, window_size=hf_window_size, min_similarity_ratio=hf_min_similarity)
    pages_body = (page.body for page in vol_pages)
    # save the removed headers/footers for user inspection
    if skip_removed_hf:
        if concat:
            with open(os.path.join(output_dir, clean_volid + '.txt'), 'w', encoding='utf-8') as vol_file:
                vol_file.write('\n'.join(pages_body))
        else:
            vol_path = os.path.join(output_dir, zip_vol_path)
            os.mkdir(vol_path)
            for vol_page_path, page_body in zip(sorted_vol_zip_page_paths, pages_body):
                with open(os.path.join(output_dir, vol_page_path), 'w', encoding='utf-8') as page_file:
                    page_file.write(page_body)
    else:
        if concat:
            with open(os.path.join(output_dir, clean_volid + '.txt'), 'w', encoding='utf-8') as vol_file:
                vol_file.write('\n'.join(pages_body))
        else:
            vol_path = os.path.join(output_dir, zip_vol_path)
            os.mkdir(vol_path)
            for vol_page_path, page_body in zip(sorted_vol_zip_page_paths, pages_body):
                with open(os.path.join(output_dir, vol_page_path), 'w', encoding='utf-8') as page_file:
                    page_file.write(page_body)

        removed_hf = []
        for vol_page_path, vol_page in zip(sorted_vol_zip_page_paths, vol_pages):
            if not (vol_page.has_header or vol_page.has_footer):
                # skip reporting pages that don't have an identified header or footer
                continue
            _, page_name = os.path.split(vol_page_path)
            page_name, _ = os.path.splitext(page_name)
            removed_hf.append({'page': page_name, 'header': vol_page.header, 'footer': vol_page.footer})

        if concat:
            removed_hf_filename = os.path.join(output_dir, clean_volid + '_removed_hf.csv')
        else:
            removed_hf_filename = os.path.join(output_dir, clean_volid, 'removed_hf.csv')

        pd.DataFrame(removed_hf, columns=['page', 'header', 'footer']).to_csv(removed_hf_filename, index=False)


def download(args):
    # extract files
    with open(args.file) as IDfile:
        volumeIDs = [line.strip() for line in IDfile]

    data_api_config = htrc.config.HtrcDataApiConfig(
        token=args.token,
        host=args.datahost,
        port=args.dataport,
        epr=args.dataepr,
        cert=args.datacert,
        key=args.datakey
    )

    return download_volumes(volumeIDs, args.output,
                            remove_headers_footers=args.remove_headers_footers or args.remove_headers_footers_and_concat,
                            concat=args.concat or args.remove_headers_footers_and_concat,
                            mets=args.mets,
                            pages=args.pages,
                            hf_window_size=args.window_size,
                            hf_min_similarity=args.min_similarity_ratio,
                            parallelism=args.parallelism,
                            batch_size=args.batch_size,
                            skip_removed_hf=args.skip_removed_hf,
                            data_api_config=data_api_config)


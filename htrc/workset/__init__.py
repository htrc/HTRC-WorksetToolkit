"""
`htrc.workset`

Contains function to extract all volume IDs from a JSON-LD workset 
representation.

Will eventually be expanded to allow for querying based on arbitrary
ID and for update and removal of volumes from Workset.
"""
from __future__ import absolute_import, print_function
from future import standard_library
standard_library.install_aliases()

import unicodecsv as csv
from io import BytesIO
import json
from pprint import pprint
import re
from urllib.request import urlopen
from urllib.parse import urlparse

from pyld import jsonld

def get_volumes(data):
    """
    Takes a data structure in the canonical HathiTrust JSON-LD format
    and expands the dataset. Traverses the edm:gathers relation to find
    all HT volume IDs.
    
    Returns a list of volume IDs for use with the `htrc.metadata` and
    `htrc.volume` modules.
    """

    # Remove all namespaces to ensure proper referencing
    data = jsonld.expand(data)

    # Build up the list of volumes. Because the JSON-LD `@graph` may
    # contain multiple worksets, this code uses a set representation
    # to ensure that duplicates are removed
    volumes = set()
    for obj in data:
        # retrieve list of entities gathered
        gathers = obj.get('http://www.europeana.eu/schemas/edm/gathers', [])
        gathers = [vol['@id'].replace('http://hdl.handle.net/2027/','') 
                      for vol in gathers]

        # Check if `gathers` has any elements to ensure we don't add []
        # to the list of volumes.
        if gathers:
            volumes.update(gathers)

    # return the list representation, maintains a more consistent interface
    return list(volumes)


def load(filename):
    """
    Takes a filename and retrieves a list of volumes from the workset
    description. If a URL is passed, automatically uses `load_url` to resolve.
    """
    if filename.startswith('http://') or filename.startswith('https://'):
        return load_url(filename)

    with open(filename) as infile:
        data = json.load(infile)

    # Retrieve and print the volumes
    return get_volumes(data)


def load_url(url):
    """
    Takes a workset URL, parses it, and uses the workset retrieval API to fetch
    the data and return the volumes..
    """
    url_components = urlparse(url)
    if url_components.netloc.startswith('babel.hathitrust.org'):
        return load_hathitrust_collection(url)
    elif (url_components.netloc.startswith('htrc.hathitrust.org')
        and url_components.path.startswith('/wsid/')):
        base_url = 'http://acbres224.ischool.illinois.edu:8080'
        base_url += '/dcWSfetch/getDescription?id='
        base_url += url
        url = base_url
    elif (url_components.netloc.startswith('acbres224.ischool.illinois.edu')
        and url_components.path.startswith('/dcWSfetch/')):
        # copied from direct call to WS fetch, a-ok.
        pass
    else:
        raise ValueError("Invalid workset URL: {}".format(url))

    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))

    return get_volumes(data)


def get_volumes_from_csv(data):
    """
    Retrieves the volume list for a given HathiTrust collection.
    """

    csvfile = BytesIO(data)
    reader = csv.DictReader(csvfile, delimiter='\t')
    volumes = [row['htitem_id'] for row in reader] 
    csvfile.close()

    return volumes 


def load_hathitrust_collection(url):
    """
    Retrieves the volume list for a given HathiTrust Collection URL.
    In contrast to `get_volumes_csv`, which makes the request and handles data,
    this function parses out the collection ID from a variety of canonical URL
    schemes for collections:
    - https://babel.hathitrust.org/shcgi/mb?a=listis;c=548413090
    - https://babel.hathitrust.org/cgi/mb?a=listis&c=548413090
    """
    if not url.startswith('https://babel.hathitrust.org/'):
        raise ValueError('Invalid HathiTrust Collection URL: {}'.format(url))
    try:
        collection_id = re.search('c=(\d+)', url).group(1)
    except AttributeError:
        raise ValueError('Invalid HathiTrust Collection URL: {}'.format(url))
    
    url = "https://babel.hathitrust.org/shcgi/mb"
    data = "a=download&c={}&format=text".format(collection_id)

    response = urlopen(url, bytes(data.encode('utf-8')))
    data = response.read()

    return get_volumes_from_csv(data)


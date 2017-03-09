from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str

import codecs
import json
import os, os.path
import re
from time import sleep
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
import xml.etree.ElementTree as ET

import requests

def metadata(id, marc=False):
    """
    Retrieve item metadata `from the HathiTrust Bibliographic API`_.

    Params:
    :param id: HTID for the volume to be retrieved
    :param marc: Retrieve MARC-XML within JSON return value.

    _ https://www.hathitrust.org/bib_api
    """
    biblio_api = "https://catalog.hathitrust.org/api/volumes"
    
    if marc:
        biblio_api += '/full'
    else:
        biblio_api += '/brief'

    url = biblio_api + '/htid/{}.json'.format(id)

    try:
        reader = codecs.getreader('utf-8')
        data = json.load(reader(urlopen(url)))
        if len(data['records']) == 1 and len(data['items']) == 1:
            md = data['records'].values()[0]
            md.update(data['items'][0])
        return md
    except (ValueError, IndexError, HTTPError):
        logging.error("No result found for " + id)
        return dict()
        



def solr_metadata(id, sleep_time=0.1):
    solr = "http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:%s" % id
    solr += "&wt=json"  # retrieve JSON results
    if sleep_time:
        sleep(sleep_time)  # JUST TO MAKE SURE WE ARE THROTTLED
    try:
        reader = codecs.getreader('utf-8')
        data = json.load(reader(urlopen(solr)))
        return data['response']['docs'][0]
    except (ValueError, IndexError, HTTPError):
        logging.error("No result found for " + id)
        return dict()


def get_metadata(folder):
    ids = os.listdir(folder)
    data = [(id.strip(), metadata(id.strip())) for id in ids
            if not id.endswith('.log')]
    data = dict(data)
    with open(os.path.join(folder, '../metadata.json'), 'w') as outfile:
        json.dump(data, outfile)


def record_data(id, sleep_time=1):
    regex = re.compile('\W')
    url = "http://catalog.hathitrust.org/api/volumes/brief/recordnumber/{0}.json"

    url = url.format(id)
    r = requests.get(url)
    data = r.json()

    # data = data['items'][id]
    items = []
    if data:
        for item in data['items']:
            enum = regex.sub('', str(item.get('enumcron', '')).lower())
            htid = item.get('htid', '')
            items.append((enum, htid))
    else:
        items = []

    sleep(sleep_time)
    return items


"""
MARC CODE HANDLING
"""


def parse_marc(raw):
    # lazy workaround
    raw = raw.replace(' xmlns', ' xmlnamespace')
    ET.register_namespace('', 'http://www.loc.gov/MARC21/slim')
    return ET.fromstring(raw)


def get_marc_value(xml, tag, code):
    xpath = "{marc}datafield[@tag='{tag}']/{marc}subfield[@code='{code}']".format(
        tag=tag, code=code, marc='')  # marc="{http://www.loc.gov/MARC21/slim}")
    results = xml.findall(xpath)
    return results[0].text if results else None


def get_lccn_from_marc(xml):
    return get_marc_value(xml, '010', 'a')


def get_title_from_marc(xml):
    return get_marc_value(xml, '245', 'a')


def get_volume_from_marc(xml):
    return get_marc_value(xml, '974', 'c')


def get_lcc_from_marc(xml):
    # MARC tag 050a/b or 991h/i
    lcc = list()
    val = get_marc_value(xml, '050', 'a')
    if val:
        lcc.append(val)

    val = get_marc_value(xml, '050', 'b')
    if val:
        lcc[-1] += val

    val = get_marc_value(xml, '991', 'h')
    if val:
        lcc.append(val)

    val = get_marc_value(xml, '991', 'i')
    if val:
        lcc[-1] += val

    return ";".join(lcc)



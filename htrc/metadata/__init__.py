import json
import os, os.path
import re
from time import sleep
from urllib2 import urlopen, HTTPError
from urllib import quote_plus, urlencode
import xml.etree.ElementTree as ET

import requests


def metadata(id, sleep_time=1):
    solr = "http://chinkapin.pti.indiana.edu:9994/solr/meta/select/?q=id:%s" % id
    solr += "&wt=json"  # retrieve JSON results
    # TODO: exception handling
    if sleep_time:
        sleep(sleep_time)  # JUST TO MAKE SURE WE ARE THROTTLED
    try:
        data = json.load(urlopen(solr))
        print id
        return data['response']['docs'][0]
    except (ValueError, IndexError, HTTPError):
        print "No result found for " + id
        return dict()


def get_metadata(folder):
    ids = os.listdir(folder)
    data = [(id.strip(), metadata(id.strip())) for id in ids
            if not id.endswith('.log')]
    data = dict(data)
    with open(os.path.join(folder, '../metadata.json'), 'wb') as outfile:
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



"""
MARC CODE HANDLING
"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str

import xml.etree.ElementTree as ET


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



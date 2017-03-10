from future import standard_library
standard_library.install_aliases()
import json
import re
from pprint import pprint
from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs

# List of organization codes in HathiTrust Digital Library
# Derived from https://github.com/Bookworm-project/Bookworm-MARC/issues/1
# More info on HT codes at:  
ORG_CODES = {
    "mdp" : "University of Michigan",
    "miua" : "University of Michigan",
    "miun" : "University of Michigan",
    "wu" : "University of Wisconsin",
    "inu" : "Indiana University",
    "uc1" : "University of California",
    "uc2" : "University of California",
    "pst" : "Penn State University",
    "umn" : "University of Minnesota",
    "nnc1" : "Columbia University",
    "nnc2" : "Columbia University",
    "nyp" : "New York Public Library",
    "uiuo" : "University of Illinois",
    "njp" : "Princeton University",
    "yale" : "Yale University",
    "chi" : "University of Chicago",
    "coo" : "Cornell University",
    "ucm" : "Universidad Complutense de Madrid",
    "loc" : "Library of Congress",
    "ien" : "Northwestern University",
    "hvd" : "Harvard University",
    "uva" : "University of Virginia",
    "dul1" : "Duke University",
    "ncs1" : "North Carolina State University",
    "nc01" : "University of North Carolina",
    "pur1" : "Purdue University",
    "pur2" : "Purdue University",
    "mdl" : "Minnesota Digital Library",
    "usu" : "Utah State University Press",
    "gri" : "Getty Research Institute",
    "uiug" : "University of Illinois",
    "psia" : "Penn State University",
    "bc" : "Boston College",
    "ufl1" : "University of Florida",
    "ufl2" : "University of Florida",
    "txa" : "Texas A&M University",
    "keio" : "Keio University",
    "osu" : "The Ohio State University",
    "uma" : "University of Massachusets",
    "udel" : "University of Delaware",
    "caia" : "Clark Art Institute Library"
}


def parse_record_id(string, fix_truncated_id=False):
    # type: (str) -> str
    '''
    Takes either a record ID or a HT URL for a record. 
    Returns a string containing the record ID or None.

    >>> parse_record_id('https://catalog.hathitrust.org/Record/000234911')
    '000234911'
    >>> parse_record_id('001022499')
    '001022499'
    >>> parse_record_id('1022499', fix_truncated_id=True)
    '001022499'
    '''
    REGEX = r'(?:http[s]?://catalog.hathitrust.org/Record/)?([\d]+)'
    
    try:
        record = re.search(REGEX, string).group(1)
    except AttributeError:
        raise ValueError("No record ID found in string: {}".format(string))

    # Correct truncated IDs or raise error.
    if len(record) != 9:
        if fix_truncated_id:
            record = '0'*(9-len(record)) + record
        else:
            raise ValueError("Invalid record ID. Valid record IDs are 9 digits. " +
            "Call parse_record_id(string, fix_truncated_id=True) to correct.")

    return record


def parse_volume_id(string):
    # type: (str) -> str
    '''
    Takes either a volume ID, HT URL, or Handle URL for a volume.
    Returns a string containing the HTID or None.

    Organization codes for the volumes can be found in ORG_CODES.
    '''

    # First extract the volume ID from a URL, fallbck to assume string.
    parsed_url = urlparse(string)
    if parsed_url.netloc == 'hdl.handle.net':
        # Parse the Handle ID, ex:
        # https://hdl.handle.net/2027/uc2.ark:/13960/fk92805m1s'
        # Note that if the Handle URL contains page info, this is discarded.
        id = parsed_url.path.replace('/2027/', '')

    elif parsed_url.netloc == 'babel.hathitrust.org':
        # Parse the HT Digital Library URL, ex:
        # https://babel.hathitrust.org/cgi/pt?id=uc2.ark:/13960/fk92805m1s;view=1up;seq=7
        if parsed_url.query:
            id = parse_qs(parsed_url.query).get('id', None)[0]
        # TODO: Determine if there are alternate babel.hathitrust.org URLs.

    else:
        id = string

    # Validate ID against ORG_CODES. 
    # Won't guarantee volume existance, but is a sanity check.
    if id and any(id.startswith(org) for org in ORG_CODES):
        return id
    else: 
        raise ValueError("Invalid Organization Code in HathiTrust ID")


def volume_id_to_record_id(volume_id):
    # type: (str) -> str
    """
    Takes a volume id and returns a record id.

    See also: `parse_record_id`
    """
    URL = 'https://catalog.hathitrust.org/Record/HTID/{}'.format(volume_id)
    record_url = urlopen(URL).geturl()
    return parse_record_id(record_url)


def record_id_to_volume_ids(record_id):
    """
    Takes a record id and returns a list of corresponding volume ids.

    HathiTrust is a Digital Library, but is composed of scans of physical
    artifacts. A single catalog record may correspond to multiple volumes 
    in print, especially among pre-20th century texts. Additionally, a single
    catalog record may correspond to  multiple scans from multiple libraries.
    
    This function resolves these ambiguities by selecting only a single copy per
    unique volume label. For example, if a book was printed as three volumes
    labeled in the catalog record as 'v. 1', 'v. 2', and 'v. 3', and contained
    scans from four different libraries of each, this function would return a
    list of 3 volume ids.

    Future iterations of this function may take a list of preferred sources
    based on ORG_CODE and attempt to use same-source volumes for consistency.
    """
    # Get record from BibAPI
    URL = "http://catalog.hathitrust.org/api/volumes/brief/recordnumber/{0}.json"
    URL = URL.format(record_id)
    data = urlopen(URL)
    data = json.load(data)
    data = data['items']

    if not data:
        raise KeyError("No items found for record ID: {}".format(record_id))
    
    # Normalize volume labels
    REGEX = re.compile('\W')
    items = [('DEFAULT' if not item['enumcron']
                        else REGEX.sub('', item['enumcron']), 
                 item['htid']) for item in data]

    # Cast to a dictionary, which removes duplicates as each dictionary key may
    # only have a single value.
    items = dict(items)
    
    if not items:
        raise KeyError("No items found for record ID: {}".format(record_id))
    
    # Return the list of volume ids
    return list(items.values())



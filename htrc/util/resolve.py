import re
from urllib2 import urlopen
from urlparse import urlparse, parse_qs

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


def parse_record_id(string):
    # type: (str) -> str
    '''
    Takes either a record ID or a HT URL for a record. 
    Returns a string containing the record ID or None.

    >>> parse_record_id('https://catalog.hathitrust.org/Record/000234911')
    '000234911'
    >>> parse_record_id('001022499')
    '001022499'
    >>> # Example without a valid record ID
    >>> parse_record_id('https://hdl.handle.net/2027/hvd.hn3t2m')
    >>> parse_record_id('this is not a valid URL or volume ID')
    >>> # The lack of return is an implicit None value.
    '''
    REGEX = r'(?:http[s]?://catalog.hathitrust.org/Record/)?([\d]+)'
    
    try:
        return re.search(REGEX, string).group(1)
    except AttributeError:
        return None


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
            id = parse_qs(parsed_url.query).get('id', None)
        # TODO: Determine if there are alternate babel.hathitrust.org URLs.

    else:
        id = parsed_url.path

    # Validate ID against ORG_CODES. 
    # Won't guarantee volume existance, but is a sanity check.
    if id and any(id.startswith(org) for org in ORG_CODES):
        return id
    else: 
        return None


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
    One commmonly misunderstood aspect of the HT library is that volumes
    """

    base_url = "http://catalog.hathitrust.org/api/volumes/brief/recordnumber/{0}.json"
    vols = []
    regex = re.compile('\W')
    
    record_data = dict()
    for id in record_ids:
    url = base_url.format(id)
    r = requests.get(url)
    data = r.json()
    data = data['records'][id]
    items = [(regex.sub('', item['enumcron']), item['htid']) 
            for item in data['items']]
    items = dict(items)
    for item in items.values():
        print item
    vols.append(items.values())
    time.sleep(0.05)
    record_data[id] = data

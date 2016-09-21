"""
`htrc.workset`

Contains function to extract all volume IDs from a JSON-LD workset 
representation.

Will eventually be expanded to allow for querying based on arbitrary
ID and for update and removal of volumes from Workset.
"""


from pyld import jsonld
import json
from pprint import pprint

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

# Support for testing `get_volumes` using the module: 
# `python -m htrc.workset WORKSET_FILE.json`
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()
   
    # open the JSON-LD file
    with open(args.filename) as infile:
        data = json.load(infile)

    # Retrieve and print the volumes
    volumes = get_volumes(data)

    for vol in volumes:
        print vol


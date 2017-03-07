import unittest2 as unittest

import htrc.workset

class TestWorkset(unittest.TestCase):
    def test_get_volumes(self):
        """
        Test get_volumes by ensuring that the JSON-LD data structure can be
        extracted.
        """
        pass

    def test_load_file(self):
        pass

    def test_load_url_hathitrust(self):
        pass

    def test_load_url_htrc(self):
        pass

    def test_get_volumes_from_csv(self):
        pass

    def test_load_hathitrust_collection(self):
        pass 


suite = unittest.TestLoader().loadTestsFromTestCase(TestWorkset)
unittest.TextTestRunner(verbosity=2).run(suite)

import unittest2 as unittest

import htrc.volumes

class TestVolumes(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_volumes(self):
        pass

    def test_get_pages(self):
        pass

    def test_get_token(self):
        pass

    def test_print_zip(self):
        pass

    def test_download_volumes(self):
        pass

    def test_download(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestVolumes)
unittest.TextTestRunner(verbosity=2).run(suite)


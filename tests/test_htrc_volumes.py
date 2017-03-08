from mock import Mock, patch
import tempfile
import unittest2 as unittest

import htrc.volumes

class TestVolumes(unittest.TestCase):
    def setUp(self):
        self.config_path = tempfile.NamedTemporaryFile(delete=False).name
        self.empty_config_path = tempfile.NamedTemporaryFile(delete=False).name

    def tearDown(self):
        import os
        os.remove(self.config_path)

    @patch('htrc.volumes.bool_prompt')
    @patch('htrc.volumes.input')
    def test_credential_store(self, input_mock, bool_mock):
        # configure mocks
        input_mock.return_value = '1234'
        bool_mock.return_value = True

        # test prompts
        username, password = htrc.volumes.credential_prompt(self.config_path)
        self.assertEqual(username, '1234')
        self.assertEqual(password, '1234')

        # test read
        username, password = htrc.volumes.credentials_from_config(
            self.config_path)
        self.assertEqual(username, '1234')
        self.assertEqual(password, '1234')

    def test_empty_credential_exception(self):
        with self.assertRaises(EnvironmentError):
            htrc.volumes.credentials_from_config(self.empty_config_path)

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


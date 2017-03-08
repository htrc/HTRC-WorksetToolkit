from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

from io import BytesIO  # used to stream http response into zipfile.
from mock import Mock, patch, PropertyMock
import tempfile
import unittest2 as unittest

import htrc.volumes

class MockResponse(BytesIO):
    def __init__(self, data, status=200, *args, **kwargs):
        BytesIO.__init__(self, data, *args, **kwargs)
        self.status = status

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

    @patch('htrc.volumes.http.client.HTTPSConnection')
    def test_get_oauth2_token(self, https_mock):
        response_mock = Mock(status=200)
        response_mock.read.return_value = '{"access_token": "a1b2c3d4e5f6"}'
        https_mock.return_value.getresponse.return_value = response_mock
        
        token = htrc.volumes.get_oauth2_token('1234','1234')
        self.assertEqual(token, 'a1b2c3d4e5f6')

    @patch('htrc.volumes.http.client.HTTPSConnection')
    def test_get_oauth2_token_fail(self, https_mock):
        response_mock = Mock(status=500)
        response_mock.read.return_value = '{"access_token": "a1b2c3d4e5f6"}'
        https_mock.return_value.getresponse.return_value = response_mock

        with self.assertRaises(EnvironmentError):
            token = htrc.volumes.get_oauth2_token('1234','1234')

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


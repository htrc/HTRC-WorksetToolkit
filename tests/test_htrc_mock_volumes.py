from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock

from io import BytesIO  # used to stream http response into zipfile.
from tempfile import NamedTemporaryFile, mkdtemp
import unittest2 as unittest

import htrc.mock.volumes

class MockResponse(BytesIO):
    def __init__(self, data, status=200, *args, **kwargs):
        BytesIO.__init__(self, data, *args, **kwargs)
        self.status = status

class TestVolumes(unittest.TestCase):
    def setUp(self):
        self.test_vols = ['mdp.39015050817181', 'mdp.39015055436151',
            'mdp.39015056169157', 'mdp.39015050161697', 'mdp.39015042791874']

        self.config_path = NamedTemporaryFile(delete=False).name
        self.empty_config_path = NamedTemporaryFile(delete=False).name

        self.output_path = mkdtemp()

    def tearDown(self):
        import os, shutil
        os.remove(self.config_path)
        shutil.rmtree(self.output_path)

    @patch('htrc.mock.volumes.credential_prompt')
    def test_credential_prompt(self, credential_prompt_mock):
        # configure mocks
        credential_prompt_mock.return_value = ('1234', '1234')

        # test prompts
        username, password = htrc.mock.volumes.credential_prompt(self.config_path)
        self.assertEqual(username, '1234')
        self.assertEqual(password, '1234')

        # test read
        username, password = htrc.mock.volumes.credentials_from_config(
            self.config_path)
        self.assertEqual(username, None)
        self.assertEqual(password, None)

    def test_get_oauth2_token(self):
        token = htrc.mock.volumes.get_oauth2_token('1234','1234')
        self.assertEqual(token, 'a1b2c3d4e5f6')

    def test_get_volumes_and_pages(self):
        htrc.mock.volumes.get_volumes('1234', self.test_vols)
        htrc.mock.volumes.get_pages('1234', self.test_vols)

    def test_get_volumes_and_pages_empty(self):
        with self.assertRaises(ValueError):
            htrc.mock.volumes.get_volumes('1234', [])

        with self.assertRaises(ValueError):
            htrc.mock.volumes.get_pages('1234', [])

    @patch('htrc.mock.volumes.ZipFile')
    @patch('htrc.mock.volumes.get_volumes')
    @patch('htrc.mock.volumes.get_oauth2_token')
    def test_download_volumes(self, oauth2_mock, volumes_mock, zip_mock):
        oauth2_mock.return_value = 'a1b2c3d4e5'
        volumes_mock.return_value = b''

        htrc.mock.volumes.download_volumes(self.test_vols, self.output_path,
            username='1234', password='1234')

        # test directory creation
        import shutil
        shutil.rmtree(self.output_path)
        htrc.mock.volumes.download_volumes(self.test_vols, self.output_path,
            username='1234', password='1234')

    @patch('htrc.mock.volumes.ZipFile')
    @patch('htrc.mock.volumes.get_volumes')
    @patch('htrc.mock.volumes.get_oauth2_token')
    def test_download_volumes_saved_creds(self, oauth2_mock, volumes_mock, zip_mock):
        oauth2_mock.return_value = 'a1b2c3d4e5'
        volumes_mock.return_value = b''

        # test config-based auth
        import os, os.path
        config_path = os.path.expanduser('~')
        config_path = os.path.join(config_path, '.htrc')
        preexisting_config = os.path.exists(config_path)
        if not preexisting_config:
            htrc.mock.volumes.save_credentials('1234', '1234', config_path)

        htrc.mock.volumes.download_volumes(self.test_vols, self.output_path)

        if not preexisting_config:
            os.remove(config_path)

    def test_download(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestVolumes)
unittest.TextTestRunner(verbosity=2).run(suite)


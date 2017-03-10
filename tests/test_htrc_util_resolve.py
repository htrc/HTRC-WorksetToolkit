from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch

import unittest2 as unittest

import htrc.util.resolve as resolve

class TestResolve(unittest.TestCase):
    def test_parse_record_id(self):
        id = resolve.parse_record_id('https://catalog.hathitrust.org/Record/000234911')
        self.assertEqual(id, '000234911')

        id = resolve.parse_record_id('000234911')
        self.assertEqual(id, '000234911')

        
        with self.assertRaises(ValueError):
            resolve.parse_record_id('https://hdl.handle.net/2027/hvd.hn3t2m')

        with self.assertRaises(ValueError):
            resolve.parse_record_id('this is not a valid URL or volume ID')

    def test_parse_truncated_record_id(self):
        # test truncated IDs
        with self.assertRaises(ValueError):
            resolve.parse_record_id('234911')

        id = resolve.parse_record_id('234911', fix_truncated_id=True)
        self.assertEqual(id, '000234911')

    def test_parse_volume_id(self):
        id = resolve.parse_volume_id('https://hdl.handle.net/2027/uc2.ark:/13960/fk92805m1s')
        self.assertEqual(id, 'uc2.ark:/13960/fk92805m1s')

        id = resolve.parse_volume_id('https://babel.hathitrust.org/cgi/pt?id=uc2.ark:/13960/fk92805m1s;view=1up;seq=7')
        self.assertEqual(id, 'uc2.ark:/13960/fk92805m1s')

        id = resolve.parse_volume_id('uc2.ark:/13960/fk92805m1s')
        self.assertEqual(id, 'uc2.ark:/13960/fk92805m1s')

        with self.assertRaises(ValueError):
            # check if incorrect institution ID raises error
            resolve.parse_volume_id('uc42.ark:/13960/fk92805m1s')
        
    @patch('htrc.util.resolve.urlopen')
    def test_volume_id_to_record_id(self, urlopen_mock):
        urlopen_mock.return_value.geturl.return_value =\
            'https://catalog.hathitrust.org/Record/000850926'
        record_id = resolve.volume_id_to_record_id('uc2.ark:/13960/fk92805m1s')

        self.assertEqual(record_id, '000850926')


    @patch('htrc.util.resolve.urlopen')
    def test_record_id_to_volume_ids(self, urlopen_mock):
        urlopen_mock.return_value.read.return_value =\
            b'{"items":[{"orig":"Harvard University","fromRecord":"000850926","htid":"hvd.hn3t2m","itemURL":"https:\/\/hdl.handle.net\/2027\/hvd.hn3t2m","rightsCode":"pd","lastUpdate":"20130803","enumcron":false,"usRightsString":"Full view"}]}'.decode('utf-8')
        ids = resolve.record_id_to_volume_ids('000234911')
        self.assertEqual(ids, ['hvd.hn3t2m'])

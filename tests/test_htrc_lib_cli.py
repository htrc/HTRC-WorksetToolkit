from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import sys
if sys.version_info.major == 2:
    from mock import Mock, patch, PropertyMock
elif sys.version_info.major == 3:
    from unittest.mock import Mock, patch, PropertyMock

import unittest2 as unittest

from htrc.lib.cli import *

class TestVolumes(unittest.TestCase):
    @patch('htrc.lib.cli.input')
    def test_bool_prompt(self, input_mock):
        # test True
        input_mock.return_value = 'y'
        return_value = bool_prompt("Enter yes")
        self.assertEqual(return_value, True)
        
        input_mock.return_value = 'n'
        return_value = bool_prompt("Enter no")
        self.assertEqual(return_value, False)

        input_mock.return_value = ''
        return_value = bool_prompt("Enter nothing for false", default=False)
        self.assertEqual(return_value, False)
        
        return_value = bool_prompt("Enter nothing for true", default=True)
        self.assertEqual(return_value, True)

    @patch('htrc.lib.cli.input')
    def test_prompt_default(self, input_mock):
        input_mock.return_value = ''
        return_value = prompt("Enter nothing for 3", default='3')
        self.assertEqual(return_value, '3')


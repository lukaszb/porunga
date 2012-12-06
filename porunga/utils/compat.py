"""
This module provides utilities or wraps existing modules/packages into
tools universal across supported Python versions.
"""
from __future__ import unicode_literals
from __future__ import print_function

import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

if sys.version_info >= (3, 2):
    def assertItemsEqual(self, result, expected, msg=None):
        self.assertEqual(sorted(result), sorted(expected), msg=msg)
    unittest.TestCase.assertItemsEqual = assertItemsEqual


try:
    from collections import OrderedDict
except ImportError:
    from monolith.utils.ordereddict import OrderedDict

try:
    unicode = unicode
except NameError:
    basestring = unicode = str

if sys.version_info < (2, 7):
    from contextlib import nested
else:
    def nested(*context_managers):
        return tuple(context_managers)


__all__ = ['unittest', 'OrderedDict', 'nested', 'unicode']


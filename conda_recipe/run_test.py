

import sys
import unittest

from pybgen.tests import test_suite as pybgen_test_suite


result = unittest.TextTestRunner().run(pybgen_test_suite)
sys.exit(0 if result.wasSuccessful() else 1)

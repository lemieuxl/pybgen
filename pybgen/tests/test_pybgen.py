# This file is part of pybgen.
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Louis-Philippe Lemieux Perreault
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from __future__ import print_function

import os
import shutil
import unittest
from tempfile import mkdtemp

from pkg_resources import resource_filename

from .. import pybgen


class TestPyBGEN(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Creating a temporary directory
        cls.tmp_dir = mkdtemp(prefix="pyplink_test_")

        # Getting the BGEN file
        cls.bgen_fn = resource_filename(
            __name__,
            os.path.join("data", "example.32bits.bgen"),
        )

    def setUp(self):
        # Reading the BGEN file
        self.bgen = pybgen.PyBGEN(self.bgen_fn)

    @classmethod
    def tearDownClass(cls):
        # Cleaning the temporary directory
        shutil.rmtree(cls.tmp_dir)

    def tearDown(self):
        # Closing the PyPlink object
        self.bgen.close()

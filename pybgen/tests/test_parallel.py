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


import os
import random
import unittest

from pkg_resources import resource_filename

import numpy as np

from ..parallel import ParallelPyBGEN
from ..pybgen import HAS_ZSTD
from .truths import truths
from .test_pybgen import ReaderTests


__all__ = ["parallel_reader_tests"]


class ParallelReaderTests(ReaderTests):

    def setUp(self):
        # Getting the truth for this file
        self.truths = truths["dosage"][self.truth_filename]

        # Reading the BGEN file
        bgen_fn = resource_filename(__name__, self.bgen_filename)
        self.bgen = ParallelPyBGEN(bgen_fn)

    def test_iter_variants_by_name(self):
        """Tests the iteration of variants by name."""
        # Fetching random variants in the index
        self.bgen._bgen_index.execute("SELECT rsid FROM Variant")
        names = [
            _[0] for _ in random.sample(self.bgen._bgen_index.fetchall(), 5)
        ]

        seen_variants = set()
        iterator = self.bgen.iter_variants_by_names(names)
        for variant, dosage in iterator:
            # The name of the variant
            name = variant.name
            seen_variants.add(name)

            # Comparing the variant
            self._compare_variant(
                self.truths["variants"][name]["variant"],
                variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                self.truths["variants"][name]["data"], dosage,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, set(names))


class ParallelProbsReaderTests(ParallelReaderTests):

    def setUp(self):
        # Getting the truth for this file
        self.truths = truths["probs"][self.truth_filename]

        # Reading the BGEN file
        bgen_fn = resource_filename(__name__, self.bgen_filename)
        self.bgen = ParallelPyBGEN(bgen_fn, probs_only=True)

    def test_check_returned_value(self):
        """Tests the module is returning probability data."""
        self.assertTrue(self.bgen._return_probs)


class Test32bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.32bits.bgen")
    truth_filename = "example.32bits.truths.txt.bz2"


class Test32bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.32bits.bgen")
    truth_filename = "example.32bits.probs.truths.txt.bz2"


class Test24bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.24bits.bgen")
    truth_filename = "example.24bits.truths.txt.bz2"


class Test24bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.24bits.bgen")
    truth_filename = "example.24bits.probs.truths.txt.bz2"


class Test16bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.bgen")
    truth_filename = "example.16bits.truths.txt.bz2"


class Test16bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.bgen")
    truth_filename = "example.16bits.probs.truths.txt.bz2"


@unittest.skipIf(not HAS_ZSTD, "module 'zstandard' not installed")
class Test16bitsZstd(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.zstd.bgen")
    truth_filename = "example.16bits.zstd.truths.txt.bz2"


@unittest.skipIf(not HAS_ZSTD, "module 'zstandard' not installed")
class Test16bitsZstdProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.zstd.bgen")
    truth_filename = "example.16bits.zstd.probs.truths.txt.bz2"


class Test9bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.9bits.bgen")
    truth_filename = "example.9bits.truths.txt.bz2"


class Test9bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.9bits.bgen")
    truth_filename = "example.9bits.probs.truths.txt.bz2"


class Test8bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.8bits.bgen")
    truth_filename = "example.8bits.truths.txt.bz2"


class Test8bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.8bits.bgen")
    truth_filename = "example.8bits.probs.truths.txt.bz2"


class Test3bits(ParallelReaderTests):
    bgen_filename = os.path.join("data", "example.3bits.bgen")
    truth_filename = "example.3bits.truths.txt.bz2"


class Test3bitsProbs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "example.3bits.bgen")
    truth_filename = "example.3bits.probs.truths.txt.bz2"


class TestLayout1(ParallelReaderTests):
    bgen_filename = os.path.join("data", "cohort1.bgen")
    truth_filename = "cohort1.truths.txt.bz2"


class TestLayout1Probs(ParallelProbsReaderTests):
    bgen_filename = os.path.join("data", "cohort1.bgen")
    truth_filename = "cohort1.probs.truths.txt.bz2"


parallel_reader_tests = (
    Test32bits, Test24bits, Test16bits, Test16bitsZstd, Test9bits, Test8bits,
    Test3bits, TestLayout1, Test32bitsProbs, Test24bitsProbs, Test16bitsProbs,
    Test16bitsZstdProbs, Test9bitsProbs, Test8bitsProbs, Test3bitsProbs,
    TestLayout1Probs,
)

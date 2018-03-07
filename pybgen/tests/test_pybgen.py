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

import numpy as np
from pkg_resources import resource_filename

from .. import pybgen
from .truths import truths


__all__ = ["reader_tests"]


class ReaderTests(unittest.TestCase):

    def setUp(self):
        # Getting the truth for this file
        self.truths = truths["dosage"][self.truth_filename]

        # Reading the BGEN files
        bgen_fn = resource_filename(__name__, self.bgen_filename)
        self.bgen = pybgen.PyBGEN(bgen_fn)

    def tearDown(self):
        # Closing the object
        self.bgen.close()

    def _compare_variant(self, expected, observed):
        """Compare two variants."""
        self.assertEqual(expected.name, observed.name)
        self.assertEqual(expected.chrom, observed.chrom)
        self.assertEqual(expected.pos, observed.pos)
        self.assertEqual(expected.a1, observed.a1)
        self.assertEqual(expected.a2, observed.a2)

    def test_check_returned_value(self):
        """Tests the module is returning dosage data."""
        self.assertFalse(self.bgen._return_probs)

    def test_repr(self):
        """Tests the __repr__ representation."""
        self.assertEqual(
            "PyBGEN({:,d} samples; {:,d} variants)".format(
                self.truths["nb_samples"],
                self.truths["nb_variants"],
            ),
            str(self.bgen),
        )

    def test_nb_samples(self):
        """Tests the number of samples."""
        self.assertEqual(self.truths["nb_samples"], self.bgen.nb_samples)

    def test_nb_variants(self):
        """Tests the number of variants."""
        self.assertEqual(self.truths["nb_variants"], self.bgen.nb_variants)

    def test_samples(self):
        """Tests the samples attribute."""
        if self.truths["samples"] is None:
            self.assertTrue(self.bgen.samples is None)
        else:
            self.assertEqual(self.truths["samples"], self.bgen.samples)

    def test_get_first_variant(self):
        """Tests getting the first variant of the file."""
        # The variant to retrieve
        name = "RSID_2"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(
            self.truths["variants"][name]["variant"], variant,
        )

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            self.truths["variants"][name]["data"], dosage,
        )

    def test_get_middle_variant(self):
        """Tests getting a variant in the middle of the file."""
        # The variant to retrieve
        name = "RSID_148"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(
            self.truths["variants"][name]["variant"], variant,
        )

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            self.truths["variants"][name]["data"], dosage,
        )

    def test_get_last_variant(self):
        """Tests getting the last variant of the file."""
        # The variant to retrieve
        name = "RSID_200"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(
            self.truths["variants"][name]["variant"], variant,
        )

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            self.truths["variants"][name]["data"], dosage,
        )

    def test_get_missing_variant(self):
        """Tests getting a variant which is absent from the BGEN file."""
        with self.assertRaises(ValueError) as cm:
            self.bgen.get_variant("UNKOWN_VARIANT_NAME")
        self.assertEqual(
            "UNKOWN_VARIANT_NAME: name not found",
            str(cm.exception),
        )

    def test_iter_all_variants(self):
        """Tests the iteration of all variants."""
        seen_variants = set()
        for variant, dosage in self.bgen.iter_variants():
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
        self.assertEqual(seen_variants, self.truths["variant_set"])

    def test_as_iterator(self):
        """Tests the module as iterator."""
        seen_variants = set()
        for variant, dosage in self.bgen:
            # The name of the variant
            name = variant.name
            seen_variants.add(name)

            # Comparing the variant
            self._compare_variant(
                self.truths["variants"][name]["variant"], variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                self.truths["variants"][name]["data"], dosage,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, self.truths["variant_set"])

    def test_iter_variant_info(self):
        """Tests the iteration of all variants' information."""
        seen_variants = set()
        for variant in self.bgen.iter_variant_info():
            # The name of the variant
            name = variant.name
            seen_variants.add(name)

            # Comparing the variant
            self._compare_variant(
                self.truths["variants"][name]["variant"], variant,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, self.truths["variant_set"])

    def test_iter_variants_in_region(self):
        """Tests the iteration of all variants in a genomic region."""
        seen_variants = set()
        iterator = self.bgen.iter_variants_in_region("01", 67000, 70999)
        for variant, dosage in iterator:
            # The name of the variant
            name = variant.name
            seen_variants.add(name)

            # Comparing the variant
            self._compare_variant(
                self.truths["variants"][name]["variant"], variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                self.truths["variants"][name]["data"], dosage,
            )

        # Checking if we checked all variants
        expected = set()
        for name in self.truths["variant_set"]:
            variant = self.truths["variants"][name]["variant"]
            if variant.chrom == "01":
                if variant.pos >= 67000 and variant.pos <= 70999:
                    expected.add(name)
        self.assertEqual(seen_variants, expected)

    def test_iter_seeks(self):
        """Tests the _iter_seeks function."""
        # Fetching random seeks from the index
        self.bgen._bgen_index.execute(
            "SELECT rsid, file_start_position FROM Variant"
        )
        seeks = random.sample(self.bgen._bgen_index.fetchall(), 5)

        seen_variants = set()
        iterator = self.bgen._iter_seeks([_[1] for _ in seeks])
        for variant, dosage in iterator:
            # The name of the variant
            name = variant.name
            seen_variants.add(name)

            # Comparing the variant
            self._compare_variant(
                self.truths["variants"][name]["variant"], variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                self.truths["variants"][name]["data"], dosage,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, {_[0] for _ in seeks})


class ProbsReaderTests(ReaderTests):

    def setUp(self):
        # Getting the truth for this file
        self.truths = truths["probs"][self.truth_filename]

        # Reading the BGEN files
        bgen_fn = resource_filename(__name__, self.bgen_filename)
        self.bgen = pybgen.PyBGEN(bgen_fn, probs_only=True)

    def test_check_returned_value(self):
        """Tests the module is returning probability data."""
        self.assertTrue(self.bgen._return_probs)


class Test32bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.32bits.bgen")
    truth_filename = "example.32bits.truths.txt.bz2"


class Test32bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.32bits.bgen")
    truth_filename = "example.32bits.probs.truths.txt.bz2"


class Test24bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.24bits.bgen")
    truth_filename = "example.24bits.truths.txt.bz2"


class Test24bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.24bits.bgen")
    truth_filename = "example.24bits.probs.truths.txt.bz2"


class Test16bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.bgen")
    truth_filename = "example.16bits.truths.txt.bz2"


class Test16bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.bgen")
    truth_filename = "example.16bits.probs.truths.txt.bz2"


@unittest.skipIf(not pybgen.HAS_ZSTD, "module 'zstandard' not installed")
class Test16bitsZstd(ReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.zstd.bgen")
    truth_filename = "example.16bits.zstd.truths.txt.bz2"


@unittest.skipIf(not pybgen.HAS_ZSTD, "module 'zstandard' not installed")
class Test16bitsZstdProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.16bits.zstd.bgen")
    truth_filename = "example.16bits.zstd.probs.truths.txt.bz2"


class Test9bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.9bits.bgen")
    truth_filename = "example.9bits.truths.txt.bz2"


class Test9bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.9bits.bgen")
    truth_filename = "example.9bits.probs.truths.txt.bz2"


class Test8bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.8bits.bgen")
    truth_filename = "example.8bits.truths.txt.bz2"


class Test8bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.8bits.bgen")
    truth_filename = "example.8bits.probs.truths.txt.bz2"


class Test3bits(ReaderTests):
    bgen_filename = os.path.join("data", "example.3bits.bgen")
    truth_filename = "example.3bits.truths.txt.bz2"


class Test3bitsProbs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "example.3bits.bgen")
    truth_filename = "example.3bits.probs.truths.txt.bz2"


class TestLayout1(ReaderTests):
    bgen_filename = os.path.join("data", "cohort1.bgen")
    truth_filename = "cohort1.truths.txt.bz2"


class TestLayout1Probs(ProbsReaderTests):
    bgen_filename = os.path.join("data", "cohort1.bgen")
    truth_filename = "cohort1.probs.truths.txt.bz2"


reader_tests = (
    Test32bits, Test24bits, Test16bits, Test16bitsZstd, Test9bits, Test8bits,
    Test3bits, TestLayout1, Test32bitsProbs, Test24bitsProbs, Test16bitsProbs,
    Test16bitsZstdProbs, Test9bitsProbs, Test8bitsProbs, Test3bitsProbs,
    TestLayout1Probs,
)

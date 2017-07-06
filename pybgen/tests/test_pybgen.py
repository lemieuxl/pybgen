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
import shutil
import unittest
from tempfile import mkdtemp

import numpy as np
from pkg_resources import resource_filename

from .. import pybgen
from .truths import example_32bits_truths as truths_1
from .truths import cohort1_truths as truths_2


class TestPyBGEN_1(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Creating a temporary directory
        cls.tmp_dir = mkdtemp(prefix="pybgen_test_")

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
        # Closing the object
        self.bgen.close()

    def _compare_variant(self, expected, observed):
        """Compare two variants."""
        self.assertEqual(expected.name, observed.name)
        self.assertEqual(expected.chrom, observed.chrom)
        self.assertEqual(expected.pos, observed.pos)
        self.assertEqual(expected.a1, observed.a1)
        self.assertEqual(expected.a2, observed.a2)

    def test_repr(self):
        """Tests the __repr__ representation."""
        self.assertEqual(
            "PyBGEN({:,d} samples; {:,d} variants)".format(
                truths_1["nb_samples"], truths_1["nb_variants"],
            ),
            str(self.bgen),
        )

    def test_nb_samples(self):
        """Tests the number of samples."""
        self.assertEqual(truths_1["nb_samples"], self.bgen.nb_samples)

    def test_nb_variants(self):
        """Tests the number of variants."""
        self.assertEqual(truths_1["nb_variants"], self.bgen.nb_variants)

    def test_samples(self):
        """Tests the samples attribute."""
        self.assertEqual(truths_1["samples"], self.bgen.samples)

    def test_get_first_variant(self):
        """Tests getting the first variant of the file."""
        # The variant to retrieve
        name = "RSID_2"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(truths_1["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_1["variants"][name]["dosage"], dosage,
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
        self._compare_variant(truths_1["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_1["variants"][name]["dosage"], dosage,
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
        self._compare_variant(truths_1["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_1["variants"][name]["dosage"], dosage,
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
                truths_1["variants"][name]["variant"],
                variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                truths_1["variants"][name]["dosage"], dosage,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, truths_1["variant_set"])


class TestPyBGEN_2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Creating a temporary directory
        cls.tmp_dir = mkdtemp(prefix="pybgen_test_")

        # Getting the BGEN file
        cls.bgen_fn = resource_filename(
            __name__,
            os.path.join("data", "cohort1.bgen"),
        )

    def setUp(self):
        # Reading the BGEN file
        self.bgen = pybgen.PyBGEN(self.bgen_fn)

    @classmethod
    def tearDownClass(cls):
        # Cleaning the temporary directory
        shutil.rmtree(cls.tmp_dir)

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

    def test_repr(self):
        """Tests the __repr__ representation."""
        self.assertEqual(
            "PyBGEN({:,d} samples; {:,d} variants)".format(
                truths_2["nb_samples"], truths_2["nb_variants"],
            ),
            str(self.bgen),
        )

    def test_nb_samples(self):
        """Tests the number of samples."""
        self.assertEqual(truths_2["nb_samples"], self.bgen.nb_samples)

    def test_nb_variants(self):
        """Tests the number of variants."""
        self.assertEqual(truths_2["nb_variants"], self.bgen.nb_variants)

    def test_samples(self):
        """Tests the samples attribute."""
        self.assertTrue(self.bgen.samples is None)

    def test_get_first_variant(self):
        """Tests getting the first variant of the file."""
        # The variant to retrieve
        name = "RSID_1"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(truths_2["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_2["variants"][name]["dosage"], dosage,
        )

    def test_get_middle_variant(self):
        """Tests getting a variant in the middle of the file."""
        # The variant to retrieve
        name = "RSID_161"

        # Getting the results (there should be only one
        r = self.bgen.get_variant(name)
        self.assertEqual(1, len(r))
        variant, dosage = r.pop()

        # Checking the variant
        self._compare_variant(truths_2["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_2["variants"][name]["dosage"], dosage,
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
        self._compare_variant(truths_2["variants"][name]["variant"], variant)

        # Checking the dosage
        np.testing.assert_array_almost_equal(
            truths_2["variants"][name]["dosage"], dosage,
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
                truths_2["variants"][name]["variant"],
                variant,
            )

            # Comparing the dosage
            np.testing.assert_array_almost_equal(
                truths_2["variants"][name]["dosage"], dosage,
            )

        # Checking if we checked all variants
        self.assertEqual(seen_variants, truths_2["variant_set"])

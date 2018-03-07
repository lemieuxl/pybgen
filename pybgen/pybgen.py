"""Module that reads BGEN files."""

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


from __future__ import division

import os
import sys
import zlib
import logging
import sqlite3
from math import ceil
from struct import unpack
from io import UnsupportedOperation

import numpy as np

from six.moves import range

try:
    import zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False


__author__ = "Louis-Philippe Lemieux Perreault"
__copyright__ = "Copyright 2017 Louis-Philippe Lemieux Perreault"
__license__ = "MIT"


__all__ = ["PyBGEN"]


# The logger
logger = logging.getLogger(__name__)


# The python version
PYTHON_VERSION = sys.version_info.major


class _Variant(object):
    __slots__ = ("name", "chrom", "pos", "a1", "a2")

    def __init__(self, name, chrom, pos, a1, a2):
        self.name = name
        self.chrom = chrom
        self.pos = pos
        self.a1 = a1
        self.a2 = a2

    def __repr__(self):
        return "<Variant {} chr{}:{}_{}/{}>".format(
            self.name, self.chrom, self.pos, self.a1, self.a2,
        )


class PyBGEN(object):
    """Reads and store a set of BGEN files.

    Args:
        fn (str): The name of the BGEN file.
        mode (str): The open mode for the BGEN file.
        prob_t (float): The probability threshold (optional).
        probs_only (boolean): Return only the probabilities instead of dosage.

    Reads or write BGEN files.

    .. code-block:: python

        from pybgen import PyBGEN

        # Reading a BGEN file
        with PyBGEN("bgen_file_name") as bgen:
            pass

    """

    def __init__(self, fn, mode="r", prob_t=0.9, _skip_index=False,
                 probs_only=False):
        """Initializes a new PyBGEN instance."""
        # The mode
        self._mode = mode

        # What to return
        self._return_probs = probs_only

        if self._mode == "r":
            # Parsing the file
            self._bgen = open(fn, "rb")
            self._parse_header()

            # Did the samples were parsed?
            if not self._has_sample:
                self._samples = None

            # Connecting to the index
            self._skip_index = _skip_index
            if not _skip_index:
                if not os.path.isfile(fn + ".bgi"):
                    raise IOError("{}: no such file".format(fn + ".bgi"))
                self._connect_index()

            # The probability
            self.prob_t = prob_t

            # Seeking to the first variant of the file
            self._bgen.seek(self._first_variant_block)

        elif self._mode == "w":
            raise NotImplemented("'w' mode not yet implemented")

        else:
            raise ValueError("invalid mode: '{}'".format(self._mode))

    def __repr__(self):
        """The representation of the PyBGEN object."""
        if self._mode == "r":
            return "PyBGEN({:,d} samples; {:,d} variants)".format(
                self._nb_samples, self._nb_variants,
            )

        return 'PyBGEN(mode="w")'

    def __iter__(self):
        """The __iter__ function."""
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        return self

    def __next__(self):
        """The __next__ function."""
        return self.next()

    def __enter__(self):
        """Entering the context manager."""
        return self

    def __exit__(self, *args):
        """Exiting the context manager."""
        self.close()

    def close(self):
        """Closes the BGEN object."""
        # Closing the BGEN file
        self._bgen.close()

        # Closing the index file (if in read mode)
        if self._mode == "r" and not self._skip_index:
            self._bgen_db.close()

    @property
    def nb_variants(self):
        """Returns the number of markers.

        Returns:
            int: The number of markers in the dataset.

        """
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        return self._nb_variants

    @property
    def nb_samples(self):
        """Returns the number of samples.

        Returns:
            int: The number of samples in the dataset.

        """
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        return self._nb_samples

    @property
    def samples(self):
        """Returns the samples.

        Returns:
            tuple: The samples.

        """
        return self._samples

    def next(self):
        """Returns the next variant.

        Returns:
            tuple: The variant's information and its genotypes (dosage) as
            :py:class:`numpy.ndarray`.

        """
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        if self._bgen.tell() > self._last_variant_block:
            raise StopIteration()

        return self._read_current_variant()

    def iter_variants(self):
        """Iterates over variants from the beginning of the BGEN file.

        Returns:
            tuple: A variant and the dosage.

        """
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        # Seeking back to the first variant block
        self._bgen.seek(self._first_variant_block)

        # Return itself (the generator)
        return self

    def iter_variants_in_region(self, chrom, start, end):
        """Iterates over variants in a specific region.

        Args:
            chrom (str): The name of the chromosome.
            start (int): The starting position of the region.
            end (int): The ending position of the region.

        """
        # Getting the region from the index file
        self._bgen_index.execute(
            "SELECT file_start_position "
            "FROM Variant "
            "WHERE chromosome = ? AND position >= ? AND position <= ?",
            (chrom, start, end),
        )

        # Fetching all the seek positions
        seek_positions = [_[0] for _ in self._bgen_index.fetchall()]

        # Fetching seek positions, we return the variant
        for seek_pos in seek_positions:
            self._bgen.seek(seek_pos)
            yield self._read_current_variant()

    def iter_variant_info(self):
        """Iterate over marker information."""
        self._bgen_index.execute(
            "SELECT chromosome, position, rsid, allele1, allele2 FROM Variant",
        )

        # The array size
        array_size = 1000

        # Fetching the results
        results = self._bgen_index.fetchmany(array_size)
        while results:
            for chrom, pos, rsid, a1, a2 in results:
                yield _Variant(rsid, chrom, pos, a1, a2)
            results = self._bgen_index.fetchmany(array_size)

    def _iter_seeks(self, seeks):
        """Iterate over seek positions."""
        for seek in seeks:
            self._bgen.seek(seek)
            yield self._read_current_variant()

    def get_variant(self, name):
        """Gets the values for a given variant.

        Args:
            name (str): The name of the variant.

        Returns:
            list: A list containing all the value for a given variant. The list
            has more than one item if there are duplicated variants.

        """
        if self._mode != "r":
            raise UnsupportedOperation("not available in 'w' mode")

        # Fetching the variant
        self._bgen_index.execute(
            "SELECT file_start_position FROM Variant WHERE rsid = ?",
            (name, )
        )

        # Fetching all the seek positions
        seek_positions = [_[0] for _ in self._bgen_index.fetchall()]

        # Constructing the results
        results = []
        for seek_pos in seek_positions:
            self._bgen.seek(seek_pos)
            results.append(self._read_current_variant())

        if not results:
            raise ValueError("{}: name not found".format(name))

        return results

    def _read_current_variant(self):
        """Reads the current variant."""
        # Getting the variant's information
        var_id, rs_id, chrom, pos, alleles = self._get_curr_variant_info()

        # Getting the variant's dosage
        dosage = self._get_curr_variant_data()

        return _Variant(rs_id, chrom, pos, *alleles), dosage

    def _get_curr_variant_info(self):
        """Gets the current variant's information."""
        if self._layout == 1:
            n = unpack("<I", self._bgen.read(4))[0]
            if n != self._nb_samples:
                raise ValueError(
                    "{}: invalid BGEN file".format(self._bgen.name),
                )

        # Reading the variant id
        var_id = self._bgen.read(unpack("<H", self._bgen.read(2))[0]).decode()

        # Reading the variant rsid
        rs_id = self._bgen.read(unpack("<H", self._bgen.read(2))[0]).decode()

        # Reading the chromosome
        chrom = self._bgen.read(unpack("<H", self._bgen.read(2))[0]).decode()

        # Reading the position
        pos = unpack("<I", self._bgen.read(4))[0]

        # Getting the number of alleles
        nb_alleles = 2
        if self._layout == 2:
            nb_alleles = unpack("<H", self._bgen.read(2))[0]

        # Getting the alleles
        alleles = []
        for _ in range(nb_alleles):
            alleles.append(self._bgen.read(
                unpack("<I", self._bgen.read(4))[0]
            ).decode())

        return var_id, rs_id, chrom, pos, tuple(alleles)

    def _get_curr_variant_probs_layout_1(self):
        """Gets the current variant's probabilities (layout 1)."""
        c = self._nb_samples
        if self._is_compressed:
            c = unpack("<I", self._bgen.read(4))[0]

        # Getting the probabilities
        probs = np.frombuffer(
            self._decompress(self._bgen.read(c)),
            dtype="u2",
        ) / 32768
        probs.shape = (self._nb_samples, 3)

        return probs

    def _get_curr_variant_probs_layout_2(self):
        """Gets the current variant's probabilities (layout 2)."""
        # The total length C of the rest of the data for this variant
        c = unpack("<I", self._bgen.read(4))[0]

        # The number of bytes to read
        to_read = c

        # D = C if no compression
        d = c
        if self._is_compressed:
            # The total length D of the probability data after
            # decompression
            d = unpack("<I", self._bgen.read(4))[0]
            to_read = c - 4

        # Reading the data and checking
        data = self._decompress(self._bgen.read(to_read))
        if len(data) != d:
            raise ValueError(
                "{}: invalid BGEN file".format(self._bgen.name)
            )

        # Checking the number of samples
        n = unpack("<I", data[:4])[0]
        if n != self._nb_samples:
            raise ValueError(
                "{}: invalid BGEN file".format(self._bgen.name)
            )
        data = data[4:]

        # Checking the number of alleles (we only accept 2 alleles)
        nb_alleles = unpack("<H", data[:2])[0]
        if nb_alleles != 2:
            raise ValueError(
                "{}: only two alleles are "
                "supported".format(self._bgen.name)
            )
        data = data[2:]

        # TODO: Check ploidy for sexual chromosomes
        # The minimum and maximum for ploidy (we only accept ploidy of 2)
        min_ploidy = _byte_to_int(data[0])
        max_ploidy = _byte_to_int(data[1])
        if min_ploidy != 2 and max_ploidy != 2:
            raise ValueError(
                "{}: only accepting ploidy of "
                "2".format(self._bgen.name)
            )
        data = data[2:]

        # Check the list of N bytes for missingness (since we assume only
        # diploid values for each sample)
        ploidy_info = np.frombuffer(data[:n], dtype=np.uint8)
        ploidy_info = np.unpackbits(
            ploidy_info.reshape(1, ploidy_info.shape[0]).T,
            axis=1,
        )
        missing_data = ploidy_info[:, 0] == 1
        data = data[n:]

        # TODO: Permit phased data
        # Is the data phased?
        is_phased = data[0] == 1
        if is_phased:
            raise ValueError(
                "{}: only accepting unphased "
                "data".format(self._bgen.name)
            )
        data = data[1:]

        # The number of bits used to encode each probabilities
        b = _byte_to_int(data[0])
        data = data[1:]

        # Reading the probabilities (don't forget we allow only for diploid
        # values)
        probs = None
        if b == 8:
            probs = np.frombuffer(data, dtype=np.uint8)

        elif b == 16:
            probs = np.frombuffer(data, dtype=np.uint16)

        elif b == 32:
            probs = np.frombuffer(data, dtype=np.uint32)

        else:
            probs = _pack_bits(data, b)

        # Changing shape and computing dosage
        probs.shape = (self._nb_samples, 2)

        return probs / (2**b - 1), missing_data

    def _get_curr_variant_data(self):
        """Gets the current variant's dosage or probabilities."""
        if self._layout == 1:
            # Getting the probabilities
            probs = self._get_curr_variant_probs_layout_1()

            if self._return_probs:
                # Returning the probabilities
                return probs

            else:
                # Returning the dosage
                return self._layout_1_probs_to_dosage(probs)

        else:
            # Getting the probabilities
            probs, missing_data = self._get_curr_variant_probs_layout_2()

            if self._return_probs:
                # Getting the alternative allele homozygous probabilities
                last_probs = self._get_layout_2_last_probs(probs)

                # Stacking the probabilities
                last_probs.shape = (last_probs.shape[0], 1)
                full_probs = np.hstack((probs, last_probs))

                # Setting the missing to NaN
                full_probs[missing_data] = np.nan

                # Returning the probabilities
                return full_probs

            else:
                # Computing the dosage
                dosage = self._layout_2_probs_to_dosage(probs)

                # Setting the missing to NaN
                dosage[missing_data] = np.nan

                # Returning the dosage
                return dosage

    def _layout_1_probs_to_dosage(self, probs):
        """Transforms probability values to dosage (from layout 1)"""
        # Constructing the dosage
        dosage = 2 * probs[:, 2] + probs[:, 1]
        if self.prob_t > 0:
            dosage[~np.any(probs >= self.prob_t, axis=1)] = np.nan

        return dosage

    @staticmethod
    def _get_layout_2_last_probs(probs):
        """Gets the layout 2 last probabilities (homo alternative)."""
        return 1 - np.sum(probs, axis=1)

    def _layout_2_probs_to_dosage(self, probs):
        """Transforms probability values to dosage (from layout 2)."""
        # Computing the last genotype's probabilities
        last_probs = self._get_layout_2_last_probs(probs)

        # Constructing the dosage
        dosage = 2 * last_probs + probs[:, 1]

        # Setting low quality to NaN
        if self.prob_t > 0:
            good_probs = (
                np.any(probs >= self.prob_t, axis=1) |
                (last_probs >= self.prob_t)
            )
            dosage[~good_probs] = np.nan

        return dosage

    def _parse_header(self):
        """Parses the header (header and sample blocks)."""
        # Parsing the header block
        self._parse_header_block()

        # Parsing the sample block (if any)
        if self._has_sample:
            self._parse_sample_block()

    def _parse_header_block(self):
        """Parses the header block."""
        # Getting the data offset (the start point of the data
        self._offset = unpack("<I", self._bgen.read(4))[0]
        self._first_variant_block = self._offset + 4

        # Getting the header size
        self._header_size = unpack("<I", self._bgen.read(4))[0]

        # Getting the number of samples and variants
        self._nb_variants = unpack("<I", self._bgen.read(4))[0]
        self._nb_samples = unpack("<I", self._bgen.read(4))[0]

        # Checking the magic number
        magic = self._bgen.read(4)
        if magic != b"bgen":
            # The magic number might be 0, then
            if unpack("<I", magic)[0] != 0:
                raise ValueError(
                    "{}: invalid BGEN file.".format(self._bgen.name)
                )

        # Passing through the "free data area"
        self._bgen.read(self._header_size - 20)

        # Reading the flag
        flag = np.frombuffer(self._bgen.read(4), dtype=np.uint8)
        flag = np.unpackbits(flag.reshape(1, flag.shape[0]).T, axis=1)

        # Getting the compression type from the layout
        compression = _bits_to_int(flag[0, -2:])
        self._is_compressed = False
        if compression == 0:
            # No decompression required
            self._decompress = self._no_decompress

        elif compression == 1:
            # ZLIB decompression
            self._decompress = zlib.decompress
            self._is_compressed = True

        elif compression == 2:
            if not HAS_ZSTD:
                raise ValueError("zstandard module is not installed")

            # ZSTANDARD decompression (needs to be check)
            self._decompress = zstd.ZstdDecompressor().decompress
            self._is_compressed = True

        # Getting the layout
        layout = _bits_to_int(flag[0, -6:-2])
        if layout == 0:
            raise ValueError(
                "{}: invalid BGEN file".format(self._bgen.name)
            )
        elif layout == 1:
            self._layout = 1
        elif layout == 2:
            self._layout = 2
        else:
            raise ValueError(
                "{}: {} invalid layout type".format(self._bgen.name, layout)
            )

        # Checking if samples are in the file
        self._has_sample = flag[-1, 0] == 1

    def _parse_sample_block(self):
        """Parses the sample block."""
        # Getting the block size
        block_size = unpack("<I", self._bgen.read(4))[0]
        if block_size + self._header_size > self._offset:
            raise ValueError(
                "{}: invalid BGEN file".format(self._bgen.name)
            )

        # Checking the number of samples
        n = unpack("<I", self._bgen.read(4))[0]
        if n != self._nb_samples:
            raise ValueError(
                "{}: invalid BGEN file".format(self._bgen.name)
            )

        # Getting the sample information
        samples = []
        for i in range(self._nb_samples):
            size = unpack("<H", self._bgen.read(2))[0]
            samples.append(self._bgen.read(size).decode())
        self._samples = tuple(samples)

        # Just a check with the header
        if len(self.samples) != self._nb_samples:
            raise ValueError("{}: number of samples different between header "
                             "and sample block".format(self._bgen.name))

    def _connect_index(self):
        """Connect to the index (which is an SQLITE database)."""
        self._bgen_db = sqlite3.connect(self._bgen.name + ".bgi")
        self._bgen_index = self._bgen_db.cursor()

        # Fetching the number of variants and the first and last seek position
        self._bgen_index.execute(
            "SELECT COUNT (rsid), "
            "       MIN (file_start_position), "
            "       MAX (file_start_position) "
            "FROM Variant"
        )
        result = self._bgen_index.fetchone()
        nb_markers = result[0]
        first_variant_block = result[1]
        self._last_variant_block = result[2]

        # Checking the number of markers
        if nb_markers != self._nb_variants:
            raise ValueError(
                "{}: number of markers different between header ({:,d}) "
                "and index file ({:,d})".format(
                    self._bgen.name, self._nb_variants, nb_markers,
                )
            )

        # Checking the first variant seek position
        if first_variant_block != self._first_variant_block:
            raise ValueError("{}: invalid index".format(self._bgen.name))

    @staticmethod
    def _no_decompress(data):
        return data


def _bits_to_int(bits):
    """Converts bits to int."""
    result = 0
    for bit in bits:
        result = (result << 1) | bit
    return result


def _byte_to_int_python3(byte):
    """Converts a byte to a int for python 3."""
    return byte


def _byte_to_int_python2(byte):
    """Converts a byte to a int for python 2."""
    return unpack("<B", byte)[0]


_byte_to_int = _byte_to_int_python3
if PYTHON_VERSION < 3:
    _byte_to_int = _byte_to_int_python2


def _pack_bits(data, b):
    """Unpacks BGEN probabilities (as bits)."""
    # Getting the data from the bytes
    data = np.fromiter(
        ((_byte_to_int(byte) >> i) & 1 for byte in data for i in range(8)),
        dtype=bool,
    )
    data.shape = (data.shape[0] // b, b)

    # Finding the closest full bytes (if required)
    # TODO: Improve this so that it is more efficient
    full_bytes = data[:, ::-1]
    if data.shape[1] % 8 != 0:
        nb_bits = int(ceil(b / 8)) * 8
        full_bytes = np.zeros((data.shape[0], nb_bits), dtype=bool)
        full_bytes[:, -b:] += data[:, ::-1]

    # Packing the bits
    packed = np.packbits(full_bytes, axis=1)

    # Left-shifting for final value
    final = packed[:, 0]
    for i in range(1, packed.shape[1]):
        final = np.left_shift(final, 8, dtype=np.uint) | packed[:, i]

    return final

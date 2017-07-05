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
import bz2

import numpy as np
from pkg_resources import resource_filename

from ..pybgen import _Variant as Variant


__author__ = "Louis-Philippe Lemieux Perreault"
__copyright__ = "Copyright 2014 Louis-Philippe Lemieux Perreault"
__license__ = "MIT"


__all__ = ["example_32bits_truths"]


# Creating the truth value for the 'example.32bits.bgen' file
fn = resource_filename(
    __name__, os.path.join("data", "example.32bits.truths.txt.bz2"),
)
example_32bits_truths = {}
with bz2.BZ2File(fn, "r") as f:
    # Reading the data
    data = tuple(
        row.strip().split("\t") for row in f.read().decode().splitlines()
    )

    # The first row contains the samples
    samples = tuple(data[0])
    example_32bits_truths["samples"] = samples
    example_32bits_truths["nb_samples"] = len(samples)

    # The first column of each row contains the markers
    markers = tuple(row[0] for row in data[1:])
    example_32bits_truths["variant_set"] = set(markers)
    example_32bits_truths["nb_variants"] = len(markers)

    # Now, constructing the variants
    example_32bits_truths["variants"] = {}
    for variant_data in data[1:]:
        name, chrom, pos, a1, a2 = variant_data[:5]
        variant = Variant(name, chrom, int(pos), a1, a2)
        dosage = np.array(variant_data[5:], dtype=float)
        example_32bits_truths["variants"][name] = {
            "variant": variant,
            "dosage": dosage,
        }

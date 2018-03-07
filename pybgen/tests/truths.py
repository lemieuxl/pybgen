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
import itertools

import numpy as np
from pkg_resources import resource_filename

from ..pybgen import _Variant as Variant


__author__ = "Louis-Philippe Lemieux Perreault"
__copyright__ = "Copyright 2014 Louis-Philippe Lemieux Perreault"
__license__ = "MIT"


__all__ = ["truths"]


# The name of the files containing the dosage truths
_DOSAGE_FILENAMES = (
    os.path.join("data", "example.32bits.truths.txt.bz2"),
    os.path.join("data", "example.24bits.truths.txt.bz2"),
    os.path.join("data", "example.16bits.truths.txt.bz2"),
    os.path.join("data", "example.16bits.zstd.truths.txt.bz2"),
    os.path.join("data", "example.9bits.truths.txt.bz2"),
    os.path.join("data", "example.8bits.truths.txt.bz2"),
    os.path.join("data", "example.3bits.truths.txt.bz2"),
    os.path.join("data", "cohort1.truths.txt.bz2"),
)

# The name of the files containing the probabilities truths
_PROBS_FILENAMES = (
    os.path.join("data", "example.32bits.probs.truths.txt.bz2"),
    os.path.join("data", "example.24bits.probs.truths.txt.bz2"),
    os.path.join("data", "example.16bits.probs.truths.txt.bz2"),
    os.path.join("data", "example.16bits.zstd.probs.truths.txt.bz2"),
    os.path.join("data", "example.9bits.probs.truths.txt.bz2"),
    os.path.join("data", "example.8bits.probs.truths.txt.bz2"),
    os.path.join("data", "example.3bits.probs.truths.txt.bz2"),
    os.path.join("data", "cohort1.probs.truths.txt.bz2"),
)


def _generate_truths():
    """Generate the truths."""
    final_dosage_truths = {}
    final_probs_truths = {}

    #  Generating the truths for the dosage files
    for filename in itertools.chain(_DOSAGE_FILENAMES, _PROBS_FILENAMES):
        is_probs = filename.endswith("probs.truths.txt.bz2")

        fn = resource_filename(__name__, filename)
        file_truths = {}
        with bz2.BZ2File(fn, "r") as f:
            # Reading the data
            data = tuple(
                row.strip().split("\t")
                for row in f.read().decode().splitlines()
            )

            # The first row contains the samples
            samples = tuple(data[0])
            nb_samples = len(samples)
            if samples[0] == "None":
                samples = None
                nb_samples = int(data[0][1])
            file_truths["samples"] = samples
            file_truths["nb_samples"] = nb_samples

            # The first column of each row contains the markers
            markers = tuple(row[0] for row in data[1:])
            file_truths["variant_set"] = set(markers)
            file_truths["nb_variants"] = len(markers)

            # Now, constructing the variants
            file_truths["variants"] = {}
            for variant_data in data[1:]:
                name, chrom, pos, a1, a2 = variant_data[:5]
                variant = Variant(name, chrom, int(pos), a1, a2)
                values = np.array(variant_data[5:], dtype=float)
                if is_probs:
                    values.shape = (nb_samples, 3)
                file_truths["variants"][name] = {
                    "variant": variant,
                    "data": values,
                }

        # Saving the file truths
        if is_probs:
            final_probs_truths[os.path.basename(fn)] = file_truths
        else:
            final_dosage_truths[os.path.basename(fn)] = file_truths

    return {"dosage": final_dosage_truths, "probs": final_probs_truths}


# All the truths
truths = _generate_truths()

"""Module that reads BGEN files in parallel."""

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

import logging
import multiprocessing

from six.moves import range

from .pybgen import PyBGEN


__author__ = "Louis-Philippe Lemieux Perreault"
__copyright__ = "Copyright 2017 Louis-Philippe Lemieux Perreault"
__license__ = "MIT"


__all__ = ["ParallelPyBGEN"]


# The logger
logger = logging.getLogger(__name__)


def _pybgen_reader(fn, prob_t, probs_only, seeks, queue):
    """Reads specific markers according to a seek queue."""
    with PyBGEN(fn, mode="r", prob_t=prob_t, probs_only=probs_only,
                _skip_index=True) as bgen:
        for r in bgen._iter_seeks(seeks):
            queue.put(r)
    queue.put(None)


class ParallelPyBGEN(PyBGEN):
    """Reads BGEN files in parallel.

    Args:
        fn (str): The name of the BGEN file.
        prob_t (float): The probability threshold (optional).
        cpus (int): The number of CPUs (default is 2).
        probs_only (boolean): Return only the probabilities instead of dosage.
        max_variants (int): The maximal number of variants in the Queue

    Reads a BGEN file using multiple processes.

    .. code-block:: python

        from pybgen import ParrallelPyBGEN as PyBGEN

        # Reading a BGEN file
        with PyBGEN("bgen_file_name") as bgen:
            pass

    """

    def __init__(self, fn, prob_t=0.9, cpus=2, probs_only=False,
                 max_variants=1000):
        """Initializes a new PyBGEN instance."""
        # Calling the parent's constructor
        super(ParallelPyBGEN, self).__init__(
            fn, mode="r", prob_t=prob_t, probs_only=probs_only,
        )

        # Initializing the queue and process
        self.cpus = cpus
        self._max_variants = max_variants
        self._seeks = None

    def iter_variants(self):
        """Iterates over all variants using multiple process."""
        # Getting tall the variants seek position
        if self._seeks is None:
            self._get_all_seeks()
        seeks = [self._seeks[i::self.cpus] for i in range(self.cpus)]

        return self._parallel_iter_seeks(seeks)

    def iter_variants_by_names(self, names):
        """Iterates over variants using a list of names.

        Args:
            names (list): A list of names to extract specific variants.

        """
        seeks = self._get_seeks_for_names(names)
        seeks = [seeks[i::self.cpus] for i in range(self.cpus)]

        return self._parallel_iter_seeks(seeks)

    def _get_all_seeks(self):
        """Gets the list of seeks."""
        self._bgen_index.execute("SELECT file_start_position FROM Variant")
        seeks = [_[0] for _ in self._bgen_index.fetchall()]
        seeks.sort()
        self._seeks = tuple(seeks)

    def _get_seeks_for_names(self, names):
        """Gets the seek values for each names."""
        # Generating a temporary table that will contain the markers to extract
        self._bgen_index.execute("CREATE TEMPORARY TABLE tnames (name text)")
        self._bgen_index.executemany(
            "INSERT INTO tnames VALUES (?)",
            [(n, ) for n in names],
        )

        # Fetching the seek positions
        self._bgen_index.execute(
            "SELECT file_start_position "
            "FROM Variant "
            "WHERE rsid IN (SELECT name FROM tnames)",
        )
        return tuple(_[0] for _ in self._bgen_index.fetchall())

    def _spawn_workers(self, seeks, queue):
        """Spawn some workers."""
        self._workers = []
        for i in range(self.cpus):
            worker = multiprocessing.Process(
                target=_pybgen_reader,
                args=(self._bgen.name, self.prob_t, self._return_probs,
                      seeks[i], queue),
            )
            self._workers.append(worker)
            worker.start()

    def _parallel_iter_seeks(self, seeks):
        """Iterates over variants using multiple process."""
        # Spanning processes
        queue = multiprocessing.Queue(self._max_variants)
        self._spawn_workers(seeks, queue)

        # Launching the analysis
        try:
            nb_finish = 0
            while True:
                if nb_finish >= self.cpus:
                    break

                result = queue.get()
                if result is None:
                    nb_finish += 1
                    continue
                yield result

        finally:
            # Terminating the worker, whatever happened
            for worker in self._workers:
                worker.terminate()

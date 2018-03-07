
pybgen's API
=============


Main PyBGEN class
------------------

.. autoclass:: pybgen.PyBGEN
   :members:


.. automodule:: pybgen
   :members:


Parallel PyBGEN class
----------------------

We provide a wrapper class called :py:class:`ParallelPyBGEN` which implements
two functions to iterate over variants in parallel. This is useful for huge
datasets such as the UK Biobank imputation files.

.. autoclass:: pybgen.ParallelPyBGEN
   :members:


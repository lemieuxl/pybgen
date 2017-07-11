.. pybgen documentation master file, created by
   sphinx-quickstart on Fri Mar 10 09:00:31 2017.

pybgen
=======

:py:mod:`pybgen` is a Python (2 and 3) BGEN file parser and writer (not quite
yet) released under the MIT licence.

For more information on how to use :py:mod:`pybgen`, refer to the
:doc:`API documentation <pybgen>`. Below is a snippet describing the most
common usage of the module.


.. code-block:: python


    from pybgen import PyBGEN

    with PyBGEN("simple/data/example.32bits.bgen") as bgen:
        # Iterating over all variants
        for info, dosage in bgen:
            pass

        # Getting the genotypes of as single variant
        for info, dosage in bgen.get_variant("RSID_192"):
            print(info)
            print(dosage)


.. toctree::
   :hidden:

   installation
   pybgen

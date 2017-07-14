from distutils.core import setup, Extension

import numpy as np

module1 = Extension('c_test',
                    sources = ['test.c'])

include = np.get_include()

setup(
    name = 'c_ext_test',
    version = '1.0',
    description = 'This is a demo package',
    ext_modules = [module1],
    include_dirs=[include],
)

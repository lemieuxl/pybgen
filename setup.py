#!/usr/bin/env python

# How to build source distribution
#   - python setup.py sdist --format bztar
#   - python setup.py sdist --format gztar
#   - python setup.py sdist --format zip
#   - python setup.py bdist_wheel --universal

# How to build for conda
#   - cd conda_recipe
#   - conda clean -ytps; conda build purge; conda build --python $VERSION .
#   - cp $FILE ../conda_dist/linux-64
#   - conda convert -p all ../conda_dist/linux-64/$FILE -o ../conda_dist
#   - cd ../conda_dist && conda index *


import os
from setuptools import setup


MAJOR = 0
MINOR = 5
MICRO = 0
VERSION = "{}.{}.{}".format(MAJOR, MINOR, MICRO)


def write_version_file(fn=None):
    if fn is None:
        fn = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            os.path.join("pybgen", "version.py"),
        )

    content = (
        "\n# THIS FILE WAS GENERATED AUTOMATICALLY BY PYBGEN SETUP.PY\n"
        'pybgen_version = "{version}"\n'
    )

    a = open(fn, "w")
    try:
        a.write(content.format(version=VERSION))
    finally:
        a.close()


def get_requirements():
    # Initial requirements
    requirements = ["numpy >= 1.12.0", "six >= 1.10.0", "setuptools >= 27.0"]

    return requirements


def setup_package():
    # Saving the version into a file
    write_version_file()

    setup(
        zip_safe=False,
        name="pybgen",
        version=VERSION,
        description="Python module to read BGEN files.",
        author="Louis-Philippe Lemieux Perreault",
        author_email="louis-philippe.lemieux.perreault@statgen.org",
        url="https://github.com/lemieuxl/pybgen",
        license="MIT",
        packages=["pybgen", "pybgen.tests"],
        package_data={"pybgen.tests": ["data/*"], },
        test_suite="pybgen.tests.test_suite",
        install_requires=get_requirements(),
        classifiers=["Operating System :: POSIX :: Linux",
                     "Operating System :: MacOS :: MacOS X",
                     "Operating System :: Microsoft",
                     "Programming Language :: Python",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.4",
                     "Programming Language :: Python :: 3.5",
                     "Programming Language :: Python :: 3.6",
                     "License :: OSI Approved :: MIT License",
                     "Topic :: Scientific/Engineering :: Bio-Informatics"],
        keywords="bioinformatics format BGEN binary",
    )

    return


if __name__ == "__main__":
    setup_package()

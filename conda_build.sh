#!/bin/bash -x

# Getting pybgen's version to build
pybgen_version=$1
if [ -z $pybgen_version ]; then
    (>&2 echo "usage: $0 VERSION PYTHON_VERSION")
    exit 1
fi

# Creating a directory for the build module (with noarch)
mkdir -p conda_dist/noarch

# Creating a directory for the skeleton
mkdir -p skeleton
pushd skeleton

# Creating the skeleton
conda skeleton pypi pybgen --version $pybgen_version

# Checking that fetching pybgen was successful
if [ $? -ne 0 ]; then
    (>&2 echo "Error when creating skeleton for pybgen version $pybgen_version")
    exit 1
fi

# The different python versions build
python_versions="2.7 3.4 3.5 3.6"

# The different build platforms
platforms="all"

# Building
for python_build_version in $python_versions; do
    # Building
    conda build --python $python_build_version pybgen &> log.txt

    # Checking the build was completed
    if [ $? -ne 0 ]; then
        cat log.txt
        (>&2 echo "Error when building pybgen $pybgen_version (python $python_build_version)")
        exit 1
    fi

    # Fetching the file name of the build
    filename=$(grep -oP "anaconda upload \K(\S+)$" log.txt)

    # Checking the file exists
    if [ -z $filename ]||[ ! -e $filename ]; then
        echo "Problem fetching file $filename" 1>&2
        exit 1
    fi

    # Converting to the different platforms
    for platform in $platforms; do
        conda convert -p $platform $filename -o ../conda_dist &> build_log.txt

        # Checking the conversion was completed
        if [ $? -ne 0 ]; then
            (>&2 echo "Problem converting pybgen $pybgen_version (python $python_build_version) to $platform")
            exit 1
        fi

        # Checking if a conversion was skipped due to same platform
        if egrep --quiet Skipping build_log.txt; then
            # Finding which platform was skipped
            missing=$(
                egrep Skipping build_log.txt |
                egrep -o "'([[:alnum:]]+-[[:digit:]]+)'" |
                uniq |
                sed -e "s/'//g"
            )
            mkdir -p ../conda_dist/$missing
            cp $filename ../conda_dist/$missing
        fi

    done

    # Purging
    conda build purge

done

popd
rm -rf skeleton

# Indexing
pushd conda_dist
conda index *
popd

# Permissions
find conda_dist -type d -print0 | xargs -0 chmod 755
find conda_dist -type f -print0 | xargs -0 chmod 644

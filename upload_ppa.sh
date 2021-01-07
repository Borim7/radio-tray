#!/bin/bash

set -e

# ppa require ubuntu distribution series in first line of changelog
UBUNTU_SERIES=focal
# only if same release need to be updated again
PPA_VERSION=

SRC_ARCHIVE_PATH=dist/*.tar.bz2
SRC_ARCHIVE=`basename $SRC_ARCHIVE_PATH`
#PACKAGE_NAME=radiotray-0.8.0
PACKAGE_NAME="${SRC_ARCHIVE%.tar.bz2}"

rm -rf ppa/*
mkdir -p ppa/$PACKAGE_NAME/debian
tar -xmf $SRC_ARCHIVE_PATH -C ppa/

for FILE in $(git ls-files debian)
do
	cp $FILE ppa/$PACKAGE_NAME/debian
done

# update changelog for ppa
# replace debian series with ubuntu series
sed -i "1s/unstable;/$UBUNTU_SERIES;/" ppa/$PACKAGE_NAME/debian/changelog
# update version
sed -i "1s/)/-ppa$PPA_VERSION~$UBUNTU_SERIES)/" ppa/$PACKAGE_NAME/debian/changelog

# create source package
cd ppa/$PACKAGE_NAME
debuild -S

# upload source package
cd ..
dput ppa:borim/radiotray radiotray*_source.changes


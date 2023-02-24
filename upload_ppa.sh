#!/bin/bash

set -e

# ppa require ubuntu distribution series in first line of changelog
UBUNTU_SERIES="focal jammy kinetic"
# only if same release need to be updated again
PPA_VERSION=

SRC_ARCHIVE_PATH=dist/*.tar.bz2
SRC_ARCHIVE=`basename $SRC_ARCHIVE_PATH`
PACKAGE_NAME="${SRC_ARCHIVE%.tar.bz2}"

rm -rf ppa/*

for SERIES in $UBUNTU_SERIES
do
	BASE_DIR=ppa/$SERIES
	PACKAGE_DIR=$BASE_DIR/$PACKAGE_NAME

	mkdir -p $PACKAGE_DIR/debian
	tar -xmf $SRC_ARCHIVE_PATH -C ppa/$SERIES/

	for FILE in $(git ls-files debian)
	do
		cp $FILE $PACKAGE_DIR/debian
	done

	# update changelog for ppa
	# replace debian series with ubuntu series
	sed -i "1s/unstable;/$SERIES;/" $PACKAGE_DIR/debian/changelog
	# update version
	sed -i "1s/)/-ppa$PPA_VERSION~$SERIES)/" $PACKAGE_DIR/debian/changelog

	# create source package
	(cd $PACKAGE_DIR && debuild -S)

	# upload source package
	dput ppa:borim/radiotray $BASE_DIR/radiotray*_source.changes
done


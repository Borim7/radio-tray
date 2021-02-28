#!/bin/bash

set -e

if [ "$1" = "--sign" ]; then
SIGN_OPTION=
else
SIGN_OPTION="-ui -uc"
fi

rm -rf dist/*
python3 setup.py sdist
python3 setup.py bdist

dpkg-buildpackage -b -rfakeroot $SIGN_OPTION

mv ../radiotray_0.8.1_{all.deb,*.changes,*.buildinfo} dist


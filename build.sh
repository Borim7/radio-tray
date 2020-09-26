#!/bin/bash

rm -rf dist/*
python3 setup.py sdist
python3 setup.py bdist

dpkg-buildpackage -b -rfakeroot

mv ../radiotray_0.8.0_{all.deb,*.changes,*.buildinfo} dist


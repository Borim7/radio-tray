# RadioTray

This is a simple music streaming player that lives on the system tray. By clicking on the RadioTray icon,
you'll be presented with a list of pre-configured online radios. By selecting one of those radios, it
will start playing.

Right now, Radio Tray bundles with pre-configured radios. But you can and should add more manually.

Adding online radios to the list is very simple. By right-clicking the RadioTray icon and selecting
"Config radios...", you may add the name and URL of an online radio.
This version allows you to add direct URLs (to media streams or files) and URLs pointing at playlist formats (pls, m3u, asx, wax, wvx).



RadioTray was written in Python and uses gtk and gstreamer libraries (you'll need these to run RadioTray).

## Requirements
- python3
- python3-gst-1.0
- python3-gi
- python3-lxml
- python3-dbus
- python3-xdg
- gir1.2-appindicator3-0.1

## Build requirements
- python3-setuptools
- python3-distutils-extra
- dh-python
- debhelper

## Installation
To install, you can run `python setup.py install`. Note: there is no uninstall script.

Alternative you can build a debian package by running `build.sh`, the package will be generated under dist.
For signed debian package use `build.sh --sign`

For prebuild packages you can use following PPA:
- https://launchpad.net/~borim/+archive/ubuntu/radiotray

It can be added to your package respositories with the command:
```
sudo add-apt-repository ppa:borim/radiotray
```

You need to install RadioTray. To run RadioTray, you should execute `bin/radiotray` or `python3 -m radiotray` from the extracted tarball.


# Authors & Acknowlegements

RadioTray was written by Carlos Ribeiro <carlosmribeiro1@gmail.com>. RadioTray is Copyright (c) 2009,
2010 by Carlos Ribeiro <carlosmribeiro1@gmail.com>; it is distributed under the GNU General Public
License, see COPYING for details.

Radio Tray icon is a GPL icon made by WooThemes
http://www.woothemes.com/2009/02/wp-woothemes-ultimate-icon-set-first-release/

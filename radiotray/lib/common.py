# -*- coding: utf-8 -*-

import os

from xdg.BaseDirectory import xdg_data_home
# provide translation functions for complete code base
from . import i18n # pylint: disable=unused-import

try:
    from defs import * # pylint: disable=wildcard-import
except ImportError:
    APPVERSION = "0.8.3"
    if os.uname()[0] == 'OpenBSD':
        datadir = "/usr/local/share"
    else:
        datadir = "/usr/share"

# Application info
APPNAME = "Radio Tray"
APPDIRNAME = APPNAME.lower().replace(" ","")

COPYRIGHT_YEAR = '2009 - 2011'
COPYRIGHTS = "%s - Copyright (c) %s\n" \
             "Carlos Ribeiro <carlosmribeiro1@gmail.com>" % (APPNAME, COPYRIGHT_YEAR)
WEBSITE = "https://github.com/Borim7/radio-tray"
AUTHORS = [
    _('Developers:'),
    "Carlos Ribeiro <carlosmribeiro1@gmail.com>",
    _('Contributors:'),
    'Og Maciel <ogmaciel@gnome.com>',
    'Ed Bruck <ed.bruck1@gmail.com>',
    'Behrooz Shabani <behrooz@rock.com>',
    'Valdur Kana <valdur55@gmail.com>',
]

ARTISTS = []
LICENSE = """Radio Tray
Copyright (C) %s - Carlos Ribeiro <carlosmribeiro1@gmail.com>.

Radio Tray is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Radio Tray is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
""" % COPYRIGHT_YEAR

# Media path
if os.path.exists(os.path.abspath('../data/images/')):
    IMAGE_PATH = os.path.abspath('../data/images/')
else:
    IMAGE_PATH = '%s/%s/images' % (datadir, APPDIRNAME)

# Images
APP_ICON = os.path.join(IMAGE_PATH, 'radiotray.png')
APP_ICON_ON = os.path.join(IMAGE_PATH, 'radiotray_on.png')
APP_ICON_OFF = os.path.join(IMAGE_PATH, 'radiotray_off.png')
APP_ICON_CONNECT = os.path.join(IMAGE_PATH, 'radiotray_connecting.gif')
APP_INDICATOR_ICON_ON = "radiotray_on"
APP_INDICATOR_ICON_OFF = "radiotray_off"
APP_INDICATOR_ICON_CONNECT = "radiotray_connecting"
# Config info
CFG_NAME = 'bookmarks.xml'
OPTIONS_CFG_NAME = 'config.xml'
USER_CFG_PATH =  os.path.join(xdg_data_home, APPDIRNAME)
OLD_USER_CFG_PATH = os.environ['HOME'] + "/.radiotray/"

REL_CFG_DIR = os.path.abspath('../data/')
if os.path.exists(os.path.join(REL_CFG_DIR, CFG_NAME)):
    DEFAULT_CFG_PATH = REL_CFG_DIR
else:
    DEFAULT_CFG_PATH = '%s/%s/' % (datadir, APPDIRNAME)

DEFAULT_RADIO_LIST = os.path.join(DEFAULT_CFG_PATH, CFG_NAME)
DEFAULT_CONFIG_FILE = os.path.join(DEFAULT_CFG_PATH, OPTIONS_CFG_NAME)

# Plugins
SYSTEM_PLUGIN_PATH = os.path.join(DEFAULT_CFG_PATH, 'plugins')
USER_PLUGIN_PATH = os.path.join(USER_CFG_PATH, 'plugins')

#Logfile
LOGFILE = os.path.join(USER_CFG_PATH,'radiotray.log')

#temporary icon file
ICON_FILE = os.path.join(USER_CFG_PATH,'icon')

# user-agent
USER_AGENT = "RadioTray/" + APPVERSION


def getDefaultHttpHeader():
    return {"User-Agent": USER_AGENT}

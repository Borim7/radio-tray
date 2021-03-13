##########################################################################
# Copyright 2009 Carlos Ribeiro
#
# This file is part of Radio Tray
#
# Radio Tray is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 1 of the License, or
# (at your option) any later version.
#
# Radio Tray is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Radio Tray.  If not, see <http://www.gnu.org/licenses/>.
#
##########################################################################
from os.path import exists, join
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from . import common


def load_ui_file(name):
    ui = Gtk.Builder()
    ui.add_from_file(join(common.DEFAULT_CFG_PATH, name))
    return ui

paths = ("/usr/local/share/radiotray","/usr/share/radiotray")

def tryopen(filename):
    """Returns a reading file handle for filename,
    searching through directories in a built-in list.
    """
    try:
        f = open(filename)
        return f
    except IOError:
        for p in paths:
            try:
                f = open(join(p,filename))
                return f
            except IOError:
                pass
    raise IOError("Unable to find file "+filename)

def findfile(filename):
    """Looks for filename, searching a built-in list of directories;
    returns the path where it finds the file.
    """
    if exists(filename):
        return filename
    for p in paths:
        x = join(p,filename)
        print(x)
        if exists(x):
            return x

    return None

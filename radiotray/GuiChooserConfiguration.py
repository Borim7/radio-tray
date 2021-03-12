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
import sys
import logging

try:
    import gi
    gi.require_version("Gtk", "3.0")
except:
    pass
try:
    from gi.repository import Gtk
    #import Gtk.glade
except Exception as e:
    print(e)
    sys.exit(1)

from .lib import utils


class GuiChooserConfiguration:

    def __init__(self):
        gladefile = utils.load_ui_file("configGui.glade")
        self.wTree = gladefile
        self.dialog = self.wTree.get_object("guiChooserDialog")
        self.rb_systray = self.wTree.get_object("rb_systray")
        self.rb_appindicator = self.wTree.get_object("rb_appindicator")
        self.log = logging.getLogger('radiotray')

    def run(self):
        result = self.dialog.run()
        self.dialog.hide()

        #user clicks cancel
        if result == 0:
            sys.exit(0)

        if self.rb_systray.get_active():
            self.log.info('user chose notification area')
            return "systray"
        else:
            self.log.info('user chose app indicator')
            return "appindicator"

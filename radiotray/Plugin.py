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

import threading
import logging
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

# This class should be extended by plugins implementations
class Plugin(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.log = logging.getLogger('radiotray')

        self.eventManagerWrapper = None
        self.eventSubscriber = None
        self.provider = None
        self.cfgProvider = None
        self.mediator = None
        self.tooltip = None
        self.menuItem = None

    def initialize(self, name, eventManagerWrapper, eventSubscriber, provider, cfgProvider,
        mediator, tooltip):

        self.name = name
        self.eventManagerWrapper = eventManagerWrapper
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip
        self.menuItem = Gtk.MenuItem(self.getName())
        self.menuItem.connect('activate', self.on_menu)
        self.menuItem.show()


    def getName(self):
        return self.name


    def activate(self):
        raise NotImplementedError( "Subclasses should override this" )

    def finalize(self):
        print("Finalizing " + self.name)
        self.join()

    def setMenuItem(self, item):
        self.menuItem = item

    def getMenuItem(self):
        return self.menuItem

    def hasMenuItem(self):
        return False

    def on_menu(self, _data):
        """Called when clicked on plugin entry in menu.
        Default is to do nothing, reimplement if needed."""

    def run(self):
        self.activate()

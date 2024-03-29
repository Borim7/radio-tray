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
import logging
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk
    from gi.repository import GObject
    GObject.threads_init()
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from .lib import utils
from .lib.common import APP_ICON_ON


class PluginConfiguration:

    def __init__(self, pluginManager, cfgProvider):

        self.pluginManager = pluginManager
        self.cfgProvider = cfgProvider
        self.log = logging.getLogger('radiotray')

        # load glade and get gui objects
        gladefile = utils.load_ui_file("configPlugins.glade")
        self.wTree = gladefile
        self.window = self.wTree.get_object("dialog1")
        self.list = self.wTree.get_object("treeview1")

        # set icon
        self.window.set_icon_from_file(APP_ICON_ON)

        # load plugin data
        liststore = self.load_data()
        self.list.set_model(liststore)


        # config plugins view
        cell1 = Gtk.CellRendererToggle()
        cell1.set_property('activatable', True)
        cell1.set_activatable(True)
        cell1.set_property('mode', Gtk.CellRendererMode.ACTIVATABLE)
        cell1.connect( 'toggled', self.on_toggle, liststore )
        tvcolumn1 = Gtk.TreeViewColumn(_('Active'), cell1)

        tvcolumn1.add_attribute( cell1, "active", 0)

        cell2 = Gtk.CellRendererText()
        tvcolumn2 = Gtk.TreeViewColumn(_('Name'), cell2, text=1)

        self.list.append_column(tvcolumn1)
        self.list.append_column(tvcolumn2)

        # connect signals from gladefile
        if self.window:
            self.wTree.connect_signals(self)


        self.window.show()


    def load_data(self):

        self.activePlugins = self.cfgProvider.getConfigList('active_plugins')
#        if plugins == None:
#            self.cfgProvider.setConfigValue('active_plugins'


        liststore = Gtk.ListStore(GObject.TYPE_BOOLEAN, GObject.TYPE_STRING)
        plugins = self.pluginManager.getPlugins()

        for p in plugins:
            if p.name in self.activePlugins:
                liststore.append([True, p.name])
            else:
                liststore.append([False, p.name])

        return liststore



    def on_toggle(self, _cell, path, model):

        model[path][0] = not model[path][0]
        name = model[path][1]

        self.log.debug('Setting %s to %s', model[path][1], str(model[path][0]))
        self.log.debug(self.activePlugins)
        if model[path][0]:
            self.log.debug('apppend %s', name)
            self.activePlugins.append(name)
            self.pluginManager.activatePlugin(name)
        else:
            self.log.debug('remove %s', name)
            self.activePlugins.remove(name)
            self.pluginManager.deactivatePlugin(name)


        self.log.debug(self.activePlugins)


    def on_close_clicked(self, _widget):

        self.cfgProvider.setConfigList('active_plugins', self.activePlugins)
        self.window.destroy()

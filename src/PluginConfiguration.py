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

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
    import gobject
    import os
    from lib import utils
except:
    sys.exit(1)

class PluginConfiguration(object):

    def __init__(self, pluginManager, cfgProvider):
        
        self.pluginManager = pluginManager
        self.cfgProvider = cfgProvider

        # load glade and get gui objects
        gladefile = utils.load_ui_file("configPlugins.glade")
        self.wTree = gladefile
        self.window = self.wTree.get_object("dialog1")
        self.list = self.wTree.get_object("treeview1")

        # load plugin data
        liststore = self.load_data()
        self.list.set_model(liststore)


        # config plugins view
        cell1 = gtk.CellRendererToggle()
        cell1.set_property('activatable', True)
        cell1.set_activatable(True)
        cell1.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)
        cell1.connect( 'toggled', self.on_toggle, liststore )
        tvcolumn1 = gtk.TreeViewColumn(_('Active'), cell1)

        tvcolumn1.add_attribute( cell1, "active", 0)

        cell2 = gtk.CellRendererText()
        tvcolumn2 = gtk.TreeViewColumn(_('Name'), cell2, text=1)

        self.list.append_column(tvcolumn1)
        self.list.append_column(tvcolumn2)

        if (self.window):
            dic = { "on_close_clicked" : self.on_close_clicked}
            self.wTree.connect_signals(self)


        self.window.run()


    def load_data(self):
        
        self.activePlugins = self.cfgProvider.getConfigList('active_plugins')
#        if plugins == None:
#            self.cfgProvider.setConfigValue('active_plugins'


        liststore = gtk.ListStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)
        plugins = self.pluginManager.getPlugins()
  
        for p in plugins:
            if p.name in self.activePlugins:
                liststore.append([True, p.name])
            else:
                liststore.append([False, p.name])

        return liststore



    def on_toggle(self, cell, path, model):
        
        model[path][0] = not model[path][0]
        name = model[path][1]

        print 'Setting ' + model[path][1] + ' to ' + str(model[path][0])
        print self.activePlugins
        if(model[path][0] == True):
            print "apppend " + name
            self.activePlugins.append(name)
            self.pluginManager.activatePlugin(name)
        else:
            print "remove " + name
            self.activePlugins.remove(name)
            self.pluginManager.deactivatePlugin(name)

        
        print self.activePlugins


    def on_close_clicked(self, widget):

        self.cfgProvider.setConfigList('active_plugins', self.activePlugins)
        self.window.destroy()


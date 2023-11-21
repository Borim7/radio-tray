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
import os

from radiotray.events.EventManager import EventManager
from radiotray.Plugin import Plugin
from radiotray.lib import utils
from radiotray.lib.common import SYSTEM_PLUGIN_PATH, USER_PLUGIN_PATH


class HistoryPlugin(Plugin):

    def __init__(self):
        super().__init__()

        self.gladefile = None
        self.text = None
        self.window = None
        self.last_title = 'none'


    def getName(self):
        return self.name


    def activate_gtk(self, data):
        if os.path.exists(os.path.join(USER_PLUGIN_PATH, "history.glade")):
            self.gladefile = utils.load_ui_file(os.path.join(USER_PLUGIN_PATH, "history.glade"))
        elif os.path.exists(os.path.join(SYSTEM_PLUGIN_PATH, "history.glade")):
            self.gladefile = utils.load_ui_file(os.path.join(SYSTEM_PLUGIN_PATH, "history.glade"))
        else:
            self.log.error('Error initializing History plugin: history.glade not found')

        self.text = self.gladefile.get_object('textview1')
        self.window = self.gladefile.get_object("dialog1")
        self.last_title = 'none'

        if self.window:
            #dic = { "on_close_clicked" : self.on_close_clicked}
            self.gladefile.connect_signals(self)


    def activate(self):
        self.eventSubscriber.bind(EventManager.SONG_CHANGED, self.on_song_changed)
        GLib.idle_add(self.activate_gtk, None)


    def on_song_changed(self, data):

        if 'title' in list(data.keys()):
            title = data['title']
            if title != self.last_title:
                self.last_title = title
                # avoid crash, if fault during activation happend
                if self.text is not None:
                    buffer = self.text.get_buffer()
                    buffer.insert(buffer.get_end_iter(),title+'\n')


    def on_menu(self, data):
        self.window.show()

    def on_close_clicked(self, widget):
        self.window.hide()
        return True

    def on_delete_event(self, widget, event, data=None):
        self.window.hide()
        return True

    def hasMenuItem(self):
        return True

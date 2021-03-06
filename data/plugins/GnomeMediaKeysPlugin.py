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

import dbus
from radiotray.Plugin import Plugin

class GnomeMediaKeysPlugin(Plugin):

    def __init__(self):
        super(GnomeMediaKeysPlugin, self).__init__()

        self.bus = None
        self.bus_object = None


    def initialize(self, name, eventManagerWrapper, eventSubscriber, provider, cfgProvider,
        mediator, tooltip):

        self.name = name
        self.eventManagerWrapper = eventManagerWrapper
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip


    def getName(self):
        return self.name


    def activate(self):
        try:
            self.bus = dbus.SessionBus()
            self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon',
                '/org/gnome/SettingsDaemon/MediaKeys')
            self.bus_object.GrabMediaPlayerKeys("RadioTray", 0,
                dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
            self.bus_object.connect_to_signal('MediaPlayerKeyPressed', self.handle_mediakey)
        except dbus.DBusException:
            print("Could not bind to Gnome for Media Keys")


    def handle_mediakey(self, *mmkeys):
        for key in mmkeys:
            if key == "Play":
                if self.mediator.isPlaying():
                    self.mediator.stop()
                else:
                    self.mediator.playLast()
            elif key == "Stop":
                if self.mediator.isPlaying():
                    self.mediator.stop()

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
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Notify", "0.7")

    from gi.repository import Notify
    from gi.repository import GdkPixbuf
except (ImportError, ValueError) as e:
    print(__file__ + ": " + str(e))
    sys.exit(1)

from radiotray.Plugin import Plugin
from radiotray.lib.common import APP_ICON, APPNAME
from radiotray.events.EventManager import EventManager

class NotificationPlugin(Plugin):

    def __init__(self):
        super().__init__()

        self.notif = None
        self.lastMessage = None
        self.eventManagerWrapper = None

    def getName(self):
        return self.name

    def initialize(self, name, eventManagerWrapper, eventSubscriber, provider, cfgProvider,
        mediator, tooltip):

        self.name = name
        self.eventManagerWrapper = eventManagerWrapper
        self.eventSubscriber = eventSubscriber
        self.provider = provider
        self.cfgProvider = cfgProvider
        self.mediator = mediator
        self.tooltip = tooltip


    def activate(self):
        self.notif = None
        self.lastMessage = None
        self.eventSubscriber.bind(EventManager.NOTIFICATION, self.on_notification)


    def on_notification(self, data):

        message = data['message']
        title = data['title']
        if self.lastMessage != message:

            self.lastMessage = message

            if self.notif is None:

                if Notify.init(APPNAME):
                    try:
                        self.notif = Notify.Notification.new(title, message, None)
                        self.notif.set_urgency(Notify.Urgency.LOW)
                        self.set_icon(data)
                        self.notif.set_timeout(Notify.EXPIRES_DEFAULT)
                        self.notif.show()
                    except gi.repository.GLib.GError:
                        # probably dbus is not responding, e.g. during shutdown, ignore error
                        self.log.error(
                            'Error: notification can not be displayed, after initialization')

                else:
                    self.log.error('Error: there was a problem initializing the pynotify module')

            else:
                try:
                    self.set_icon(data)
                    self.notif.update(title, message, None)
                    self.notif.show()
                except gi.repository.GLib.GError:
                    # probably dbus is not responding, e.g. during shutdown, ignore error
                    self.log.error('Error: notification can not be displayed')


    def set_icon(self, data):
        #some radios publish cover data in the 'homepage' tag
        if 'icon' in list(data.keys()):

            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(data['icon'], 48, 48)
                self.notif.set_icon_from_pixbuf(pixbuf)
            except gi.repository.GLib.GError as e:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(APP_ICON, 48, 48)
                self.notif.set_icon_from_pixbuf(pixbuf)
                print(e)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(APP_ICON, 48, 48)
            self.notif.set_icon_from_pixbuf(pixbuf)
